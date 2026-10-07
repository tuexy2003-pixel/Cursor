"""HTTP interface for the company control plane. Decisions stay in the domain services."""

from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from creative_os.api.deps import get_session
from creative_os.config import get_settings
from creative_os.mcp.auth import mcp_bearer_matches
from creative_os.mcp.server import invoke, tool_names
from creative_os.services.control_plane import (
    ControlPlaneError,
    assignment_packet,
    assignment_queue,
    company_status,
    create_work_order,
    decide_approval,
    import_manual_response,
    list_workflow_runs,
    reference_gap_queue,
    start_workflow,
    work_queue,
    workflow_run_view,
)

router = APIRouter(tags=["company"])


class WorkOrderBody(BaseModel):
    goal: str
    program_id: str
    account_id: str | None = None
    campaign_id: str | None = None
    creative_id: str | None = None
    priority: str = "NORMAL"
    notes: str | None = None
    reference_requirements: list[dict[str, Any]] = Field(default_factory=list)


class StartBody(BaseModel):
    work_order_id: str


class ImportBody(BaseModel):
    raw_response: str
    provider_name: str
    model_name: str


class DecisionBody(BaseModel):
    decision: str
    concept_id: str | None = None
    notes: str | None = None


class McpBody(BaseModel):
    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    caller: str = "mcp"


def require_mcp_token(authorization: str | None = Header(default=None)) -> None:
    if not mcp_bearer_matches(authorization):
        raise HTTPException(status_code=401, detail="MCP credential required")


def _guard(exc: ControlPlaneError) -> HTTPException:
    status = 403 if exc.code in {"PROHIBITED", "SELF_APPROVAL", "OPERATOR_REQUIRED", "DISABLED"} else 400
    return HTTPException(status_code=status, detail={"code": exc.code, "message": str(exc)})


@router.get("/company/status")
def get_company_status(session: Session = Depends(get_session)) -> dict[str, Any]:
    return company_status(session)


@router.get("/company/queue")
def get_queue(session: Session = Depends(get_session)) -> dict[str, Any]:
    return work_queue(session)


@router.get("/company/workflow-runs")
def get_workflow_runs(session: Session = Depends(get_session)) -> list[dict[str, Any]]:
    return list_workflow_runs(session)


@router.get("/company/workflow-runs/{workflow_run_id}")
def get_workflow_run(workflow_run_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    try:
        return workflow_run_view(session, workflow_run_id)
    except ControlPlaneError as exc:
        raise _guard(exc) from exc


@router.get("/company/approvals")
def get_approvals(session: Session = Depends(get_session)) -> dict[str, Any]:
    status = company_status(session)
    return {"waiting_on_human": status["waiting_on_human"]}


@router.get("/company/assignments")
def get_assignments(session: Session = Depends(get_session)) -> list[dict[str, Any]]:
    return assignment_queue(session)


@router.get("/company/assignments/{assignment_id}/packet")
def get_packet(assignment_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    try:
        return assignment_packet(session, assignment_id)
    except ControlPlaneError as exc:
        raise _guard(exc) from exc


@router.get("/company/reference-gaps")
def get_reference_gaps(session: Session = Depends(get_session)) -> dict[str, Any]:
    return {"gaps": reference_gap_queue(session)}


@router.post("/company/work-orders")
def post_work_order(body: WorkOrderBody, session: Session = Depends(get_session)) -> dict[str, str]:
    try:
        order = create_work_order(
            session,
            goal=body.goal,
            program_id=body.program_id,
            account_id=body.account_id,
            campaign_id=body.campaign_id,
            creative_id=body.creative_id,
            priority=body.priority,
            notes=body.notes,
            reference_requirements=body.reference_requirements,
            requested_by=get_settings().operator_identity,
        )
    except ControlPlaneError as exc:
        raise _guard(exc) from exc
    return {"id": order.id, "status": order.status}


@router.post("/company/workflow-runs")
def post_workflow_run(body: StartBody, session: Session = Depends(get_session)) -> dict[str, str]:
    try:
        run = start_workflow(session, body.work_order_id, actor=get_settings().operator_identity)
    except ControlPlaneError as exc:
        raise _guard(exc) from exc
    return {"id": run.id, "status": run.status}


@router.post("/company/assignments/{assignment_id}/import")
def post_import(
    assignment_id: str, body: ImportBody, session: Session = Depends(get_session)
) -> dict[str, Any]:
    try:
        assignment = import_manual_response(
            session,
            assignment_id,
            body.raw_response,
            provider_name=body.provider_name,
            model_name=body.model_name,
            actor=get_settings().operator_identity,
        )
    except ControlPlaneError as exc:
        raise _guard(exc) from exc
    return {
        "id": assignment.id,
        "status": assignment.status,
        "validation_status": assignment.validation_status,
        "api_verified": assignment.api_verified,
        "error_detail": assignment.error_detail,
    }


@router.post("/company/approvals/{request_id}/decide")
def post_decision(
    request_id: str, body: DecisionBody, session: Session = Depends(get_session)
) -> dict[str, str]:
    try:
        request = decide_approval(
            session,
            request_id,
            body.decision,
            actor=get_settings().operator_identity,
            concept_id=body.concept_id,
            notes=body.notes,
        )
    except ControlPlaneError as exc:
        raise _guard(exc) from exc
    return {"id": request.id, "status": request.status}


@router.get("/mcp/tools", dependencies=[Depends(require_mcp_token)])
def get_mcp_tools() -> dict[str, Any]:
    """MCP registry / debug API. The streamable HTTP transport is /mcp."""
    return {"role": "MCP_REGISTRY_DEBUG", **tool_names()}


@router.post("/mcp", dependencies=[Depends(require_mcp_token)])
def post_mcp(body: McpBody, session: Session = Depends(get_session)) -> dict[str, Any]:
    try:
        return invoke(session, body.tool, body.arguments, caller=body.caller)
    except ControlPlaneError as exc:
        raise _guard(exc) from exc
