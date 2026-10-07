"""Deterministic company orchestration. Creative OS remains the system of record."""

import json
from datetime import timedelta
from typing import Any

from pydantic import BaseModel, ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from creative_os.config import get_settings
from creative_os.models import (
    Account,
    Asset,
    ConceptBatch,
    ConceptCandidate,
    ContextBundle,
    Creative,
    CreativeTask,
    ModelRun,
    Program,
    StoryAuditRecord,
    StoryLock,
    StoryLockVersion,
)
from creative_os.models.company import (
    ActionAuthorization,
    ApprovalRequest,
    EvidenceRecord,
    ExternalExecution,
    Specialist,
    SpecialistAssignment,
    StepRun,
    VerificationResult,
    WorkflowDefinition,
    WorkflowDefinitionVersion,
    WorkflowEvent,
    WorkflowRun,
    WorkOrder,
)
from creative_os.schemas.contracts import ConceptGenerationResult, StoryDevelopmentAuditResult
from creative_os.services.canonical import stable_digest
from creative_os.services.concepts import decide_concept, link_selected_concept
from creative_os.services.context_bundles import create_context_bundle
from creative_os.services.provider_packet import packet_document
from creative_os.services.scope import ContextScope, ScopeError, validate_scope
from creative_os.services.story_locks import decide_story_lock_version
from creative_os.services.tasks import create_creative_task, creative_for_task
from creative_os.services.text_reasoning import _store_audit, _store_concepts
from creative_os.util import sha256_text, utcnow

NODE_KINDS = frozenset(
    {
        "CREATE_CREATIVE_TASK",
        "COMPILE_CONTEXT",
        "SPECIALIST_REASONING",
        "IMPORT_SPECIALIST_RESULT",
        "DIVERSITY_CHECK",
        "HUMAN_CONCEPT_SELECTION",
        "STORY_DEVELOPMENT",
        "STORY_QA",
        "HUMAN_STORY_APPROVAL",
        "PRODUCTION_ROUTING",
        "REFERENCE_READINESS",
        "PRODUCTION",
        "PRODUCTION_QA",
        "POST_APPROVAL",
        "EXTERNAL_EXECUTION",
        "VERIFICATION",
    }
)
DISABLED_KINDS = frozenset(
    {"PRODUCTION", "PRODUCTION_QA", "POST_APPROVAL", "EXTERNAL_EXECUTION", "VERIFICATION"}
)
SPECIALIST_ROLES = (
    {
        "role": "CREATIVE_DIRECTOR",
        "capabilities": ["CONCEPT_GENERATION", "STORY_DEVELOPMENT", "STORY_QA"],
        "transports": ["MANUAL_SUBSCRIPTION", "API", "MCP"],
    },
    {
        "role": "CREATIVE_QA",
        "capabilities": ["STORY_QA", "PRODUCTION_QA"],
        "transports": ["MANUAL_SUBSCRIPTION", "API", "MCP"],
    },
    {
        "role": "ENGINEERING",
        "capabilities": ["DIAGNOSIS"],
        "transports": ["MANUAL_SUBSCRIPTION", "MCP"],
    },
    {
        "role": "RESEARCH",
        "capabilities": ["RESEARCH"],
        "transports": ["MANUAL_SUBSCRIPTION", "MCP", "EXTERNAL_SYSTEM"],
    },
    {
        "role": "OPERATIONS",
        "capabilities": ["EXTERNAL_EXECUTION"],
        "transports": ["MANUAL_SUBSCRIPTION", "MCP", "EXTERNAL_SYSTEM"],
    },
)
NEW_CREATIVE_V1: list[dict[str, Any]] = [
    {
        "id": "create_concept_task",
        "kind": "CREATE_CREATIVE_TASK",
        "config": {"stage": "CONCEPT_GENERATION"},
    },
    {
        "id": "compile_concept_context",
        "kind": "COMPILE_CONTEXT",
        "config": {"stage": "CONCEPT_GENERATION"},
    },
    {
        "id": "concept_director",
        "kind": "SPECIALIST_REASONING",
        "config": {
            "role": "CREATIVE_DIRECTOR",
            "transport": "MANUAL_SUBSCRIPTION",
            "contract": "ConceptGenerationResult",
            "capability": "CONCEPT_GENERATION",
        },
    },
    {
        "id": "import_concepts",
        "kind": "IMPORT_SPECIALIST_RESULT",
        "config": {"contract": "ConceptGenerationResult"},
    },
    {"id": "diversity", "kind": "DIVERSITY_CHECK", "config": {}},
    {
        "id": "select_concept",
        "kind": "HUMAN_CONCEPT_SELECTION",
        "config": {"approval_type": "SELECT_CONCEPT"},
    },
    {"id": "story_development", "kind": "STORY_DEVELOPMENT", "config": {"stage": "STORY_DEVELOPMENT"}},
    {"id": "compile_story_context", "kind": "COMPILE_CONTEXT", "config": {"stage": "STORY_DEVELOPMENT"}},
    {
        "id": "story_director",
        "kind": "SPECIALIST_REASONING",
        "config": {
            "role": "CREATIVE_DIRECTOR",
            "transport": "MANUAL_SUBSCRIPTION",
            "contract": "StoryDevelopmentAuditResult",
            "capability": "STORY_DEVELOPMENT",
        },
    },
    {
        "id": "import_story",
        "kind": "IMPORT_SPECIALIST_RESULT",
        "config": {"contract": "StoryDevelopmentAuditResult"},
    },
    {"id": "story_qa", "kind": "STORY_QA", "config": {}},
    {
        "id": "approve_story",
        "kind": "HUMAN_STORY_APPROVAL",
        "config": {"approval_type": "APPROVE_STORYLOCK"},
    },
    {"id": "production_routing", "kind": "PRODUCTION_ROUTING", "config": {}},
    {"id": "reference_readiness", "kind": "REFERENCE_READINESS", "config": {}},
]
STEP_EDGES: dict[str, set[str]] = {
    "PENDING": {"READY", "RUNNING", "WAITING_EXTERNAL_RESPONSE", "WAITING_HUMAN", "BLOCKED", "CANCELLED"},
    "READY": {"RUNNING", "WAITING_EXTERNAL_RESPONSE", "WAITING_HUMAN", "BLOCKED", "CANCELLED"},
    "RUNNING": {
        "SUCCEEDED",
        "FAILED",
        "WAITING_EXTERNAL_RESPONSE",
        "WAITING_HUMAN",
        "BLOCKED",
        "CANCELLED",
    },
    "WAITING_EXTERNAL_RESPONSE": {"RUNNING", "SUCCEEDED", "FAILED", "CANCELLED"},
    "WAITING_HUMAN": {"RUNNING", "SUCCEEDED", "FAILED", "BLOCKED", "CANCELLED"},
    "BLOCKED": {"READY", "RUNNING", "SUCCEEDED", "WAITING_HUMAN", "CANCELLED", "FAILED"},
    "SUCCEEDED": set(),
    "FAILED": set(),
    "CANCELLED": set(),
}
ORDER_EDGES: dict[str, set[str]] = {
    "DRAFT": {"READY", "RUNNING", "CANCELLED"},
    "READY": {"RUNNING", "CANCELLED", "DRAFT"},
    "RUNNING": {"WAITING_SPECIALIST", "WAITING_HUMAN", "BLOCKED", "COMPLETED", "CANCELLED"},
    "WAITING_SPECIALIST": {"RUNNING", "WAITING_HUMAN", "BLOCKED", "CANCELLED"},
    "WAITING_HUMAN": {"RUNNING", "WAITING_SPECIALIST", "BLOCKED", "COMPLETED", "CANCELLED"},
    "BLOCKED": {"RUNNING", "WAITING_HUMAN", "WAITING_SPECIALIST", "COMPLETED", "CANCELLED"},
    "COMPLETED": set(),
    "CANCELLED": set(),
}
APPROVAL_TYPES = frozenset(
    {
        "SELECT_CONCEPT",
        "APPROVE_STORYLOCK",
        "APPROVE_PRODUCTION",
        "APPROVE_POST",
        "AUTHORIZE_EXTERNAL_ACTION",
    }
)
ACTION_TYPES = frozenset({"MODEL_RUN", "POST_CONTENT", "RUN_GEELARK_WORKFLOW", "START_DEVICE"})
EXECUTABLE_ACTIONS = frozenset({"MODEL_RUN"})
EXECUTION_STATES = (
    "REQUESTED",
    "ACCEPTED",
    "RUNNING",
    "REPORTED_COMPLETE",
    "VERIFIED",
    "VERIFICATION_FAILED",
    "UNKNOWN_OUTCOME",
)
CONTRACTS: dict[str, type[BaseModel]] = {
    "ConceptGenerationResult": ConceptGenerationResult,
    "StoryDevelopmentAuditResult": StoryDevelopmentAuditResult,
}


class ControlPlaneError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def create_work_order(
    session: Session,
    *,
    goal: str,
    program_id: str,
    requested_by: str | None = None,
    account_id: str | None = None,
    campaign_id: str | None = None,
    creative_id: str | None = None,
    priority: str = "NORMAL",
    notes: str | None = None,
    reference_requirements: list[dict[str, Any]] | None = None,
    status: str = "READY",
) -> WorkOrder:
    if not goal.strip():
        raise ControlPlaneError("GOAL_REQUIRED", "a work order requires a goal")
    if status not in {"DRAFT", "READY"}:
        raise ControlPlaneError("INVALID_STATUS", "a new work order starts as DRAFT or READY")
    try:
        scope = validate_scope(
            session,
            ContextScope(
                program_id=program_id,
                account_id=account_id,
                campaign_id=campaign_id,
                creative_id=creative_id,
            ),
        )
    except ScopeError as exc:
        raise ControlPlaneError("SCOPE", str(exc)) from exc
    now = utcnow()
    order = WorkOrder(
        goal=goal.strip(),
        program_id=scope.program_id or program_id,
        account_id=scope.account_id,
        campaign_id=scope.campaign_id,
        creative_id=scope.creative_id,
        priority=priority.strip().upper() or "NORMAL",
        requested_by=requested_by or get_settings().operator_identity,
        created_at=now,
        updated_at=now,
        status=status,
        notes=notes,
        task_ids=[],
        reference_requirements=list(reference_requirements or []),
    )
    session.add(order)
    session.flush()
    return order


def ensure_registry(session: Session) -> list[Specialist]:
    rows: list[Specialist] = []
    for spec in SPECIALIST_ROLES:
        row = session.scalar(select(Specialist).where(Specialist.role == spec["role"]))
        if row is None:
            row = Specialist(
                role=str(spec["role"]),
                capabilities=list(spec["capabilities"]),
                transports=list(spec["transports"]),
                authoritative=False,
                created_at=utcnow(),
            )
            session.add(row)
            session.flush()
        rows.append(row)
    return rows


def ensure_new_creative_v1(session: Session) -> WorkflowDefinitionVersion:
    for node in NEW_CREATIVE_V1:
        if node["kind"] not in NODE_KINDS:
            raise ControlPlaneError("UNKNOWN_NODE", f"node kind {node['kind']} is not in the catalog")
    definition = session.scalar(select(WorkflowDefinition).where(WorkflowDefinition.key == "NEW_CREATIVE_V1"))
    if definition is None:
        definition = WorkflowDefinition(
            key="NEW_CREATIVE_V1",
            name="New creative",
            created_at=utcnow(),
        )
        session.add(definition)
        session.flush()
    current = session.scalar(
        select(WorkflowDefinitionVersion)
        .where(WorkflowDefinitionVersion.definition_id == definition.id)
        .order_by(WorkflowDefinitionVersion.version_number.desc())
        .limit(1)
    )
    if current is not None:
        return current
    graph = [dict(node) for node in NEW_CREATIVE_V1]
    version = WorkflowDefinitionVersion(
        definition_id=definition.id,
        version_number=1,
        graph=graph,
        graph_hash=stable_digest({"nodes": graph}),
        created_at=utcnow(),
    )
    session.add(version)
    session.flush()
    return version


def start_workflow(
    session: Session,
    work_order_id: str,
    *,
    definition_key: str = "NEW_CREATIVE_V1",
    actor: str | None = None,
) -> WorkflowRun:
    if definition_key != "NEW_CREATIVE_V1":
        raise ControlPlaneError("UNKNOWN_WORKFLOW", "v0.4 publishes only NEW_CREATIVE_V1")
    order = _order(session, work_order_id)
    if order.status not in {"DRAFT", "READY"}:
        raise ControlPlaneError("WORK_ORDER_BUSY", f"work order is {order.status}")
    version = ensure_new_creative_v1(session)
    ensure_registry(session)
    now = utcnow()
    run = WorkflowRun(
        work_order_id=order.id,
        definition_version_id=version.id,
        status="RUNNING",
        memory={},
        created_at=now,
        updated_at=now,
    )
    session.add(run)
    session.flush()
    for index, node in enumerate(version.graph):
        if not isinstance(node, dict) or node.get("kind") not in NODE_KINDS:
            raise ControlPlaneError("INVALID_GRAPH", "stored graph contains a node outside the catalog")
        config = dict(node.get("config") or {})
        step = StepRun(
            workflow_run_id=run.id,
            position=index,
            node_id=str(node["id"]),
            node_kind=str(node["kind"]),
            input_refs={"config": config},
            output_refs={},
            status="PENDING",
            specialist_role=config.get("role"),
            capability=config.get("capability"),
            attempt=0,
            evidence_ids=[],
        )
        session.add(step)
    session.flush()
    _move_order(session, order, run, "RUNNING", actor or get_settings().operator_identity, "workflow started")
    advance(session, run.id, actor=actor)
    session.refresh(run)
    return run


def resume_step(session: Session, step_run_id: str, *, actor: str | None = None) -> WorkflowRun:
    step = session.get(StepRun, step_run_id)
    if step is None:
        raise ControlPlaneError("STEP_NOT_FOUND", "step does not exist")
    steps = _steps(session, step.workflow_run_id)
    if any(earlier.status != "SUCCEEDED" for earlier in steps if earlier.position < step.position):
        raise ControlPlaneError("SKIP_FORBIDDEN", "a later step cannot run before earlier steps succeed")
    return advance(session, step.workflow_run_id, actor=actor)


def advance(session: Session, workflow_run_id: str, *, actor: str | None = None) -> WorkflowRun:
    run = _run(session, workflow_run_id)
    actor_name = actor or get_settings().operator_identity
    steps = _steps(session, run.id)
    for index, step in enumerate(steps):
        if step.status == "SUCCEEDED":
            continue
        if any(earlier.status != "SUCCEEDED" for earlier in steps[:index]):
            raise ControlPlaneError("SKIP_FORBIDDEN", "a later step cannot run before earlier steps succeed")
        if step.status in {"WAITING_EXTERNAL_RESPONSE", "WAITING_HUMAN", "BLOCKED", "FAILED", "CANCELLED"}:
            break
        _execute(session, run, step, steps, actor_name)
        if step.status != "SUCCEEDED":
            break
    _sync(session, run, actor_name)
    return run


def import_manual_response(
    session: Session,
    assignment_id: str,
    raw_response: str,
    *,
    provider_name: str,
    model_name: str,
    actor: str | None = None,
) -> SpecialistAssignment:
    """Record an operator-pasted specialist response. This function does not open a socket."""
    assignment = session.get(SpecialistAssignment, assignment_id)
    if assignment is None:
        raise ControlPlaneError("ASSIGNMENT_NOT_FOUND", "specialist assignment does not exist")
    if assignment.transport != "MANUAL_SUBSCRIPTION":
        raise ControlPlaneError("TRANSPORT_MISMATCH", "manual import is only for MANUAL_SUBSCRIPTION")
    if assignment.status != "WAITING_EXTERNAL_RESPONSE":
        raise ControlPlaneError("ASSIGNMENT_CLOSED", f"assignment is {assignment.status}")
    if not provider_name.strip() or not model_name.strip():
        raise ControlPlaneError("PROVIDER_REQUIRED", "declare the provider and model used outside Creative OS")
    step = session.get(StepRun, assignment.step_run_id)
    if step is None:
        raise ControlPlaneError("STEP_NOT_FOUND", "assignment step does not exist")
    run = _run(session, step.workflow_run_id)
    actor_name = actor or get_settings().operator_identity
    step.attempt = step.attempt + 1
    assignment.provider_name = provider_name.strip()
    assignment.model_name = model_name.strip()
    assignment.api_verified = False
    assignment.raw_response = raw_response
    assignment.imported_at = utcnow()
    try:
        payload = json.loads(raw_response)
        model = CONTRACTS[assignment.contract_name].model_validate(payload)
    except (json.JSONDecodeError, ValidationError, KeyError) as exc:
        assignment.validation_status = "INVALID"
        assignment.parsed_response = None
        assignment.error_detail = str(exc)
        session.flush()
        _event(session, run.id, step.id, step.status, step.status, actor_name, "invalid manual response")
        return assignment
    bundle = session.get(ContextBundle, assignment.context_bundle_id) if assignment.context_bundle_id else None
    if bundle is None:
        raise ControlPlaneError("BUNDLE_MISSING", "manual import requires the frozen context bundle")
    parsed = model.model_dump(mode="json")
    model_run = _manual_run(session, bundle, assignment, raw_response, parsed)
    before = _approved_pointer(session, run)
    if isinstance(model, ConceptGenerationResult):
        _store_concepts(session, bundle, model_run, model)
        batch_id = (model_run.output_refs or {}).get("concept_batch_id")
        assignment.result_refs = dict(model_run.output_refs or {})
        _remember(run, "concept_batch_id", batch_id)
        _remember(run, "concept_ids", (model_run.output_refs or {}).get("concept_ids") or [])
    elif isinstance(model, StoryDevelopmentAuditResult):
        _store_audit(session, bundle, model_run, model)
        assignment.result_refs = dict(model_run.output_refs or {})
        _remember(run, "story_audit_id", (model_run.output_refs or {}).get("story_audit_record_id"))
    else:
        raise ControlPlaneError("UNKNOWN_CONTRACT", "manual response did not match a known contract")
    after = _approved_pointer(session, run)
    if after != before:
        raise ControlPlaneError("POINTER_MOVED", "a specialist import must not move an approval pointer")
    assignment.parsed_response = parsed
    assignment.validation_status = "VALID"
    assignment.status = "SUCCEEDED"
    assignment.error_detail = None
    _evidence(
        session,
        run,
        step,
        evidence_type="MANUAL_RESPONSE",
        source=f"{assignment.transport}:{provider_name}",
        subject_type="specialist_assignment",
        subject_id=assignment.id,
        content_hash=sha256_text(raw_response),
        claims=["proposal"],
        verification_state="UNVERIFIED",
    )
    _set_step(session, step, "SUCCEEDED", actor_name, "valid manual response imported")
    step.output_refs = {
        "assignment_id": assignment.id,
        "validation_status": "VALID",
        "api_verified": False,
        **assignment.result_refs,
    }
    advance(session, run.id, actor=actor_name)
    session.refresh(assignment)
    return assignment


def decide_approval(
    session: Session,
    request_id: str,
    decision: str,
    *,
    actor: str,
    concept_id: str | None = None,
    notes: str | None = None,
) -> ApprovalRequest:
    request = session.get(ApprovalRequest, request_id)
    if request is None:
        raise ControlPlaneError("APPROVAL_NOT_FOUND", "approval request does not exist")
    _reject_specialist_actor(actor)
    operator = get_settings().operator_identity
    if actor != operator:
        raise ControlPlaneError("OPERATOR_REQUIRED", "only the human operator can decide an approval")
    if request.requested_by == actor and request.requested_by.startswith("specialist:"):
        raise ControlPlaneError("SELF_APPROVAL", "a specialist cannot approve its own request")
    choice = decision.strip().upper()
    if choice not in {"APPROVED", "REJECTED", "NEEDS_CHANGES", "CANCELLED"}:
        raise ControlPlaneError(
            "INVALID_DECISION",
            "decision must be APPROVED, REJECTED, NEEDS_CHANGES, or CANCELLED",
        )
    if request.status != "PENDING":
        raise ControlPlaneError("APPROVAL_CLOSED", f"approval request is {request.status}")
    if choice == "APPROVED" and request.approval_type == "SELECT_CONCEPT":
        _select_concept(session, request, concept_id, actor, notes)
    elif choice == "APPROVED" and request.approval_type == "APPROVE_STORYLOCK":
        _approve_story(session, request, actor, notes)
    elif choice == "APPROVED" and request.approval_type in {
        "APPROVE_PRODUCTION",
        "APPROVE_POST",
        "AUTHORIZE_EXTERNAL_ACTION",
    }:
        raise ControlPlaneError("NOT_ENABLED", f"{request.approval_type} cannot be executed in v0.4")
    request.status = choice if choice != "APPROVED" else "APPROVED"
    request.decided_by = actor
    request.decided_at = utcnow()
    request.notes = notes
    session.flush()
    if request.step_run_id and request.workflow_run_id:
        step = session.get(StepRun, request.step_run_id)
        run = _run(session, request.workflow_run_id)
        if step is not None and choice == "APPROVED":
            _set_step(session, step, "SUCCEEDED", actor, f"{request.approval_type} approved")
            step.output_refs = {
                "approval_request_id": request.id,
                "subject_type": request.subject_type,
                "subject_id": request.subject_id,
                "subject_hash": request.subject_hash,
            }
            advance(session, run.id, actor=actor)
        elif step is not None and choice in {"REJECTED", "CANCELLED"}:
            _set_step(session, step, "FAILED", actor, choice)
            _sync(session, run, actor)
        elif step is not None:
            _event(session, run.id, step.id, step.status, step.status, actor, "needs changes")
    return request


def request_approval(
    session: Session,
    *,
    approval_type: str,
    subject_type: str,
    subject_id: str,
    subject_hash: str,
    requested_by: str,
    workflow_run_id: str | None = None,
    step_run_id: str | None = None,
    payload: dict[str, Any] | None = None,
) -> ApprovalRequest:
    if approval_type not in APPROVAL_TYPES:
        raise ControlPlaneError("UNKNOWN_APPROVAL", f"unknown approval type {approval_type}")
    if not subject_hash:
        raise ControlPlaneError("HASH_REQUIRED", "an approval binds the exact subject hash")
    request = ApprovalRequest(
        approval_type=approval_type,
        subject_type=subject_type,
        subject_id=subject_id,
        subject_hash=subject_hash,
        status="PENDING",
        requested_by=requested_by,
        workflow_run_id=workflow_run_id,
        step_run_id=step_run_id,
        payload=payload or {},
        created_at=utcnow(),
    )
    session.add(request)
    session.flush()
    return request


def create_manual_assignment_for_step(session: Session, step_run_id: str) -> SpecialistAssignment:
    step = session.get(StepRun, step_run_id)
    if step is None or step.node_kind != "SPECIALIST_REASONING":
        raise ControlPlaneError("STEP_MISMATCH", "manual assignment requires a specialist step")
    existing = session.scalar(select(SpecialistAssignment).where(SpecialistAssignment.step_run_id == step.id))
    if existing is not None:
        return existing
    run = _run(session, step.workflow_run_id)
    if step.status == "PENDING":
        advance(session, run.id)
        session.refresh(step)
    existing = session.scalar(select(SpecialistAssignment).where(SpecialistAssignment.step_run_id == step.id))
    if existing is None:
        raise ControlPlaneError("ASSIGNMENT_UNAVAILABLE", "the specialist step is not ready for assignment")
    return existing


def compile_context_for_step(session: Session, step_run_id: str) -> dict[str, Any]:
    step = session.get(StepRun, step_run_id)
    if step is None or step.node_kind != "COMPILE_CONTEXT":
        raise ControlPlaneError("STEP_MISMATCH", "context compilation requires a compile step")
    if step.output_refs.get("context_bundle_id"):
        return dict(step.output_refs)
    run = _run(session, step.workflow_run_id)
    advance(session, run.id)
    session.refresh(step)
    if not step.output_refs.get("context_bundle_id"):
        raise ControlPlaneError("CONTEXT_NOT_READY", "the compile step did not produce a bundle")
    return dict(step.output_refs)


def assess_reference_readiness(session: Session, requirements: list[dict[str, Any]]) -> dict[str, Any]:
    gaps: list[dict[str, Any]] = []
    matched: list[dict[str, str]] = []
    assets = list(session.scalars(select(Asset)))
    for requirement in requirements:
        if not isinstance(requirement, dict):
            raise ControlPlaneError("INVALID_REQUIREMENT", "a reference requirement must be an object")
        asset = _matching_asset(assets, requirement)
        if asset is None:
            gaps.append(
                {
                    "ecosystem": requirement.get("ecosystem"),
                    "surface_type": requirement.get("surface_type"),
                    "state": requirement.get("state"),
                    "mode": requirement.get("mode"),
                    "product": requirement.get("product"),
                    "required_role": requirement.get("required_role"),
                    "reason": requirement.get("reason") or "declared requirement has no matching asset",
                }
            )
        else:
            matched.append(
                {
                    "requirement": str(requirement.get("surface_type") or requirement),
                    "asset_id": asset.id,
                }
            )
    status = "BLOCKED_MISSING_REFERENCE" if gaps else "READY"
    return {"status": status, "gaps": gaps, "matched": matched, "declared_count": len(requirements)}


def recheck_reference_readiness(
    session: Session, workflow_run_id: str, *, actor: str | None = None
) -> WorkflowRun:
    run = _run(session, workflow_run_id)
    step = next((item for item in _steps(session, run.id) if item.node_kind == "REFERENCE_READINESS"), None)
    if step is None or step.status != "BLOCKED":
        raise ControlPlaneError("NOT_BLOCKED", "reference readiness is not blocked")
    order = _order(session, run.work_order_id)
    report = assess_reference_readiness(session, list(order.reference_requirements or []))
    actor_name = actor or get_settings().operator_identity
    step.output_refs = report
    _remember(run, "readiness", report)
    if report["status"] == "READY":
        _set_step(session, step, "SUCCEEDED", actor_name, "declared references are present")
        _remember(run, "outcome", "READY_FOR_PRODUCTION")
        _sync(session, run, actor_name)
    else:
        step.error_code = "BLOCKED_MISSING_REFERENCE"
        step.error_detail = json.dumps(report["gaps"])
        session.flush()
    return run


def create_action_authorization(
    session: Session,
    *,
    action_type: str,
    subject_type: str,
    subject_id: str,
    payload_hash: str,
    requested_by: str,
    target: str | None = None,
    limits: dict[str, Any] | None = None,
    expires_in_hours: int = 24,
    notes: str | None = None,
) -> ActionAuthorization:
    if action_type not in ACTION_TYPES:
        raise ControlPlaneError("UNKNOWN_ACTION", f"unknown action type {action_type}")
    if not payload_hash:
        raise ControlPlaneError("HASH_REQUIRED", "an action authorization freezes the payload hash")
    row = ActionAuthorization(
        action_type=action_type,
        subject_type=subject_type,
        subject_id=subject_id,
        payload_hash=payload_hash,
        target=target,
        limits=limits or {},
        requested_by=requested_by,
        authorizer=None,
        expires_at=utcnow() + timedelta(hours=expires_in_hours),
        status="PENDING",
        notes=notes,
        created_at=utcnow(),
    )
    session.add(row)
    session.flush()
    return row


def decide_action_authorization(
    session: Session, authorization_id: str, decision: str, *, actor: str
) -> ActionAuthorization:
    row = session.get(ActionAuthorization, authorization_id)
    if row is None:
        raise ControlPlaneError("AUTHORIZATION_NOT_FOUND", "action authorization does not exist")
    _reject_specialist_actor(actor)
    if actor != get_settings().operator_identity:
        raise ControlPlaneError("OPERATOR_REQUIRED", "only the human operator can authorize an action")
    if row.requested_by == actor and row.requested_by.startswith("specialist:"):
        raise ControlPlaneError("SELF_APPROVAL", "a specialist cannot authorize its own action")
    choice = decision.strip().upper()
    if row.status != "PENDING":
        raise ControlPlaneError("AUTHORIZATION_CLOSED", f"authorization is {row.status}")
    if choice == "APPROVED":
        row.status = "APPROVED"
        row.authorizer = actor
    elif choice == "REJECTED":
        row.status = "REJECTED"
        row.authorizer = actor
    else:
        raise ControlPlaneError("INVALID_DECISION", "action decision must be APPROVED or REJECTED")
    session.flush()
    return row


def execute_authorized_action(session: Session, authorization_id: str) -> dict[str, Any]:
    row = session.get(ActionAuthorization, authorization_id)
    if row is None or row.status != "APPROVED":
        raise ControlPlaneError("NOT_AUTHORIZED", "the action is not approved")
    if row.expires_at < utcnow():
        row.status = "EXPIRED"
        session.flush()
        raise ControlPlaneError("EXPIRED", "the action authorization has expired")
    if row.action_type not in EXECUTABLE_ACTIONS:
        raise ControlPlaneError(
            "DISABLED",
            f"{row.action_type} stays disabled. GeeLark, posting, and device control do not run in v0.4",
        )
    return {
        "action_type": row.action_type,
        "authorization_id": row.id,
        "executed_here": False,
        "delegate": "existing_text_reasoning_gate",
    }


def request_external_execution(
    session: Session,
    *,
    action_type: str,
    authorization_id: str | None = None,
    detail: dict[str, Any] | None = None,
) -> ExternalExecution:
    if action_type in {"POST_CONTENT", "RUN_GEELARK_WORKFLOW", "START_DEVICE"}:
        raise ControlPlaneError("DISABLED", f"{action_type} has no adapter in v0.4")
    row = ExternalExecution(
        action_authorization_id=authorization_id,
        action_type=action_type,
        adapter="NONE",
        status="REQUESTED",
        detail=detail or {},
        created_at=utcnow(),
    )
    session.add(row)
    session.flush()
    return row


def mark_external_status(session: Session, execution_id: str, status: str) -> ExternalExecution:
    row = session.get(ExternalExecution, execution_id)
    if row is None:
        raise ControlPlaneError("EXECUTION_NOT_FOUND", "external execution does not exist")
    if status not in {"ACCEPTED", "RUNNING", "REPORTED_COMPLETE", "UNKNOWN_OUTCOME"}:
        raise ControlPlaneError("INVALID_STATUS", "use verification to record VERIFIED or VERIFICATION_FAILED")
    if status == "VERIFIED":
        raise ControlPlaneError("VERIFICATION_SEPARATE", "reported completion is not verification")
    row.status = status
    if status == "REPORTED_COMPLETE":
        row.reported_at = utcnow()
    session.flush()
    return row


def record_verification(
    session: Session, execution_id: str, status: str, *, notes: str | None = None
) -> VerificationResult:
    row = session.get(ExternalExecution, execution_id)
    if row is None:
        raise ControlPlaneError("EXECUTION_NOT_FOUND", "external execution does not exist")
    if status not in {"VERIFIED", "VERIFICATION_FAILED", "UNKNOWN_OUTCOME"}:
        raise ControlPlaneError("INVALID_VERIFICATION", "verification status is not recognized")
    if row.status not in {"REPORTED_COMPLETE", "UNKNOWN_OUTCOME", "VERIFIED", "VERIFICATION_FAILED"}:
        raise ControlPlaneError("NOT_REPORTED", "verification follows a reported outcome")
    result = VerificationResult(
        external_execution_id=row.id,
        status=status,
        notes=notes,
        created_at=utcnow(),
    )
    session.add(result)
    if status == "VERIFIED":
        row.status = "VERIFIED"
    elif status == "VERIFICATION_FAILED":
        row.status = "VERIFICATION_FAILED"
    else:
        row.status = "UNKNOWN_OUTCOME"
    session.flush()
    return result


def company_status(session: Session) -> dict[str, Any]:
    orders = list(session.scalars(select(WorkOrder).order_by(WorkOrder.updated_at.desc())))
    approvals = list(
        session.scalars(
            select(ApprovalRequest)
            .where(ApprovalRequest.status == "PENDING")
            .order_by(ApprovalRequest.created_at.asc())
        )
    )
    assignments = list(
        session.scalars(
            select(SpecialistAssignment).where(SpecialistAssignment.status == "WAITING_EXTERNAL_RESPONSE")
        )
    )
    gaps = reference_gap_queue(session)
    running = [_order_view(order) for order in orders if order.status == "RUNNING"]
    blocked = [_order_view(order) for order in orders if order.status == "BLOCKED"]
    completed = [_order_view(order) for order in orders if order.status == "COMPLETED"][:8]
    recommendation = _recommend(approvals, assignments, gaps, orders)
    return {
        "calculated_by": "control_plane",
        "running": running,
        "blocked": blocked,
        "waiting_on_human": [_approval_view(row) for row in approvals],
        "waiting_on_specialist": [_assignment_view(row) for row in assignments],
        "missing_references": gaps,
        "completed_recently": completed,
        "recommended_next_action": recommendation,
    }


def reference_gap_queue(session: Session) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    steps = session.scalars(select(StepRun).where(StepRun.node_kind == "REFERENCE_READINESS"))
    for step in steps:
        report = step.output_refs or {}
        if report.get("status") == "BLOCKED_MISSING_REFERENCE":
            rows.append(
                {
                    "step_run_id": step.id,
                    "workflow_run_id": step.workflow_run_id,
                    "gaps": report.get("gaps") or [],
                }
            )
    return rows


def workflow_history(session: Session, workflow_run_id: str) -> list[dict[str, Any]]:
    events = session.scalars(
        select(WorkflowEvent)
        .where(WorkflowEvent.workflow_run_id == workflow_run_id)
        .order_by(WorkflowEvent.created_at.asc())
    )
    return [
        {
            "id": event.id,
            "step_run_id": event.step_run_id,
            "from_status": event.from_status,
            "to_status": event.to_status,
            "actor": event.actor,
            "detail": event.detail,
            "created_at": event.created_at.isoformat(),
        }
        for event in events
    ]


def assignment_packet(session: Session, assignment_id: str) -> dict[str, Any]:
    assignment = session.get(SpecialistAssignment, assignment_id)
    if assignment is None or assignment.context_bundle_id is None:
        raise ControlPlaneError("ASSIGNMENT_NOT_FOUND", "assignment packet is unavailable")
    bundle = session.get(ContextBundle, assignment.context_bundle_id)
    if bundle is None:
        raise ControlPlaneError("BUNDLE_MISSING", "frozen bundle is missing")
    contract = CONTRACTS[assignment.contract_name]
    wrapper = (
        "You are a specialist returning a proposal to Creative OS.\n"
        "Creative OS owns state. You do not approve, post, or mutate records.\n"
        f"Return only JSON matching {assignment.contract_name}.\n\n"
        f"{bundle.compiled_text}"
    )
    return {
        "transport": assignment.transport,
        "api_verified": False,
        "assignment_id": assignment.id,
        "bundle_id": bundle.id,
        "bundle_hash": bundle.payload_hash,
        "contract": assignment.contract_name,
        "schema": contract.model_json_schema(),
        "packet": packet_document(bundle),
        "wrapper": wrapper,
    }


def _execute(session: Session, run: WorkflowRun, step: StepRun, steps: list[StepRun], actor: str) -> None:
    if step.node_kind in DISABLED_KINDS:
        raise ControlPlaneError("DISABLED", f"{step.node_kind} is not enabled in v0.4")
    order = _order(session, run.work_order_id)
    _set_step(session, step, "RUNNING", actor, step.node_kind)
    if step.node_kind == "CREATE_CREATIVE_TASK":
        _create_task_step(session, run, step, order, actor)
    elif step.node_kind == "COMPILE_CONTEXT":
        _compile_step(session, run, step, order)
    elif step.node_kind == "SPECIALIST_REASONING":
        _specialist_step(session, run, step, steps, actor)
    elif step.node_kind == "IMPORT_SPECIALIST_RESULT":
        _import_step(session, step, steps)
    elif step.node_kind == "DIVERSITY_CHECK":
        _diversity_step(session, run, step)
    elif step.node_kind == "HUMAN_CONCEPT_SELECTION":
        _concept_gate(session, run, step, order)
    elif step.node_kind == "STORY_DEVELOPMENT":
        _story_task_step(session, run, step, order, actor)
    elif step.node_kind == "STORY_QA":
        _story_qa_step(session, run, step)
    elif step.node_kind == "HUMAN_STORY_APPROVAL":
        _story_gate(session, run, step, order)
    elif step.node_kind == "PRODUCTION_ROUTING":
        _routing_step(session, run, step, order)
    elif step.node_kind == "REFERENCE_READINESS":
        _readiness_step(session, run, step, order, actor)
    else:
        raise ControlPlaneError("UNKNOWN_NODE", f"{step.node_kind} has no executor")


def _create_task_step(session: Session, run: WorkflowRun, step: StepRun, order: WorkOrder, actor: str) -> None:
    stage = str((step.input_refs.get("config") or {}).get("stage") or "CONCEPT_GENERATION")
    task = create_creative_task(
        session,
        program_id=order.program_id,
        account_id=order.account_id,
        campaign_id=order.campaign_id,
        creative_id=order.creative_id,
        stage=stage,
        instruction=order.goal,
        created_by=actor,
        constraints={"work_order_id": order.id},
        input_refs={"work_order_id": order.id},
    )
    order.task_ids = [*list(order.task_ids or []), task.id]
    flag_modified(order, "task_ids")
    _remember(run, "concept_task_id", task.id)
    _finish(session, step, actor, {"creative_task_id": task.id, "stage": stage})


def _compile_step(session: Session, run: WorkflowRun, step: StepRun, order: WorkOrder) -> None:
    stage = str((step.input_refs.get("config") or {}).get("stage") or "")
    if stage == "STORY_DEVELOPMENT":
        task_id = run.memory.get("story_task_id")
    else:
        task_id = run.memory.get("concept_task_id")
    task = session.get(CreativeTask, task_id) if task_id else None
    if task is None:
        raise ControlPlaneError("TASK_MISSING", "context compilation requires the creative task")
    creative = creative_for_task(session, task)
    if creative is None and order.creative_id:
        creative = session.get(Creative, order.creative_id)
    bundle = create_context_bundle(session, creative, task=task)
    key = "story_bundle_id" if stage == "STORY_DEVELOPMENT" else "concept_bundle_id"
    _remember(run, key, bundle.id)
    _evidence(
        session,
        run,
        step,
        evidence_type="CONTEXT_BUNDLE",
        source="creative_os",
        subject_type="context_bundle",
        subject_id=bundle.id,
        content_hash=bundle.payload_hash,
        claims=["frozen_context"],
    )
    _finish(
        session,
        step,
        get_settings().operator_identity,
        {"context_bundle_id": bundle.id, "payload_hash": bundle.payload_hash, "creative_task_id": task.id},
    )


def _specialist_step(
    session: Session, run: WorkflowRun, step: StepRun, steps: list[StepRun], actor: str
) -> None:
    config = dict(step.input_refs.get("config") or {})
    transport = str(config.get("transport") or "MANUAL_SUBSCRIPTION")
    if transport != "MANUAL_SUBSCRIPTION":
        raise ControlPlaneError("TRANSPORT_DISABLED", f"{transport} is not executed in v0.4")
    role = str(config.get("role") or "")
    specialist = session.scalar(select(Specialist).where(Specialist.role == role))
    if specialist is None or specialist.authoritative:
        raise ControlPlaneError("SPECIALIST_INVALID", "specialist is missing or marked authoritative")
    bundle_id = _bundle_for_specialist(run, steps, step)
    bundle = session.get(ContextBundle, bundle_id) if bundle_id else None
    if bundle is None:
        raise ControlPlaneError("BUNDLE_MISSING", "specialist assignment requires a frozen bundle")
    assignment = SpecialistAssignment(
        step_run_id=step.id,
        specialist_role=role,
        transport=transport,
        creative_task_id=bundle.creative_task_id,
        context_bundle_id=bundle.id,
        context_bundle_hash=bundle.payload_hash,
        api_verified=False,
        status="WAITING_EXTERNAL_RESPONSE",
        contract_name=str(config.get("contract")),
        validation_status="PENDING",
        result_refs={},
        created_at=utcnow(),
    )
    session.add(assignment)
    session.flush()
    if assignment.contract_name == "ConceptGenerationResult":
        memory_key = "concept_assignment_id"
    else:
        memory_key = "story_assignment_id"
    _remember(run, memory_key, assignment.id)
    step.output_refs = {"assignment_id": assignment.id, "transport": transport, "api_verified": False}
    _set_step(session, step, "WAITING_EXTERNAL_RESPONSE", actor, "waiting for a manual specialist response")


def _import_step(session: Session, step: StepRun, steps: list[StepRun]) -> None:
    previous = _previous(steps, step, "SPECIALIST_REASONING")
    assignment_id = (previous.output_refs or {}).get("assignment_id") if previous else None
    assignment = session.get(SpecialistAssignment, assignment_id) if assignment_id else None
    if assignment is None or assignment.validation_status != "VALID":
        raise ControlPlaneError("IMPORT_REQUIRED", "a valid specialist response is required")
    _finish(
        session,
        step,
        get_settings().operator_identity,
        {"assignment_id": assignment.id, "result_refs": assignment.result_refs},
    )


def _diversity_step(session: Session, run: WorkflowRun, step: StepRun) -> None:
    batch_id = run.memory.get("concept_batch_id")
    batch = session.get(ConceptBatch, batch_id) if batch_id else None
    if batch is None:
        raise ControlPlaneError("BATCH_MISSING", "diversity check requires the concept batch")
    _evidence(
        session,
        run,
        step,
        evidence_type="CONCEPT_BATCH",
        source="creative_os",
        subject_type="concept_batch",
        subject_id=batch.id,
        content_hash=None,
        claims=["diversity_audit", str(batch.diversity_level or "")],
    )
    _finish(
        session,
        step,
        get_settings().operator_identity,
        {"concept_batch_id": batch.id, "diversity_level": batch.diversity_level, "status": batch.status},
    )


def _concept_gate(session: Session, run: WorkflowRun, step: StepRun, order: WorkOrder) -> None:
    batch_id = str(run.memory.get("concept_batch_id") or "")
    batch = session.get(ConceptBatch, batch_id) if batch_id else None
    if batch is None:
        raise ControlPlaneError("BATCH_MISSING", "concept selection requires a batch")
    concepts = list(session.scalars(select(ConceptCandidate).where(ConceptCandidate.batch_id == batch.id)))
    if any(concept.status != "PROPOSED" for concept in concepts):
        raise ControlPlaneError("CONCEPT_STATE", "concept selection starts from proposed concepts")
    subject_hash = stable_digest({"concept_ids": sorted(concept.id for concept in concepts)})
    request = request_approval(
        session,
        approval_type="SELECT_CONCEPT",
        subject_type="concept_batch",
        subject_id=batch.id,
        subject_hash=subject_hash,
        requested_by="workflow:NEW_CREATIVE_V1",
        workflow_run_id=run.id,
        step_run_id=step.id,
        payload={"concept_ids": [concept.id for concept in concepts], "work_order_id": order.id},
    )
    step.output_refs = {"approval_request_id": request.id, "subject_hash": subject_hash}
    _set_step(session, step, "WAITING_HUMAN", get_settings().operator_identity, "select one concept")


def _story_task_step(session: Session, run: WorkflowRun, step: StepRun, order: WorkOrder, actor: str) -> None:
    concept_id = str(run.memory.get("selected_concept_id") or "")
    concept = session.get(ConceptCandidate, concept_id) if concept_id else None
    if concept is None or concept.status != "SELECTED":
        raise ControlPlaneError("CONCEPT_REQUIRED", "story development requires a human-selected concept")
    task = create_creative_task(
        session,
        program_id=order.program_id,
        account_id=order.account_id,
        campaign_id=order.campaign_id,
        creative_id=order.creative_id,
        stage="STORY_DEVELOPMENT",
        instruction=f"Develop the selected concept: {concept.title}",
        created_by=actor,
        input_refs={"concept_id": concept.id, "work_order_id": order.id},
    )
    order.task_ids = [*list(order.task_ids or []), task.id]
    flag_modified(order, "task_ids")
    _remember(run, "story_task_id", task.id)
    _finish(session, step, actor, {"creative_task_id": task.id, "concept_id": concept.id})


def _story_qa_step(session: Session, run: WorkflowRun, step: StepRun) -> None:
    audit_id = run.memory.get("story_audit_id")
    audit = session.get(StoryAuditRecord, audit_id) if audit_id else None
    if audit is None or audit.record_status != "MODEL_DIAGNOSIS":
        raise ControlPlaneError("AUDIT_REQUIRED", "story QA requires a model diagnosis")
    _evidence(
        session,
        run,
        step,
        evidence_type="STORY_AUDIT",
        source="specialist",
        subject_type="story_audit_record",
        subject_id=audit.id,
        content_hash=None,
        claims=[audit.overall_status],
        verification_state="UNVERIFIED",
    )
    _finish(
        session,
        step,
        get_settings().operator_identity,
        {"story_audit_record_id": audit.id, "record_status": audit.record_status},
    )


def _story_gate(session: Session, run: WorkflowRun, step: StepRun, order: WorkOrder) -> None:
    if not order.creative_id:
        _block(session, step, "NO_PENDING_STORY_LOCK", "story approval requires a creative with a pending lock")
        return
    pending = _pending_lock(session, order.creative_id)
    if pending is None:
        _block(session, step, "NO_PENDING_STORY_LOCK", "no pending story lock version is waiting")
        return
    subject_hash = pending.document_hash or pending.content_hash
    request = request_approval(
        session,
        approval_type="APPROVE_STORYLOCK",
        subject_type="story_lock_version",
        subject_id=pending.id,
        subject_hash=subject_hash,
        requested_by="workflow:NEW_CREATIVE_V1",
        workflow_run_id=run.id,
        step_run_id=step.id,
        payload={"creative_id": order.creative_id},
    )
    step.output_refs = {"approval_request_id": request.id, "subject_hash": subject_hash}
    _set_step(
        session,
        step,
        "WAITING_HUMAN",
        get_settings().operator_identity,
        "approve the pending story lock",
    )


def _routing_step(session: Session, run: WorkflowRun, step: StepRun, order: WorkOrder) -> None:
    _finish(
        session,
        step,
        get_settings().operator_identity,
        {
            "route": "REFERENCE_READINESS",
            "executes_production": False,
            "creative_id": order.creative_id,
        },
    )
    _remember(run, "production_route", "REFERENCE_READINESS")


def _readiness_step(session: Session, run: WorkflowRun, step: StepRun, order: WorkOrder, actor: str) -> None:
    report = assess_reference_readiness(session, list(order.reference_requirements or []))
    step.output_refs = report
    _remember(run, "readiness", report)
    _evidence(
        session,
        run,
        step,
        evidence_type="REFERENCE_ASSESSMENT",
        source="reference_bank",
        subject_type="work_order",
        subject_id=order.id,
        content_hash=stable_digest(report),
        claims=[str(report["status"])],
    )
    if report["status"] == "READY":
        _set_step(session, step, "SUCCEEDED", actor, "READY_FOR_PRODUCTION")
        _remember(run, "outcome", "READY_FOR_PRODUCTION")
    else:
        _block(session, step, "BLOCKED_MISSING_REFERENCE", json.dumps(report["gaps"]))
        _remember(run, "outcome", "BLOCKED_MISSING_REFERENCE")


def _select_concept(
    session: Session,
    request: ApprovalRequest,
    concept_id: str | None,
    actor: str,
    notes: str | None,
) -> None:
    if not concept_id:
        raise ControlPlaneError("CONCEPT_REQUIRED", "name the concept to select")
    allowed = set((request.payload or {}).get("concept_ids") or [])
    if concept_id not in allowed:
        raise ControlPlaneError("CONCEPT_NOT_IN_BATCH", "the concept is outside this approval")
    concept = session.get(ConceptCandidate, concept_id)
    if concept is None:
        raise ControlPlaneError("CONCEPT_NOT_FOUND", "concept does not exist")
    current_hash = stable_digest({"concept_ids": sorted(allowed)})
    if current_hash != request.subject_hash:
        raise ControlPlaneError("HASH_MISMATCH", "the concept batch changed since the request was bound")
    decide_concept(session, concept, "SELECT", actor, notes)
    if request.workflow_run_id:
        run = _run(session, request.workflow_run_id)
        order = _order(session, run.work_order_id)
        if order.creative_id:
            creative = session.get(Creative, order.creative_id)
            if creative is not None and creative.selected_concept_id is None:
                link_selected_concept(creative, concept)
        _remember(run, "selected_concept_id", concept.id)


def _approve_story(session: Session, request: ApprovalRequest, actor: str, notes: str | None) -> None:
    version = session.get(StoryLockVersion, request.subject_id)
    creative_id = (request.payload or {}).get("creative_id")
    creative = session.get(Creative, creative_id) if creative_id else None
    if version is None or creative is None:
        raise ControlPlaneError("LOCK_MISSING", "story approval is bound to a pending story lock version")
    current_hash = version.document_hash or version.content_hash
    if current_hash != request.subject_hash:
        raise ControlPlaneError("HASH_MISMATCH", "the story lock hash changed since the request was bound")
    before = creative.current_approved_story_lock_version_id
    decide_story_lock_version(session, creative, version, "APPROVE", actor, notes)
    if creative.current_approved_story_lock_version_id == before:
        raise ControlPlaneError("POINTER_UNCHANGED", "story approval did not use the existing approval path")


def _manual_run(
    session: Session,
    bundle: ContextBundle,
    assignment: SpecialistAssignment,
    raw: str,
    parsed: dict[str, Any],
) -> ModelRun:
    now = utcnow()
    run = ModelRun(
        capability="MANUAL_SUBSCRIPTION",
        status="RECORDED",
        started_at=now,
        finished_at=now,
        input_refs={
            "context_bundle_id": bundle.id,
            "transport": "MANUAL_SUBSCRIPTION",
            "api_verified": False,
        },
        output_refs={},
        context_bundle_id=bundle.id,
        creative_task_id=bundle.creative_task_id,
        context_bundle_hash=bundle.payload_hash,
        provider_model_name=assignment.model_name,
        raw_response=raw,
        parsed_output=parsed,
        execution_origin="MANUAL_SUBSCRIPTION",
        execution_state="RECORDED",
        usage_metadata={
            "transport": "MANUAL_SUBSCRIPTION",
            "provider_declared": assignment.provider_name,
            "api_verified": False,
        },
    )
    session.add(run)
    session.flush()
    return run


def _matching_asset(assets: list[Asset], requirement: dict[str, Any]) -> Asset | None:
    for asset in assets:
        if not _field_matches(requirement.get("required_role"), asset.role):
            continue
        if not _field_matches(requirement.get("ecosystem"), asset.ecosystem_code):
            continue
        if not _field_matches(requirement.get("product"), asset.product_model):
            continue
        haystack = f"{asset.name}\n{asset.notes or ''}".casefold()
        if not _text_matches(requirement.get("surface_type"), haystack):
            continue
        if not _text_matches(requirement.get("state"), haystack):
            continue
        if not _text_matches(requirement.get("mode"), haystack):
            continue
        return asset
    return None


def _field_matches(expected: object, actual: object) -> bool:
    if expected in (None, ""):
        return True
    return str(actual or "").casefold() == str(expected).casefold()


def _text_matches(expected: object, haystack: str) -> bool:
    if expected in (None, ""):
        return True
    return str(expected).casefold() in haystack


def _pending_lock(session: Session, creative_id: str) -> StoryLockVersion | None:
    lock = session.scalar(select(StoryLock).where(StoryLock.creative_id == creative_id))
    if lock is None:
        return None
    return session.scalar(
        select(StoryLockVersion)
        .where(
            StoryLockVersion.story_lock_id == lock.id,
            StoryLockVersion.approval_state == "PENDING",
        )
        .order_by(StoryLockVersion.version_number.desc())
        .limit(1)
    )


def _approved_pointer(session: Session, run: WorkflowRun) -> str | None:
    order = _order(session, run.work_order_id)
    if not order.creative_id:
        return None
    creative = session.get(Creative, order.creative_id)
    return None if creative is None else creative.current_approved_story_lock_version_id


def _bundle_for_specialist(run: WorkflowRun, steps: list[StepRun], step: StepRun) -> str | None:
    previous = _previous(steps, step, "COMPILE_CONTEXT")
    if previous and previous.output_refs.get("context_bundle_id"):
        return str(previous.output_refs["context_bundle_id"])
    return run.memory.get("story_bundle_id") or run.memory.get("concept_bundle_id")


def _previous(steps: list[StepRun], step: StepRun, kind: str) -> StepRun | None:
    earlier = [item for item in steps if item.position < step.position and item.node_kind == kind]
    return earlier[-1] if earlier else None


def _finish(session: Session, step: StepRun, actor: str, outputs: dict[str, Any]) -> None:
    step.output_refs = outputs
    _set_step(session, step, "SUCCEEDED", actor, step.node_kind)


def _block(session: Session, step: StepRun, code: str, detail: str) -> None:
    step.error_code = code
    step.error_detail = detail
    _set_step(session, step, "BLOCKED", get_settings().operator_identity, code)


def _sync(session: Session, run: WorkflowRun, actor: str) -> None:
    order = _order(session, run.work_order_id)
    steps = _steps(session, run.id)
    if any(step.status == "BLOCKED" for step in steps):
        target = "BLOCKED"
    elif any(step.status == "WAITING_HUMAN" for step in steps):
        target = "WAITING_HUMAN"
    elif any(step.status == "WAITING_EXTERNAL_RESPONSE" for step in steps):
        target = "WAITING_SPECIALIST"
    elif any(step.status == "FAILED" for step in steps):
        target = "BLOCKED"
    elif steps and all(step.status == "SUCCEEDED" for step in steps):
        target = "COMPLETED"
    else:
        target = "RUNNING"
    _move_order(session, order, run, target, actor, "workflow sync")


def _move_order(
    session: Session, order: WorkOrder, run: WorkflowRun, target: str, actor: str, detail: str
) -> None:
    if order.status != target:
        if target not in ORDER_EDGES.get(order.status, set()):
            if "RUNNING" in ORDER_EDGES.get(order.status, set()) and target in ORDER_EDGES["RUNNING"]:
                order.status = "RUNNING"
            else:
                raise ControlPlaneError(
                    "INVALID_TRANSITION", f"work order cannot move {order.status} -> {target}"
                )
        previous = order.status
        order.status = target
        order.updated_at = utcnow()
        _event(session, run.id, None, previous, target, actor, detail)
    run.status = target
    run.updated_at = utcnow()
    flag_modified(run, "memory")
    session.flush()


def _set_step(session: Session, step: StepRun, status: str, actor: str, detail: str | None) -> None:
    if step.status == status:
        return
    if status not in STEP_EDGES.get(step.status, set()):
        raise ControlPlaneError("INVALID_TRANSITION", f"step cannot move {step.status} -> {status}")
    previous = step.status
    now = utcnow()
    step.status = status
    if step.started_at is None and status != "PENDING":
        step.started_at = now
    if status in {"SUCCEEDED", "FAILED", "CANCELLED", "BLOCKED"}:
        step.finished_at = now
    _event(session, step.workflow_run_id, step.id, previous, status, actor, detail)
    session.flush()


def _event(
    session: Session,
    run_id: str,
    step_id: str | None,
    previous: str | None,
    status: str,
    actor: str,
    detail: str | None,
) -> None:
    session.add(
        WorkflowEvent(
            workflow_run_id=run_id,
            step_run_id=step_id,
            from_status=previous,
            to_status=status,
            actor=actor,
            detail=detail,
            created_at=utcnow(),
        )
    )
    session.flush()


def _evidence(
    session: Session,
    run: WorkflowRun,
    step: StepRun,
    *,
    evidence_type: str,
    source: str,
    subject_type: str,
    subject_id: str,
    content_hash: str | None,
    claims: list[str],
    verification_state: str = "RECORDED",
) -> EvidenceRecord:
    row = EvidenceRecord(
        evidence_type=evidence_type,
        source=source,
        subject_type=subject_type,
        subject_id=subject_id,
        content_hash=content_hash,
        claims_supported=claims,
        verification_state=verification_state,
        workflow_run_id=run.id,
        step_run_id=step.id,
        created_at=utcnow(),
    )
    session.add(row)
    session.flush()
    step.evidence_ids = [*list(step.evidence_ids or []), row.id]
    flag_modified(step, "evidence_ids")
    return row


def _remember(run: WorkflowRun, key: str, value: Any) -> None:
    memory = dict(run.memory or {})
    memory[key] = value
    run.memory = memory
    flag_modified(run, "memory")


def _reject_specialist_actor(actor: str) -> None:
    lowered = actor.casefold()
    roles = {str(item["role"]).casefold() for item in SPECIALIST_ROLES}
    if lowered.startswith("specialist:") or lowered in roles:
        raise ControlPlaneError("SELF_APPROVAL", "a specialist cannot approve or authorize itself")


def _order(session: Session, work_order_id: str) -> WorkOrder:
    order = session.get(WorkOrder, work_order_id)
    if order is None:
        raise ControlPlaneError("WORK_ORDER_NOT_FOUND", "work order does not exist")
    return order


def _run(session: Session, workflow_run_id: str) -> WorkflowRun:
    run = session.get(WorkflowRun, workflow_run_id)
    if run is None:
        raise ControlPlaneError("RUN_NOT_FOUND", "workflow run does not exist")
    return run


def _steps(session: Session, workflow_run_id: str) -> list[StepRun]:
    return list(
        session.scalars(
            select(StepRun).where(StepRun.workflow_run_id == workflow_run_id).order_by(StepRun.position.asc())
        )
    )


def _recommend(
    approvals: list[ApprovalRequest],
    assignments: list[SpecialistAssignment],
    gaps: list[dict[str, Any]],
    orders: list[WorkOrder],
) -> dict[str, str]:
    if approvals:
        first = approvals[0]
        return {
            "action": "DECIDE_APPROVAL",
            "subject_id": first.id,
            "reason": f"{first.approval_type} is waiting on the human",
        }
    if assignments:
        first_assignment = assignments[0]
        return {
            "action": "IMPORT_SPECIALIST_RESPONSE",
            "subject_id": first_assignment.id,
            "reason": f"{first_assignment.specialist_role} is waiting on a manual response",
        }
    if gaps:
        return {
            "action": "SUPPLY_REFERENCES",
            "subject_id": str(gaps[0]["workflow_run_id"]),
            "reason": "production is blocked on declared missing references",
        }
    ready = next((order for order in orders if order.status in {"READY", "DRAFT"}), None)
    if ready is not None:
        return {"action": "START_WORKFLOW", "subject_id": ready.id, "reason": "a work order is ready to start"}
    return {"action": "NONE", "subject_id": "", "reason": "no allowed next action"}


def _order_view(order: WorkOrder) -> dict[str, Any]:
    return {
        "id": order.id,
        "goal": order.goal,
        "status": order.status,
        "priority": order.priority,
        "program_id": order.program_id,
        "account_id": order.account_id,
        "campaign_id": order.campaign_id,
        "creative_id": order.creative_id,
        "task_ids": list(order.task_ids or []),
        "created_at": order.created_at.isoformat(),
        "updated_at": order.updated_at.isoformat(),
    }


def _approval_view(row: ApprovalRequest) -> dict[str, Any]:
    return {
        "id": row.id,
        "approval_type": row.approval_type,
        "subject_type": row.subject_type,
        "subject_id": row.subject_id,
        "subject_hash": row.subject_hash,
        "status": row.status,
        "requested_by": row.requested_by,
        "workflow_run_id": row.workflow_run_id,
    }


def _assignment_view(row: SpecialistAssignment) -> dict[str, Any]:
    return {
        "id": row.id,
        "specialist_role": row.specialist_role,
        "transport": row.transport,
        "status": row.status,
        "api_verified": row.api_verified,
        "provider_name": row.provider_name,
        "model_name": row.model_name,
        "context_bundle_id": row.context_bundle_id,
        "context_bundle_hash": row.context_bundle_hash,
        "validation_status": row.validation_status,
        "contract_name": row.contract_name,
    }


def account_summary(session: Session, account_id: str) -> dict[str, Any]:
    account = session.get(Account, account_id)
    if account is None:
        raise ControlPlaneError("ACCOUNT_NOT_FOUND", "account does not exist")
    return {
        "id": account.id,
        "slug": account.slug,
        "name": account.name,
        "program_id": account.program_id,
        "current_approved_dna_profile_id": account.current_approved_dna_profile_id,
    }


def creative_summary(session: Session, creative_id: str) -> dict[str, Any]:
    creative = session.get(Creative, creative_id)
    if creative is None:
        raise ControlPlaneError("CREATIVE_NOT_FOUND", "creative does not exist")
    return {
        "id": creative.id,
        "slug": creative.slug,
        "name": creative.name,
        "status": creative.status,
        "program_id": creative.program_id,
        "account_id": creative.account_id,
        "current_approved_story_lock_version_id": creative.current_approved_story_lock_version_id,
        "selected_concept_id": creative.selected_concept_id,
    }


def work_queue(session: Session) -> dict[str, Any]:
    orders = list(
        session.scalars(select(WorkOrder).order_by(WorkOrder.priority.desc(), WorkOrder.created_at.asc()))
    )
    programs = list(session.scalars(select(Program).order_by(Program.slug.asc())))
    accounts = list(session.scalars(select(Account).order_by(Account.slug.asc())))
    return {
        "work_orders": [_order_view(order) for order in orders],
        "programs": [{"id": program.id, "slug": program.slug, "name": program.name} for program in programs],
        "accounts": [{"id": account.id, "slug": account.slug, "name": account.name} for account in accounts],
    }


def workflow_run_view(session: Session, workflow_run_id: str) -> dict[str, Any]:
    run = _run(session, workflow_run_id)
    version = session.get(WorkflowDefinitionVersion, run.definition_version_id)
    return {
        "id": run.id,
        "work_order_id": run.work_order_id,
        "status": run.status,
        "definition_version_id": run.definition_version_id,
        "graph_hash": None if version is None else version.graph_hash,
        "graph": [] if version is None else version.graph,
        "memory": run.memory,
        "steps": [
            {
                "id": step.id,
                "position": step.position,
                "node_id": step.node_id,
                "node_kind": step.node_kind,
                "status": step.status,
                "attempt": step.attempt,
                "specialist_role": step.specialist_role,
                "input_refs": step.input_refs,
                "output_refs": step.output_refs,
                "error_code": step.error_code,
                "error_detail": step.error_detail,
                "evidence_ids": step.evidence_ids,
                "started_at": None if step.started_at is None else step.started_at.isoformat(),
                "finished_at": None if step.finished_at is None else step.finished_at.isoformat(),
            }
            for step in _steps(session, run.id)
        ],
        "history": workflow_history(session, run.id),
    }


def list_workflow_runs(session: Session) -> list[dict[str, Any]]:
    runs = session.scalars(select(WorkflowRun).order_by(WorkflowRun.created_at.desc()))
    return [
        {
            "id": run.id,
            "work_order_id": run.work_order_id,
            "status": run.status,
            "definition_version_id": run.definition_version_id,
            "created_at": run.created_at.isoformat(),
        }
        for run in runs
    ]


def approval_queue(session: Session) -> list[dict[str, Any]]:
    rows = session.scalars(select(ApprovalRequest).order_by(ApprovalRequest.created_at.desc()))
    return [_approval_view(row) for row in rows]


def assignment_queue(session: Session) -> list[dict[str, Any]]:
    rows = session.scalars(select(SpecialistAssignment).order_by(SpecialistAssignment.created_at.desc()))
    return [_assignment_view(row) for row in rows]
