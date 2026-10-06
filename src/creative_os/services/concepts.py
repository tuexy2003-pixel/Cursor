"""Minimal concept candidates. A model may propose. Only a human may select."""

from typing import Any

from sqlalchemy.orm import Session

from creative_os.models import ApprovalEvent, ConceptCandidate, Creative, CreativeTask
from creative_os.services.lifecycle import mark_lifecycle
from creative_os.services.scope import validate_scope
from creative_os.services.tasks import task_scope
from creative_os.util import utcnow


class ConceptError(ValueError):
    pass


def propose_concept(
    session: Session,
    *,
    task: CreativeTask,
    title: str,
    created_by: str,
    premise: str | None = None,
    family: str | None = None,
    hook_direction: str | None = None,
    commerce_relation: str | None = None,
    structured_payload: dict[str, Any] | None = None,
    source_model_run_id: str | None = None,
) -> ConceptCandidate:
    if not title.strip():
        raise ConceptError("a concept requires a title")
    scope = validate_scope(session, task_scope(task))
    concept = ConceptCandidate(
        task_id=task.id,
        program_id=scope.program_id or task.program_id,
        account_id=scope.account_id,
        campaign_id=scope.campaign_id,
        ecosystem_id=scope.ecosystem_id,
        source_model_run_id=source_model_run_id,
        title=title.strip(),
        premise=premise,
        family=family,
        hook_direction=hook_direction,
        commerce_relation=commerce_relation,
        structured_payload=structured_payload or {},
        status="PROPOSED",
        created_by=created_by,
        created_at=utcnow(),
    )
    session.add(concept)
    session.flush()
    return concept


def decide_concept(
    session: Session,
    concept: ConceptCandidate,
    decision: str,
    actor: str,
    notes: str | None = None,
    creative: Creative | None = None,
) -> ConceptCandidate:
    choice = decision.strip().upper()
    if concept.created_by and actor == concept.created_by and actor != "operator":
        raise ConceptError("a model cannot select or reject its own concept")
    if choice == "SELECT":
        new_status = "SELECTED"
        allowed = concept.status == "PROPOSED"
    elif choice == "REJECT":
        new_status = "REJECTED"
        allowed = concept.status == "PROPOSED"
    elif choice == "SUPERSEDE":
        new_status = "SUPERSEDED"
        allowed = concept.status == "SELECTED"
    else:
        raise ConceptError("concept decision must be SELECT, REJECT, or SUPERSEDE")
    if not allowed:
        raise ConceptError(f"cannot {choice} a concept in {concept.status}")
    mark_lifecycle(concept)
    previous = concept.status
    concept.status = new_status
    session.add(
        ApprovalEvent(
            object_type="concept_candidate",
            object_id=concept.id,
            version_id=None,
            status=new_status,
            actor=actor,
            notes=notes,
            previous_state=previous,
            created_at=utcnow(),
        )
    )
    if new_status == "SELECTED" and creative is not None:
        link_selected_concept(creative, concept)
    session.flush()
    return concept


def link_selected_concept(creative: Creative, concept: ConceptCandidate) -> None:
    if concept.status != "SELECTED":
        raise ConceptError("only a selected concept can be linked to a creative")
    if creative.program_id != concept.program_id:
        raise ConceptError("concept belongs to a different program")
    if (
        creative.current_approved_story_lock_version_id
        and creative.selected_concept_id
        and creative.selected_concept_id != concept.id
    ):
        raise ConceptError("do not replace the concept after a story lock exists")
    creative.selected_concept_id = concept.id
