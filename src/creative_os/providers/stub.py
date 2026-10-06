from typing import Any

from creative_os.providers.base import ProviderResult


class StubProvider:
    """Explicit non-execution adapter. Phase 6 does not call a model."""

    def __init__(self, name: str, capability: str) -> None:
        self.name = name
        self.capability = capability

    def run(self, capability: str, inputs: dict[str, Any]) -> ProviderResult:
        return ProviderResult(
            status="NOT_IMPLEMENTED",
            output={"provider": self.name, "capability": capability, "input_keys": sorted(inputs)},
            error="provider execution is not enabled",
        )
