"""Prepare frozen smoke-test tasks. This module never calls a provider."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from creative_os.models import Account, ContextBundle, Creative, CreativeTask, Ecosystem, Program
from creative_os.services.context_bundles import create_context_bundle
from creative_os.services.tasks import create_creative_task
from creative_os.util import utcnow

CONCEPT_NOTE = "v0.3.2-safe-live-smoke:concept-generation"
AUDIT_NOTE = "v0.3.2-safe-live-smoke:story-audit"
CONCEPT_INSTRUCTION = (
    "Propose exactly 2 concepts for Maria in the DoorDash food-and-couples lane. "
    "This is a transport smoke test, not a quality benchmark. "
    "Do not research. Do not select a winner. Leave unknown fields null."
)
AUDIT_INSTRUCTION = (
    "Diagnose the current Target creative. "
    "This is an optional second smoke test and it is diagnosis only. "
    "Do not change the story lock. Do not research."
)


def prepare_smoke_tests(session: Session, *, actor: str = "operator") -> dict[str, Any]:
    """Create or reuse the two frozen bundles. Does not authorize or execute."""
    program = session.scalar(select(Program).limit(1))
    maria = session.scalar(select(Account).where(Account.slug == "maria"))
    doordash = session.scalar(select(Ecosystem).where(Ecosystem.code == "DOORDASH"))
    target = session.scalar(select(Creative).where(Creative.slug == "chore-stuff-target"))
    if program is None or maria is None or doordash is None or target is None:
        raise ValueError("smoke tests require the imported Maria, DoorDash, and Target records")
    concept = _concept_bundle(session, program, maria, doordash, actor)
    audit = _audit_bundle(session, target, actor)
    return {"concept_generation": concept, "story_development_audit": audit, "executed": False}


def _concept_bundle(
    session: Session,
    program: Program,
    maria: Account,
    doordash: Ecosystem,
    actor: str,
) -> dict[str, Any]:
    task = session.scalar(select(CreativeTask).where(CreativeTask.notes == CONCEPT_NOTE))
    if task is None:
        task = create_creative_task(
            session,
            program_id=program.id,
            account_id=maria.id,
            ecosystem_id=doordash.id,
            stage="CONCEPT_GENERATION",
            instruction=CONCEPT_INSTRUCTION,
            created_by=actor,
            constraints={"concept_count": 2, "smoke_test": "v0.3.2"},
            notes=CONCEPT_NOTE,
        )
    bundle = _bundle_for(session, task, creative=None)
    return _view(task, bundle)


def _audit_bundle(session: Session, creative: Creative, actor: str) -> dict[str, Any]:
    task = session.scalar(select(CreativeTask).where(CreativeTask.notes == AUDIT_NOTE))
    if task is None:
        task = create_creative_task(
            session,
            program_id=creative.program_id,
            account_id=creative.account_id,
            campaign_id=creative.campaign_id,
            creative_id=creative.id,
            ecosystem_id=creative.ecosystem_id,
            stage="STORY_DEVELOPMENT",
            instruction=AUDIT_INSTRUCTION,
            created_by=actor,
            constraints={"smoke_test": "v0.3.2", "diagnosis_only": True},
            notes=AUDIT_NOTE,
        )
    bundle = _bundle_for(session, task, creative=creative)
    return _view(task, bundle)


def _bundle_for(session: Session, task: CreativeTask, creative: Creative | None) -> ContextBundle:
    found = session.scalar(select(ContextBundle).where(ContextBundle.creative_task_id == task.id))
    if found is not None:
        return found
    return create_context_bundle(session, creative, task=task, as_of=utcnow())


def _view(task: CreativeTask, bundle: ContextBundle) -> dict[str, Any]:
    return {
        "task_id": task.id,
        "task_notes": task.notes,
        "stage": task.expected_output_type,
        "instruction": task.instruction,
        "constraints": task.constraints,
        "context_bundle_id": bundle.id,
        "context_bundle_hash": bundle.payload_hash,
        "character_count": len(bundle.compiled_text or ""),
        "estimated_tokens": bundle.token_estimate,
        "executed": False,
    }
