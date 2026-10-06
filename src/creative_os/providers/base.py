from typing import Any, Protocol


class ProviderRequest(Protocol):
    capability: str
    inputs: dict[str, Any]


class ProviderResult:
    def __init__(self, status: str, output: dict[str, Any] | None = None, error: str | None = None) -> None:
        self.status = status
        self.output = output or {}
        self.error = error


class CreativeProvider(Protocol):
    capability: str

    def run(self, capability: str, inputs: dict[str, Any]) -> ProviderResult: ...
