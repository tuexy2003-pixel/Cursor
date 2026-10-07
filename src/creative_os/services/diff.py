from typing import Any


def document_diff(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    changes: dict[str, Any] = {}
    keys = sorted(set(left) | set(right))
    for key in keys:
        if left.get(key) != right.get(key):
            changes[key] = {"from": left.get(key), "to": right.get(key)}
    return changes


def deep_diff(left: Any, right: Any, prefix: str = "") -> list[dict[str, Any]]:
    """JSON-path diff. List indexes and object keys are both addressable."""
    if left == right:
        return []
    if isinstance(left, dict) and isinstance(right, dict):
        changes: list[dict[str, Any]] = []
        for key in sorted(set(left) | set(right), key=str):
            changes.extend(deep_diff(left.get(key), right.get(key), f"{prefix}/{key}"))
        return changes
    if isinstance(left, list) and isinstance(right, list):
        changes = []
        for index in range(max(len(left), len(right))):
            before = left[index] if index < len(left) else None
            after = right[index] if index < len(right) else None
            changes.extend(deep_diff(before, after, f"{prefix}/{index}"))
        return changes
    return [{"path": prefix or "/", "from": left, "to": right}]


def changed_paths(left: dict[str, Any], right: dict[str, Any]) -> list[str]:
    return [row["path"] for row in deep_diff(left, right)]
