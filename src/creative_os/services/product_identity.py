"""Product identifier checks. Unknown ids stay unknown. Explicit superseded ids fail."""

import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from creative_os.models import Creative, StoryLockVersion
from creative_os.schemas.story_lock import FieldPatch, StoryLockDocument
from creative_os.services.story_locks import apply_story_lock_correction

_SUPERSEDED = re.compile(
    r"superseded:\s*([^,;\)]+?),\s*(TCIN|SKU|variant id|retailer item id)\s+(\d+)",
    re.IGNORECASE,
)


def product_identifier_findings(document: StoryLockDocument, source_text: str) -> list[dict[str, Any]]:
    known = [
        {
            "kind": match.group(2).upper().replace(" ", "_"),
            "identifier": match.group(3),
            "known_owner": match.group(1).strip(),
        }
        for match in _SUPERSEDED.finditer(source_text)
    ]
    findings: list[dict[str, Any]] = []
    for index, item in enumerate(document.line_items):
        if not item.external_id:
            continue
        matched = next((row for row in known if row["identifier"] == item.external_id), None)
        if matched is None:
            continue
        owner = matched["known_owner"].casefold()
        title = (item.title or "").casefold()
        model = (item.model or "").casefold()
        if owner in title or owner in model:
            continue
        findings.append(
            {
                "status": "FAIL",
                "line_index": index,
                "title": item.title,
                "model": item.model,
                "identifier_kind": matched["kind"],
                "identifier": item.external_id,
                "known_owner": matched["known_owner"],
                "evidence": "explicit superseded clause in the story lock text",
            }
        )
    return findings


def clear_superseded_product_identifiers(
    session: Session,
    creative: Creative,
    actor: str,
) -> StoryLockVersion | None:
    if not creative.current_approved_story_lock_version_id:
        return None
    current = session.get(StoryLockVersion, creative.current_approved_story_lock_version_id)
    if current is None:
        return None
    document = StoryLockDocument.model_validate(current.content_json)
    source = current.content_markdown or ""
    findings = product_identifier_findings(document, source)
    if not findings:
        return None
    patches = [FieldPatch(path=f"/line_items/{row['line_index']}/external_id", value=None) for row in findings]
    owners = ", ".join(f"{row['identifier']} ({row['known_owner']})" for row in findings)
    return apply_story_lock_correction(
        session,
        creative,
        {},
        actor=actor,
        reason=(
            "Clear product identifiers that the lock text assigns to a superseded model. "
            f"No replacement id is invented. Cleared: {owners}."
        ),
        patches=patches,
        expected_current_story_lock_version_id=current.id,
    )


def clear_target_identifier_if_present(session: Session, actor: str = "operator") -> str:
    creative = session.scalar(select(Creative).where(Creative.slug == "chore-stuff-target"))
    if creative is None:
        return "missing"
    version = clear_superseded_product_identifiers(session, creative, actor)
    if version is None:
        return "already_clear"
    return version.id
