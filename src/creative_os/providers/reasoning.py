"""Text creative-reasoning adapters. Research, image, posting, and purchasing stay out."""

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib import error, request

from creative_os.config import get_settings

ALLOWED_OUTPUTS = frozenset({"CONCEPT_GENERATION", "STORY_DEVELOPMENT_AUDIT"})
DISABLED_CAPABILITIES = frozenset(
    {
        "web_research",
        "research",
        "pinterest",
        "visual_search",
        "image_editing",
        "image_generation",
        "posting",
        "purchasing",
    }
)
MAX_PROVIDERS_PER_COMPARISON = 2


class ProviderUnavailable(RuntimeError):
    def __init__(self, provider: str, status: str = "NOT_IMPLEMENTED") -> None:
        super().__init__(f"{provider} text reasoning is {status}")
        self.status = status
        self.provider = provider


class ProviderTimeout(RuntimeError):
    """The request was sent and no response came back. Do not retry it."""


class ProviderHTTPError(RuntimeError):
    def __init__(self, message: str, body: str = "") -> None:
        super().__init__(message)
        self.body = body


class ProviderModelMismatch(RuntimeError):
    pass


@dataclass
class ReasoningResult:
    text: str
    model_name: str | None = None
    model_version: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    cached_tokens: int | None = None
    cost: float | None = None
    currency: str | None = None
    usage: dict[str, Any] | None = None
    provider_request_id: str | None = None


class CreativeReasoningProvider:
    name = "unconfigured"
    uses_paid_transport = False
    max_output_tokens: int | None = None

    def available(self) -> bool:
        return False

    def readiness(self) -> str:
        return "NOT_IMPLEMENTED"

    def explicit_model(self) -> str | None:
        return None

    def generate_concepts(self, packet_text: str) -> ReasoningResult:
        raise ProviderUnavailable(self.name)

    def audit_story_development(self, packet_text: str) -> ReasoningResult:
        raise ProviderUnavailable(self.name)


class _ChatCompletionsProvider(CreativeReasoningProvider):
    """OpenAI-compatible chat completions. The packet text is the user message."""

    uses_paid_transport = True
    url = ""
    env_keys: tuple[str, ...] = ()
    model_env = ""

    def available(self) -> bool:
        """A key is present. That is not permission to spend."""
        return _secret(self.env_keys) is not None

    def explicit_model(self) -> str | None:
        value = os.environ.get(self.model_env, "").strip()
        return value or None

    def readiness(self) -> str:
        if not self.available() or self.explicit_model() is None:
            return "NOT_CONFIGURED"
        if not get_settings().live_text_reasoning_enabled:
            return "EXECUTION_DISABLED"
        return "READY"

    def generate_concepts(self, packet_text: str) -> ReasoningResult:
        return self._complete(packet_text, "CONCEPT_GENERATION")

    def audit_story_development(self, packet_text: str) -> ReasoningResult:
        return self._complete(packet_text, "STORY_DEVELOPMENT_AUDIT")

    def _complete(self, packet_text: str, output_name: str) -> ReasoningResult:
        secret = _secret(self.env_keys)
        model = self.explicit_model()
        if secret is None or model is None:
            raise ProviderUnavailable(self.name, "NOT_CONFIGURED")
        body: dict[str, Any] = {
            "model": model,
            "temperature": 0,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Return only the JSON object required by the output contract in the packet. "
                        f"The contract name is {output_name}. Do not search the web. "
                        "Do not claim you changed stored creative records."
                    ),
                },
                {"role": "user", "content": packet_text},
            ],
        }
        if isinstance(self.max_output_tokens, int) and self.max_output_tokens > 0:
            body["max_tokens"] = self.max_output_tokens
        payload = json.dumps(body).encode("utf-8")
        req = request.Request(
            self.url,
            data=payload,
            headers={"Authorization": f"Bearer {secret}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=90) as response:
                raw_text = response.read().decode("utf-8")
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ProviderHTTPError(f"{self.name} request failed: {exc.code} {detail[:400]}", detail) from exc
        except TimeoutError as exc:
            raise ProviderTimeout(str(exc)) from exc
        except error.URLError as exc:
            if isinstance(exc.reason, TimeoutError):
                raise ProviderTimeout(str(exc.reason)) from exc
            raise ProviderHTTPError(f"{self.name} transport failed: {exc.reason}") from exc
        try:
            raw = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise ProviderHTTPError(f"{self.name} returned malformed JSON", raw_text) from exc
        if not isinstance(raw, dict):
            raise ProviderHTTPError(f"{self.name} returned a non-object response", raw_text)
        returned_model = str(raw.get("model") or "")
        if returned_model and returned_model != model:
            raise ProviderModelMismatch(f"provider returned {returned_model}; authorization asked for {model}")
        try:
            text = raw["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderHTTPError(f"{self.name} returned a malformed response", raw_text) from exc
        usage_raw = raw.get("usage")
        usage: dict[str, Any] = usage_raw if isinstance(usage_raw, dict) else {}
        request_id = raw.get("id")
        return ReasoningResult(
            text=text,
            model_name=model,
            model_version=str(raw.get("system_fingerprint") or "") or None,
            input_tokens=_int_or_none(usage.get("prompt_tokens")),
            output_tokens=_int_or_none(usage.get("completion_tokens")),
            cached_tokens=_int_or_none((usage.get("prompt_tokens_details") or {}).get("cached_tokens")),
            cost=_number_or_none(usage.get("cost")),
            currency=usage.get("currency") if isinstance(usage.get("currency"), str) else None,
            usage=usage or None,
            provider_request_id=request_id if isinstance(request_id, str) and request_id else None,
        )


class GrokReasoningProvider(_ChatCompletionsProvider):
    name = "grok"
    url = "https://api.x.ai/v1/chat/completions"
    env_keys = ("COS_XAI_API_KEY", "XAI_API_KEY")
    model_env = "COS_XAI_MODEL"


class OpenAIReasoningProvider(_ChatCompletionsProvider):
    name = "openai"
    url = "https://api.openai.com/v1/chat/completions"
    env_keys = ("COS_OPENAI_API_KEY", "OPENAI_API_KEY")
    model_env = "COS_OPENAI_MODEL"


def configured_reasoning_providers() -> list[CreativeReasoningProvider]:
    return [GrokReasoningProvider(), OpenAIReasoningProvider()]


def reasoning_provider(name: str) -> CreativeReasoningProvider:
    for provider in configured_reasoning_providers():
        if provider.name == name:
            return provider
    raise KeyError(name)


def _secret(names: tuple[str, ...]) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def _int_or_none(value: object) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return None


def _number_or_none(value: object) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int | float):
        return float(value)
    return None
