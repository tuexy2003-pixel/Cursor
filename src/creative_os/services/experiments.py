from creative_os.models import Experiment


def differing_dimensions(control: dict[str, object], variant: dict[str, object]) -> list[str]:
    keys = set(control) | set(variant)
    found: set[str] = set()
    for key in keys:
        if control.get(key) == variant.get(key):
            continue
        path = key if str(key).startswith("/") else f"/{key}"
        dimension = path.strip("/").split("/", 1)[0]
        found.add(dimension)
    return sorted(found)


def validate_experiment_isolation(
    *,
    mode: str,
    variable_dimension: str,
    control: dict[str, object],
    variant: dict[str, object],
) -> list[str]:
    changed = differing_dimensions(control, variant)
    if not changed:
        raise ValueError("control and variant do not differ")
    if mode == "SINGLE_VARIABLE":
        if changed != [variable_dimension]:
            raise ValueError(
                "single-variable experiment changed "
                f"{', '.join(changed)}; declared dimension is {variable_dimension}"
            )
        return changed
    if mode == "MULTIVARIATE":
        if variable_dimension not in changed:
            raise ValueError("multivariate experiment does not change the declared dimension")
        return changed
    raise ValueError("experiment mode must be SINGLE_VARIABLE or MULTIVARIATE")


def experiment_is_isolated(experiment: Experiment) -> bool:
    return experiment.mode in {"SINGLE_VARIABLE", "MULTIVARIATE"}
