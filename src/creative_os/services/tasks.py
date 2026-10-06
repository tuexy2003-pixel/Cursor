"""Creative tasks: the exact request a future model would be given."""

from typing import Any

from sqlalchemy.orm import Session

from creative_os.models import Creative, CreativeTask
from creative_os.services.lifecycle import mark_lifecycle
from creative_os.services.scope import ContextScope, validate_scope
from creative_os.util import utcnow


class TaskError(ValueError):
    pass


def create_creative_task(
    session: Session,
    *,
    program_id: str,
    stage: str,
    instruction: str,
    created_by: str,
    account_id: str | None = None,
    campaign_id: str | None = None,
    creative_id: str | None = None,
    ecosystem_id: str | None = None,
    constraints: dict[str, Any] | None = None,
    input_refs: dict[str, Any] | None = None,
    expected_output_type: str | None = None,
    notes: str | None = None,
) -> CreativeTask:
    if not instruction.strip():
        raise TaskError("a creative task requires an instruction")
    from creative_os.services.context_compiler import canonical_stage

    name = canonical_stage(stage)
    scope = validate_scope(
        session,
        ContextScope(
            program_id=program_id,
            account_id=account_id,
            campaign_id=campaign_id,
            creative_id=creative_id,
            ecosystem_id=ecosystem_id,
        ),
    )
    output = expected_output_type or _default_output(name)
    task = CreativeTask(
        program_id=scope.program_id or program_id,
        account_id=scope.account_id,
        campaign_id=scope.campaign_id,
        creative_id=scope.creative_id,
        ecosystem_id=scope.ecosystem_id,
        stage=name,
        instruction=instruction.strip(),
        constraints=constraints or {},
        input_refs=input_refs or {},
        created_by=created_by,
        created_at=utcnow(),
        status="OPEN",
        expected_output_type=output,
        notes=notes,
    )
    session.add(task)
    session.flush()
    return task


def consume_task(task: CreativeTask) -> None:
    if task.status == "CONSUMED":
        return
    if task.status != "OPEN":
        raise TaskError(f"creative task {task.id} cannot be consumed from {task.status}")
    mark_lifecycle(task)
    task.status = "CONSUMED"


def task_scope(task: CreativeTask) -> ContextScope:
    return ContextScope(
        program_id=task.program_id,
        account_id=task.account_id,
        campaign_id=task.campaign_id,
        creative_id=task.creative_id,
        ecosystem_id=task.ecosystem_id,
    )


def creative_for_task(session: Session, task: CreativeTask) -> Creative | None:
    if task.creative_id is None:
        return None
    return session.get(Creative, task.creative_id)


def _default_output(stage: str) -> str | None:
    if stage == "CONCEPT_GENERATION":
        return "CONCEPT_GENERATION"
    if stage == "STORY_DEVELOPMENT":
        return "STORY_DEVELOPMENT_AUDIT"
    return None
