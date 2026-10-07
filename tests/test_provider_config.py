"""Provider settings come from COS_* configuration, including the local .env file."""

import json

import pytest

from creative_os.config import get_settings
from creative_os.providers.reasoning import (
    GrokReasoningProvider,
    OpenAIReasoningProvider,
    ProviderUnavailable,
    configured_reasoning_providers,
)

pytestmark = pytest.mark.core

_SECRET = "dotenv-secret-should-not-leak"
_PROCESS_SECRET = "process-secret-should-not-leak"


def _clear_provider_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "COS_XAI_API_KEY",
        "COS_XAI_MODEL",
        "COS_OPENAI_API_KEY",
        "COS_OPENAI_MODEL",
        "COS_LIVE_TEXT_REASONING_ENABLED",
        "XAI_API_KEY",
        "OPENAI_API_KEY",
    ):
        monkeypatch.delenv(name, raising=False)


def test_dotenv_values_configure_the_provider(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_provider_env(monkeypatch)
    (tmp_path / ".env").write_text(
        "COS_XAI_API_KEY=dotenv-secret-should-not-leak\nCOS_XAI_MODEL=dotenv-model\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    settings = get_settings()
    provider = GrokReasoningProvider()
    assert settings.xai_model == "dotenv-model"
    assert provider.explicit_model() == "dotenv-model"
    assert provider.available() is True
    assert provider.readiness() == "EXECUTION_DISABLED"


def test_process_environment_overrides_dotenv(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_provider_env(monkeypatch)
    (tmp_path / ".env").write_text(
        "COS_OPENAI_API_KEY=dotenv-secret-should-not-leak\nCOS_OPENAI_MODEL=dotenv-model\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("COS_OPENAI_API_KEY", _PROCESS_SECRET)
    monkeypatch.setenv("COS_OPENAI_MODEL", "process-model")
    monkeypatch.setenv("COS_LIVE_TEXT_REASONING_ENABLED", "true")
    settings = get_settings()
    provider = OpenAIReasoningProvider()
    assert settings.openai_model == "process-model"
    assert settings.openai_api_key is not None
    assert settings.openai_api_key.get_secret_value() == _PROCESS_SECRET
    assert provider.explicit_model() == "process-model"
    assert provider.readiness() == "READY"


def test_readiness_requires_both_key_and_model(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_provider_env(monkeypatch)
    grok = GrokReasoningProvider()
    openai = OpenAIReasoningProvider()
    assert grok.readiness() == "NOT_CONFIGURED"
    assert openai.readiness() == "NOT_CONFIGURED"

    monkeypatch.setenv("COS_XAI_API_KEY", _SECRET)
    assert GrokReasoningProvider().readiness() == "NOT_CONFIGURED"
    monkeypatch.delenv("COS_XAI_API_KEY")
    monkeypatch.setenv("COS_XAI_MODEL", "explicit-model")
    assert GrokReasoningProvider().readiness() == "NOT_CONFIGURED"

    monkeypatch.setenv("COS_OPENAI_MODEL", "explicit-openai")
    assert OpenAIReasoningProvider().readiness() == "NOT_CONFIGURED"
    monkeypatch.delenv("COS_OPENAI_MODEL")
    monkeypatch.setenv("COS_OPENAI_API_KEY", _SECRET)
    assert OpenAIReasoningProvider().readiness() == "NOT_CONFIGURED"

    monkeypatch.setenv("COS_XAI_API_KEY", _SECRET)
    monkeypatch.setenv("COS_XAI_MODEL", "explicit-model")
    monkeypatch.setenv("COS_LIVE_TEXT_REASONING_ENABLED", "false")
    assert GrokReasoningProvider().readiness() == "EXECUTION_DISABLED"
    monkeypatch.setenv("COS_LIVE_TEXT_REASONING_ENABLED", "true")
    assert GrokReasoningProvider().readiness() == "READY"

    monkeypatch.setenv("COS_OPENAI_API_KEY", _SECRET)
    monkeypatch.setenv("COS_OPENAI_MODEL", "explicit-openai")
    assert OpenAIReasoningProvider().readiness() == "READY"
    monkeypatch.setenv("COS_LIVE_TEXT_REASONING_ENABLED", "false")
    assert OpenAIReasoningProvider().readiness() == "EXECUTION_DISABLED"


def test_legacy_key_is_only_a_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("XAI_API_KEY", "legacy-key")
    monkeypatch.setenv("COS_XAI_MODEL", "explicit-model")
    assert GrokReasoningProvider().available() is True
    assert GrokReasoningProvider().explicit_model() == "explicit-model"
    monkeypatch.setenv("COS_XAI_API_KEY", "canonical-key")
    secret, model = GrokReasoningProvider()._credentials()
    assert secret == "canonical-key"
    assert model == "explicit-model"


def test_public_status_does_not_contain_the_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("COS_XAI_API_KEY", _SECRET)
    monkeypatch.setenv("COS_XAI_MODEL", "explicit-model")
    monkeypatch.setenv("COS_OPENAI_API_KEY", _PROCESS_SECRET)
    monkeypatch.setenv("COS_OPENAI_MODEL", "explicit-openai")
    payload = [provider.public_view() for provider in configured_reasoning_providers()]
    encoded = json.dumps(payload)
    settings_dump = json.dumps(get_settings().model_dump(mode="json"))
    assert _SECRET not in encoded
    assert _PROCESS_SECRET not in encoded
    assert _SECRET not in settings_dump
    assert _PROCESS_SECRET not in settings_dump
    assert payload[0]["configured"] is True
    assert payload[0]["explicit_model"] == "explicit-model"
    try:
        raise ProviderUnavailable("grok", "NOT_CONFIGURED")
    except ProviderUnavailable as exc:
        assert _SECRET not in str(exc)
