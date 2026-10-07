import json
from pathlib import Path

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from creative_os.config import repo_root
from creative_os.importers.handoff import import_handoff
from creative_os.mcp.server import MUTATION_TOOLS, PROHIBITED_TOOLS, READ_TOOLS, invoke
from creative_os.models import Asset, ConceptCandidate, Creative, Program, ProviderInvocation, StoryAuditRecord
from creative_os.models.company import (
    ApprovalRequest,
    McpAuditLog,
    Specialist,
    SpecialistAssignment,
    StepRun,
    VerificationResult,
    WorkflowDefinitionVersion,
    WorkOrder,
)
from creative_os.models.entities import ImmutableVersionError
from creative_os.services.control_plane import (
    NEW_CREATIVE_V1,
    ControlPlaneError,
    assess_reference_readiness,
    company_status,
    create_action_authorization,
    create_work_order,
    decide_action_authorization,
    decide_approval,
    ensure_new_creative_v1,
    ensure_registry,
    execute_authorized_action,
    import_manual_response,
    mark_external_status,
    recheck_reference_readiness,
    record_verification,
    request_external_execution,
    resume_step,
    start_workflow,
    workflow_history,
    workflow_run_view,
)
from creative_os.services.story_locks import propose_story_lock_change
from creative_os.util import sha256_text, utcnow

pytestmark = pytest.mark.core

REQUIREMENT = {
    "ecosystem": "DOORDASH",
    "surface_type": "missing-checkout-surface",
    "state": "applied",
    "mode": "dark",
    "product": "dashpass-test",
    "required_role": "REFERENCE",
    "reason": "checkout proof for this creative",
}


def _creative(session: Session) -> Creative:
    import_handoff(session, repo_root() / "source_snapshots/2026-10-05")
    session.flush()
    creative = session.scalar(select(Creative).where(Creative.slug == "chore-stuff-target"))
    assert creative is not None
    return creative


def _concepts() -> str:
    return json.dumps(
        {
            "concepts": [
                {
                    "title": "Birthday cart",
                    "premise": "She notices the birthday reward while checking out",
                    "family": "proof",
                    "hook_direction": "today",
                    "human_event": "birthday",
                    "why_it_fits_account": "maria",
                },
                {
                    "title": "Wrong total",
                    "premise": "The bag total does not match the app",
                    "family": "mismatch",
                    "hook_direction": "receipt",
                    "human_event": "checkout",
                    "why_it_fits_account": "careful",
                },
                {
                    "title": "Rain delay",
                    "premise": "The order sits while the weather turns",
                    "family": "wait",
                    "hook_direction": "window",
                    "human_event": "delay",
                    "why_it_fits_account": "patience",
                },
            ]
        }
    )


def _story() -> str:
    return json.dumps(
        {
            "overall_status": "NEEDS_CHANGES",
            "diagnosis": "The hook is soft.",
            "hook_assessment": "soft",
            "propulsion_assessment": "steady",
            "viral_texture_assessment": "light",
            "continuity_assessment": "holds",
            "comment_door_assessment": "one door",
            "commerce_integration_assessment": "late",
            "proof_boundary_assessment": "clear",
        }
    )


def _step(session: Session, run_id: str, node_id: str) -> StepRun:
    step = session.scalar(select(StepRun).where(StepRun.workflow_run_id == run_id, StepRun.node_id == node_id))
    assert step is not None
    return step


def _waiting_assignment(session: Session) -> SpecialistAssignment:
    row = session.scalar(
        select(SpecialistAssignment).where(SpecialistAssignment.status == "WAITING_EXTERNAL_RESPONSE")
    )
    assert row is not None
    return row


def test_published_graph_is_explicit_and_versioned(session: Session) -> None:
    version = ensure_new_creative_v1(session)
    again = ensure_new_creative_v1(session)
    assert version.id == again.id
    assert version.version_number == 1
    assert [node["kind"] for node in version.graph] == [node["kind"] for node in NEW_CREATIVE_V1]
    assert "EXTERNAL_EXECUTION" not in {node["kind"] for node in version.graph}
    with pytest.raises(ControlPlaneError) as caught:
        start_workflow(session, "missing", definition_key="INVENTED_BY_MODEL")
    assert caught.value.code == "UNKNOWN_WORKFLOW"


def test_new_creative_workflow_stops_for_humans_and_references(session: Session, monkeypatch) -> None:
    def explode(*_args, **_kwargs):
        raise AssertionError("manual transport made a network call")

    monkeypatch.setattr("urllib.request.urlopen", explode)
    monkeypatch.setattr("http.client.HTTPConnection.request", explode)
    creative = _creative(session)
    pointer = creative.current_approved_story_lock_version_id
    proposed = propose_story_lock_change(
        session,
        creative,
        {"floating_hook": "a person still has to approve this"},
        proposer="grok",
        reason="needs a person",
    )
    order = create_work_order(
        session,
        goal="Make one new creative and stop before production.",
        program_id=creative.program_id,
        account_id=creative.account_id,
        campaign_id=creative.campaign_id,
        creative_id=creative.id,
        reference_requirements=[REQUIREMENT],
    )
    invocations = session.scalar(select(func.count()).select_from(ProviderInvocation))
    run = start_workflow(session, order.id)
    assert run.status == "WAITING_SPECIALIST"
    assert _step(session, run.id, "compile_concept_context").status == "SUCCEEDED"
    assignment = _waiting_assignment(session)
    assert assignment.transport == "MANUAL_SUBSCRIPTION"
    assert assignment.api_verified is False
    invalid = import_manual_response(
        session,
        assignment.id,
        "{not json",
        provider_name="grok",
        model_name="grok-4",
    )
    assert invalid.validation_status == "INVALID"
    assert invalid.status == "WAITING_EXTERNAL_RESPONSE"
    assert session.scalar(select(func.count()).select_from(ConceptCandidate)) == 0
    assert _step(session, run.id, "select_concept").status == "PENDING"
    imported = import_manual_response(
        session,
        assignment.id,
        _concepts(),
        provider_name="grok",
        model_name="grok-4",
    )
    assert imported.validation_status == "VALID"
    assert imported.api_verified is False
    concepts = list(session.scalars(select(ConceptCandidate)))
    assert concepts
    assert {concept.status for concept in concepts} == {"PROPOSED"}
    session.refresh(creative)
    assert creative.current_approved_story_lock_version_id == pointer
    session.refresh(run)
    assert run.status == "WAITING_HUMAN"
    story = _step(session, run.id, "story_development")
    with pytest.raises(ControlPlaneError) as skipped:
        resume_step(session, story.id)
    assert skipped.value.code == "SKIP_FORBIDDEN"
    request = session.scalar(select(ApprovalRequest).where(ApprovalRequest.approval_type == "SELECT_CONCEPT"))
    assert request is not None and request.status == "PENDING"
    with pytest.raises(ControlPlaneError) as specialist:
        decide_approval(session, request.id, "APPROVED", actor="CREATIVE_DIRECTOR", concept_id=concepts[0].id)
    assert specialist.value.code == "SELF_APPROVAL"
    assert request.status == "PENDING"
    decide_approval(session, request.id, "APPROVED", actor="operator", concept_id=concepts[0].id)
    session.refresh(run)
    assert run.status == "WAITING_SPECIALIST"
    assert concepts[0].status == "SELECTED"
    story_assignment = _waiting_assignment(session)
    import_manual_response(
        session,
        story_assignment.id,
        _story(),
        provider_name="openai",
        model_name="gpt-5",
    )
    audit = session.scalar(select(StoryAuditRecord))
    assert audit is not None
    assert audit.record_status == "MODEL_DIAGNOSIS"
    session.refresh(creative)
    assert creative.current_approved_story_lock_version_id == pointer
    session.refresh(run)
    assert run.status == "WAITING_HUMAN"
    story_request = session.scalar(
        select(ApprovalRequest).where(ApprovalRequest.approval_type == "APPROVE_STORYLOCK")
    )
    assert story_request is not None
    assert story_request.subject_id == proposed.id
    decide_approval(session, story_request.id, "APPROVED", actor="operator", notes="human")
    session.refresh(creative)
    assert creative.current_approved_story_lock_version_id == proposed.id
    session.refresh(run)
    assert run.status == "BLOCKED"
    view = workflow_run_view(session, run.id)
    assert view["memory"]["outcome"] == "BLOCKED_MISSING_REFERENCE"
    readiness = _step(session, run.id, "reference_readiness")
    assert readiness.error_code == "BLOCKED_MISSING_REFERENCE"
    assert any(gap["surface_type"] == "missing-checkout-surface" for gap in readiness.output_refs["gaps"])
    session.add(
        Asset(
            creative_id=creative.id,
            name="missing-checkout-surface applied dark",
            role="REFERENCE",
            rights_status="OWNED",
            original_path="tests/missing-checkout-surface.png",
            ecosystem_code="DOORDASH",
            product_model="dashpass-test",
            notes="applied dark",
            created_at=utcnow(),
            present_in_snapshot=False,
            stale=False,
            staleness_state="CURRENT",
        )
    )
    session.flush()
    recheck_reference_readiness(session, run.id)
    session.refresh(run)
    assert run.status == "COMPLETED"
    assert run.memory["outcome"] == "READY_FOR_PRODUCTION"
    assert session.scalar(select(func.count()).select_from(ProviderInvocation)) == invocations
    history = workflow_history(session, run.id)
    assert len(history) > 8
    assert any(event["to_status"] == "WAITING_HUMAN" for event in history)
    assert any(event["to_status"] == "WAITING_EXTERNAL_RESPONSE" for event in history)
    specialists = list(session.scalars(select(Specialist)))
    assert {row.role for row in specialists} == {
        "CREATIVE_DIRECTOR",
        "CREATIVE_QA",
        "ENGINEERING",
        "RESEARCH",
        "OPERATIONS",
    }
    assert all(row.authoritative is False for row in specialists)


def test_reference_readiness_does_not_invent_gaps(session: Session) -> None:
    assert assess_reference_readiness(session, [])["status"] == "READY"
    report = assess_reference_readiness(session, [REQUIREMENT])
    assert report["status"] == "BLOCKED_MISSING_REFERENCE"
    assert report["gaps"] == [
        {
            "ecosystem": "DOORDASH",
            "surface_type": "missing-checkout-surface",
            "state": "applied",
            "mode": "dark",
            "product": "dashpass-test",
            "required_role": "REFERENCE",
            "reason": "checkout proof for this creative",
        }
    ]


def test_external_completion_is_not_verification(session: Session) -> None:
    granted = create_action_authorization(
        session,
        action_type="RUN_GEELARK_WORKFLOW",
        subject_type="workflow",
        subject_id="none",
        payload_hash=sha256_text("geelark"),
        requested_by="specialist:OPERATIONS",
    )
    with pytest.raises(ControlPlaneError) as blocked:
        decide_action_authorization(session, granted.id, "APPROVED", actor="specialist:OPERATIONS")
    assert blocked.value.code == "SELF_APPROVAL"
    decide_action_authorization(session, granted.id, "APPROVED", actor="operator")
    with pytest.raises(ControlPlaneError) as disabled:
        execute_authorized_action(session, granted.id)
    assert disabled.value.code == "DISABLED"
    with pytest.raises(ControlPlaneError):
        request_external_execution(session, action_type="RUN_GEELARK_WORKFLOW", authorization_id=granted.id)
    execution = request_external_execution(session, action_type="MODEL_RUN")
    mark_external_status(session, execution.id, "ACCEPTED")
    mark_external_status(session, execution.id, "RUNNING")
    mark_external_status(session, execution.id, "REPORTED_COMPLETE")
    session.refresh(execution)
    assert execution.status == "REPORTED_COMPLETE"
    assert session.scalar(select(func.count()).select_from(VerificationResult)) == 0
    with pytest.raises(ControlPlaneError) as separate:
        mark_external_status(session, execution.id, "VERIFIED")
    assert separate.value.code == "INVALID_STATUS"
    record_verification(session, execution.id, "VERIFIED", notes="a person checked the outcome")
    session.refresh(execution)
    assert execution.status == "VERIFIED"
    verified = session.scalar(
        select(VerificationResult).where(VerificationResult.external_execution_id == execution.id)
    )
    assert verified is not None


def test_mcp_cannot_bypass_approval_or_expose_prohibited_tools(session: Session) -> None:
    program = Program(slug="desk", name="Desk", created_at=utcnow())
    session.add(program)
    session.flush()
    created = invoke(
        session,
        "create_work_order",
        {"goal": "Draft a creative", "program_id": program.id, "requested_by": "mcp"},
        caller="mcp-test",
    )
    assert created["status"] == "READY"
    audit = session.scalar(select(McpAuditLog).where(McpAuditLog.operation == "create_work_order"))
    assert audit is not None
    assert audit.caller == "mcp-test"
    assert audit.interface == "MCP"
    assert audit.affected_records[0]["id"] == created["id"]
    with pytest.raises(ControlPlaneError) as prohibited:
        invoke(session, "bypass_approval", {"work_order_id": created["id"]})
    assert prohibited.value.code == "PROHIBITED"
    with pytest.raises(ControlPlaneError) as approved:
        invoke(
            session,
            "request_approval",
            {
                "approval_type": "APPROVE_POST",
                "subject_type": "post",
                "subject_id": "post-1",
                "subject_hash": "abc",
                "status": "APPROVED",
            },
        )
    assert approved.value.code == "SELF_APPROVAL"
    pending = invoke(
        session,
        "request_approval",
        {
            "approval_type": "APPROVE_POST",
            "subject_type": "post",
            "subject_id": "post-1",
            "subject_hash": "abc",
            "requested_by": "specialist:CREATIVE_DIRECTOR",
        },
    )
    assert pending["status"] == "PENDING"
    request = session.get(ApprovalRequest, pending["id"])
    assert request is not None and request.decided_by is None
    with pytest.raises(ControlPlaneError):
        decide_approval(session, request.id, "APPROVED", actor="specialist:CREATIVE_DIRECTOR")
    exposed = READ_TOOLS | MUTATION_TOOLS
    assert exposed.isdisjoint(PROHIBITED_TOOLS)
    for name in ("execute_sql", "shell", "mutate_story_lock", "geelark", "purchase", "post_content"):
        assert name not in exposed
    status = company_status(session)
    assert status["calculated_by"] == "control_plane"
    assert status["recommended_next_action"]["action"] == "DECIDE_APPROVAL"


def test_repo_has_no_openclaw_or_geelark_adapter() -> None:
    root = Path(repo_root())
    names = [path.name.casefold() for path in root.rglob("*") if "node_modules" not in path.parts]
    assert not any("openclaw" in name for name in names)
    assert not any("geelark" in name for name in names)
    pyproject = (root / "pyproject.toml").read_text()
    assert "openclaw" not in pyproject.casefold()
    assert "geelark" not in pyproject.casefold()


def test_registry_is_not_authoritative_state(session: Session) -> None:
    rows = ensure_registry(session)
    assert rows
    assert all(row.authoritative is False for row in rows)
    order = create_work_order(session, goal="A goal", program_id=_program(session).id)
    assert isinstance(order, WorkOrder)
    assert order.task_ids == []


def _program(session: Session) -> Program:
    program = Program(slug="solo", name="Solo", created_at=utcnow())
    session.add(program)
    session.flush()
    return program


def test_definition_version_row_is_immutable_in_the_run(session: Session) -> None:
    creative = _creative(session)
    order = create_work_order(
        session,
        goal="Inspect the frozen graph.",
        program_id=creative.program_id,
        creative_id=creative.id,
    )
    run = start_workflow(session, order.id)
    version = session.get(WorkflowDefinitionVersion, run.definition_version_id)
    assert version is not None
    assert [step["node_id"] for step in workflow_run_view(session, run.id)["steps"]] == [
        node["id"] for node in NEW_CREATIVE_V1
    ]
    version.graph = [{"id": "rogue", "kind": "EXTERNAL_EXECUTION", "config": {}}]
    with pytest.raises(ImmutableVersionError):
        session.flush()
    session.rollback()
