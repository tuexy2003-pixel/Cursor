"""Account identity anchors. Generic wording is not the same failure as a contradiction."""

import re
from typing import Any

USAGE_GUIDANCE = "use when naturally relevant; do not force the name into every artifact"
_AS_RELATION = re.compile(r"^(.+?)\s+as\s+(.+)$", re.IGNORECASE)
_WRONG_ROLE = {
    "boyfriend": ("husband", "wife"),
    "girlfriend": ("wife", "husband"),
    "mom": ("wife",),
    "mother": ("wife",),
}


def identity_anchors(observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    anchors: list[dict[str, Any]] = []
    for row in observations:
        if row.get("field_name") != "recurring_relationship":
            continue
        if row.get("evidence_kind") != "HUMAN_SET_CONSTRAINT":
            continue
        match = _AS_RELATION.match(str(row.get("value") or "").strip())
        if match is None:
            continue
        anchors.append(
            {
                "relationship_type": match.group(2).strip().casefold(),
                "canonical_name": match.group(1).strip(),
                "status": "ESTABLISHED",
                "usage_guidance": USAGE_GUIDANCE,
                "source": "human-approved account context",
                "confidence": row.get("confidence"),
                "evidence_kind": row.get("evidence_kind"),
                "field_name": row.get("field_name"),
            }
        )
    return anchors


def assess_account_identity(text: str, anchors: list[dict[str, Any]]) -> dict[str, Any]:
    if not anchors:
        return {"level": "NO_ANCHOR", "contradiction": False, "reason": "no established identity anchor"}
    lowered = text.casefold()
    for anchor in anchors:
        name = str(anchor["canonical_name"])
        relation = str(anchor["relationship_type"])
        if name.casefold() in lowered:
            return {
                "level": "ACCOUNT_SPECIFIC",
                "contradiction": False,
                "reason": f"uses the established name {name}",
            }
        for wrong in _WRONG_ROLE.get(relation, ()):
            if re.search(rf"\b{wrong}\b", lowered):
                return {
                    "level": "WRONG_ACCOUNT_REALITY",
                    "contradiction": True,
                    "reason": f"uses {wrong}; the established relationship is {relation}",
                }
        named = re.search(rf"\b{re.escape(relation)}\b(?:\s+named)?\s+([A-Z][a-z]+)", text)
        if named is not None and named.group(1).casefold() != name.casefold():
            return {
                "level": "CONTRADICTION",
                "contradiction": True,
                "reason": f"names {named.group(1)} as {relation}; the established name is {name}",
            }
        if re.search(rf"\b{re.escape(relation)}\b", lowered):
            return {
                "level": "GENERIC_WORDING",
                "contradiction": False,
                "reason": f"uses {relation} without the established name {name}",
            }
    return {
        "level": "NO_RELATIONSHIP_REFERENCE",
        "contradiction": False,
        "reason": "the text does not refer to the established relationship",
    }
