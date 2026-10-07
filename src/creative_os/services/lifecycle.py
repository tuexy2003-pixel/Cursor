"""Markers for the only services allowed to change version lifecycle fields."""


def mark_lifecycle(target: object) -> None:
    object.__setattr__(target, "_lifecycle_transition", True)


def consume_lifecycle(target: object) -> bool:
    allowed = bool(getattr(target, "_lifecycle_transition", False))
    if allowed:
        object.__setattr__(target, "_lifecycle_transition", False)
    return allowed
