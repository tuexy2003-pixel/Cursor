from typing import Any


def document_diff(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    changes: dict[str, Any] = {}
    keys = sorted(set(left) | set(right))
    for key in keys:
        if left.get(key) != right.get(key):
            changes[key] = {"from": left.get(key), "to": right.get(key)}
    return changes
