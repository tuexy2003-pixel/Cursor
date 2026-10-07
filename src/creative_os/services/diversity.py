"""Batch diversity is measured after concepts exist. It does not steer ideation."""

from typing import Any

UNDERREPRESENTED_LIBRARY = (
    "mishap_consequence",
    "gift_surprise",
    "social_misunderstanding",
    "desire_led_utility",
    "claim_versus_commerce_proof",
)

_CLAIM = (
    "thinks she",
    "thinks he",
    "edited after",
    "got it wrong",
    "social credit",
    "the one who ordered",
)
_PROOF = ("order", "receipt", "doordash", "proof")
_MISREAD = ("misread", "shorted", "judging the bag", "sad bag")
_GIFT = ("birthday", "surprise gift", "hidden gift")
_MISHAP = ("overslept", "accident", "spilled", "mishap")
_DESIRE = ("bring their own", "bring-your-own", "family d", "desire", "hosted night", "comfort spread")


def fingerprint_concept(fields: dict[str, Any]) -> dict[str, Any]:
    """Lightweight extractor. Missing dimensions stay absent instead of being guessed."""
    text = " ".join(
        str(fields.get(key) or "")
        for key in (
            "title",
            "family",
            "premise",
            "human_event",
            "stakes",
            "reveal",
            "proof_surface_direction",
            "commerce_relation",
            "hook_direction",
        )
    ).casefold()
    skeleton = _skeleton(text)
    if skeleton is None:
        return {}
    mapping = {
        "claim_versus_commerce_proof": {
            "conflict_or_judgment_shape": "claim_contradicted",
            "proof_mechanism": "commerce_order_surface",
            "primary_attention_engine": "claim_versus_proof",
            "reveal_type": "order_surface_contradicts_claim",
        },
        "social_misunderstanding": {
            "conflict_or_judgment_shape": "public_misread",
            "primary_attention_engine": "social_misunderstanding",
        },
        "gift_surprise": {
            "primary_attention_engine": "gift_surprise",
            "reveal_type": "hidden_gift",
        },
        "mishap_consequence": {
            "primary_attention_engine": "mishap_consequence",
        },
        "desire_led_utility": {
            "primary_attention_engine": "desire_led_utility",
            "commerce_role": "outcome_means_or_absent",
        },
    }
    return {
        dimension: {
            "value": value,
            "assignment": "DETERMINISTIC_INFERRED",
            "source": "deterministic skeleton phrases",
        }
        for dimension, value in mapping[skeleton].items()
    }


def skeleton_key(fingerprint: dict[str, Any]) -> str | None:
    engine = _value(fingerprint, "primary_attention_engine")
    if engine == "claim_versus_proof":
        return "claim_versus_commerce_proof"
    return engine


def audit_batch(concepts: list[dict[str, Any]], constraints: dict[str, Any] | None = None) -> dict[str, Any]:
    constraints = constraints or {}
    allowed = _allowed_repeat(constraints)
    grouped: dict[str, list[str]] = {}
    unknown: list[str] = []
    for concept in concepts:
        key = skeleton_key(concept.get("mechanism_fingerprint") or {})
        title = str(concept.get("title") or concept.get("id") or "untitled")
        if key is None:
            unknown.append(title)
            continue
        grouped.setdefault(key, []).append(title)
    largest = max((len(titles) for titles in grouped.values()), default=0)
    repeated = {key: titles for key, titles in grouped.items() if len(titles) >= 2}
    flagged = [
        {"skeleton": key, "titles": titles, "count": len(titles)}
        for key, titles in grouped.items()
        if len(titles) >= 3 and key not in allowed
    ]
    if flagged:
        level = "LOW"
        reason = "3 or more concepts share the same primary narrative/proof skeleton"
    elif largest >= 2 and not (largest >= 3 and set(repeated) <= allowed):
        level = "MEDIUM"
        reason = "some skeletons repeat, below the three-concept flag"
    elif concepts and not grouped:
        level = "MEDIUM"
        reason = "no skeleton could be extracted; diversity is not claimed"
    else:
        level = "HIGH"
        reason = "no primary skeleton is shared by three or more concepts"
    if allowed and flagged == [] and largest >= 3:
        reason = "repeated skeleton is allowed because the task requested variants of that mechanism"
        level = "MEDIUM" if largest >= 3 else level
    known_count = len(concepts) - len(unknown)
    if level == "HIGH" and unknown and len(unknown) >= known_count:
        level = "MEDIUM"
        reason = "too many unknown skeletons for a high-certainty diversity claim"
    report: dict[str, Any] = {
        "level": level,
        "assessment_method": "DETERMINISTIC_HEURISTIC",
        "certainty": "HEURISTIC",
        "coverage": {"known_count": known_count, "total_count": len(concepts)},
        "reason": reason,
        "skeletons": {key: titles for key, titles in sorted(grouped.items())},
        "unknown": unknown,
        "flagged_repeated_skeletons": flagged,
        "allowed_repeated_skeletons": sorted(allowed),
        "repair_plan": None,
    }
    if level == "LOW":
        report["repair_plan"] = _repair(flagged, set(grouped))
    return report


def _repair(flagged: list[dict[str, Any]], present: set[str]) -> dict[str, Any]:
    cluster = max(flagged, key=lambda item: item["count"])
    titles = list(cluster["titles"])
    return {
        "keep": [
            {
                "title": titles[0],
                "reason": "first concept in the repeated skeleton; no separate quality score",
            }
        ],
        "replace_for_diversity": [
            {"title": title, "reason": f"overlaps skeleton {cluster['skeleton']}"} for title in titles[1:]
        ],
        "underrepresented": [name for name in UNDERREPRESENTED_LIBRARY if name not in present],
        "generates_replacements": False,
    }


def _allowed_repeat(constraints: dict[str, Any]) -> set[str]:
    if constraints.get("allow_repeated_skeleton") is True:
        requested = constraints.get("requested_variants_of")
        if isinstance(requested, str) and requested:
            return {requested}
        return set(UNDERREPRESENTED_LIBRARY)
    requested = constraints.get("requested_variants_of")
    if isinstance(requested, str) and requested:
        return {requested}
    return set()


def _skeleton(text: str) -> str | None:
    if any(phrase in text for phrase in _CLAIM) and any(phrase in text for phrase in _PROOF):
        return "claim_versus_commerce_proof"
    if any(phrase in text for phrase in _MISREAD):
        return "social_misunderstanding"
    if any(phrase in text for phrase in _GIFT):
        return "gift_surprise"
    if any(phrase in text for phrase in _MISHAP):
        return "mishap_consequence"
    if any(phrase in text for phrase in _DESIRE):
        return "desire_led_utility"
    return None


def _value(fingerprint: dict[str, Any], dimension: str) -> str | None:
    row = fingerprint.get(dimension)
    if isinstance(row, dict):
        value = row.get("value")
        return str(value) if value else None
    return None
