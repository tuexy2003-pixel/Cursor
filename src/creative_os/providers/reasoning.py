"""Text creative-reasoning adapters. Research, image, and posting stay out of this module."""

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib import error, request

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
    }
)


class ProviderUnavailable(RuntimeError):
    def __init__(self, provider: str) -> None:
        super().__init__(f"{provider} text reasoning is NOT_IMPLEMENTED")
        self.status = "NOT_IMPLEMENTED"
        self.provider = provider


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


class CreativeReasoningProvider:
    name = "unconfigured"

    def available(self) -> bool:
        return False

    def generate_concepts(self, packet_text: str) -> ReasoningResult:
        raise ProviderUnavailable(self.name)

    def audit_story_development(self, packet_text: str) -> ReasoningResult:
        raise ProviderUnavailable(self.name)


class _ChatCompletionsProvider(CreativeReasoningProvider):
    """OpenAI-compatible chat completions. The packet text is the user message."""

    url = ""
    env_keys: tuple[str, ...] = ()
    model_env = ""
    default_model = ""

    def available(self) -> bool:
        return _secret(self.env_keys) is not None

    def generate_concepts(self, packet_text: str) -> ReasoningResult:
        return self._complete(packet_text, "CONCEPT_GENERATION")

    def audit_story_development(self, packet_text: str) -> ReasoningResult:
        return self._complete(packet_text, "STORY_DEVELOPMENT_AUDIT")

    def _complete(self, packet_text: str, output_name: str) -> ReasoningResult:
        secret = _secret(self.env_keys)
        if secret is None:
            raise ProviderUnavailable(self.name)
        model = os.environ.get(self.model_env) or self.default_model
        body = {
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
        payload = json.dumps(body).encode("utf-8")
        req = request.Request(
            self.url,
            data=payload,
            headers={"Authorization": f"Bearer {secret}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=90) as response:
                raw = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"{self.name} request failed: {exc.code} {detail[:400]}") from exc
        text = raw["choices"][0]["message"]["content"]
        usage = raw.get("usage") if isinstance(raw.get("usage"), dict) else {}
        return ReasoningResult(
            text=text,
            model_name=str(raw.get("model") or model),
            model_version=str(raw.get("system_fingerprint") or "") or None,
            input_tokens=_int_or_none(usage.get("prompt_tokens")),
            output_tokens=_int_or_none(usage.get("completion_tokens")),
            cached_tokens=_int_or_none((usage.get("prompt_tokens_details") or {}).get("cached_tokens")),
            cost=None,
            currency=None,
            usage=usage or None,
        )


class GrokReasoningProvider(_ChatCompletionsProvider):
    name = "grok"
    url = "https://api.x.ai/v1/chat/completions"
    env_keys = ("COS_XAI_API_KEY", "XAI_API_KEY")
    model_env = "COS_XAI_MODEL"
    default_model = "grok-4"


class OpenAIReasoningProvider(_ChatCompletionsProvider):
    name = "openai"
    url = "https://api.openai.com/v1/chat/completions"
    env_keys = ("COS_OPENAI_API_KEY", "OPENAI_API_KEY")
    model_env = "COS_OPENAI_MODEL"
    default_model = "gpt-4.1"


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
    if isinstance(value, int):
        return value
    return None
