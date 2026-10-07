"""Tool registry for the company control plane. MCP is an interface, not an authority."""

from typing import Any

from sqlalchemy.orm import Session

from creative_os.models.company import McpAuditLog
from creative_os.services.control_plane import (
    ControlPlaneError,
    account_summary,
    approval_queue,
    company_status,
    compile_context_for_step,
    create_manual_assignment_for_step,
    create_work_order,
    creative_summary,
    reference_gap_queue,
    request_approval,
    start_workflow,
    work_queue,
    workflow_run_view,
)
from creative_os.util import utcnow

READ_TOOLS = frozenset(
    {
        "get_company_status",
        "get_work_queue",
        "get_work_order",
        "get_workflow_run",
        "get_approval_queue",
        "get_account_summary",
        "get_creative_summary",
        "get_reference_gaps",
    }
)
MUTATION_TOOLS = frozenset(
    {
        "create_work_order",
        "start_workflow",
        "compile_context_for_step",
        "create_manual_specialist_assignment",
        "request_approval",
    }
)
PROHIBITED_TOOLS = frozenset(
    {
        "execute_sql",
        "sql",
        "shell",
        "mutate_story_lock",
        "mutate_account_dna",
        "bypass_approval",
        "approve_request",
        "post_content",
        "geelark",
        "run_geelark_workflow",
        "start_device",
        "purchase",
    }
)


def invoke(
    session: Session,
    tool: str,
    arguments: dict[str, Any] | None = None,
    *,
    caller: str = "mcp",
) -> dict[str, Any]:
    payload = dict(arguments or {})
    if tool in PROHIBITED_TOOLS or tool not in READ_TOOLS | MUTATION_TOOLS:
        result = {"error": "PROHIBITED", "message": f"{tool} is not exposed"}
        _audit(session, caller, tool, payload, [], result)
        raise ControlPlaneError("PROHIBITED", f"{tool} is not exposed")
    try:
        result, affected = _dispatch(session, tool, payload)
    except ControlPlaneError as exc:
        if tool in MUTATION_TOOLS:
            _audit(session, caller, tool, payload, [], {"error": exc.code, "message": str(exc)})
        raise
    if tool in MUTATION_TOOLS:
        _audit(session, caller, tool, payload, affected, result)
    return result


def _dispatch(
    session: Session, tool: str, payload: dict[str, Any]
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    if tool == "get_company_status":
        return company_status(session), []
    if tool == "get_work_queue":
        return work_queue(session), []
    if tool == "get_work_order":
        queue = work_queue(session)
        match = next((row for row in queue["work_orders"] if row["id"] == payload.get("work_order_id")), None)
        if match is None:
            raise ControlPlaneError("WORK_ORDER_NOT_FOUND", "work order does not exist")
        return match, []
    if tool == "get_workflow_run":
        return workflow_run_view(session, str(payload["workflow_run_id"])), []
    if tool == "get_approval_queue":
        return {"approvals": approval_queue(session)}, []
    if tool == "get_account_summary":
        return account_summary(session, str(payload["account_id"])), []
    if tool == "get_creative_summary":
        return creative_summary(session, str(payload["creative_id"])), []
    if tool == "get_reference_gaps":
        return {"gaps": reference_gap_queue(session)}, []
    if tool == "create_work_order":
        order = create_work_order(
            session,
            goal=str(payload.get("goal") or ""),
            program_id=str(payload.get("program_id") or ""),
            account_id=payload.get("account_id"),
            campaign_id=payload.get("campaign_id"),
            creative_id=payload.get("creative_id"),
            priority=str(payload.get("priority") or "NORMAL"),
            notes=payload.get("notes"),
            reference_requirements=payload.get("reference_requirements") or [],
            requested_by=str(payload.get("requested_by") or "mcp"),
        )
        return {"id": order.id, "status": order.status}, [{"type": "work_order", "id": order.id}]
    if tool == "start_workflow":
        run = start_workflow(session, str(payload["work_order_id"]))
        return {"id": run.id, "status": run.status}, [{"type": "workflow_run", "id": run.id}]
    if tool == "compile_context_for_step":
        output = compile_context_for_step(session, str(payload["step_run_id"]))
        return output, [{"type": "step_run", "id": str(payload["step_run_id"])}]
    if tool == "create_manual_specialist_assignment":
        assignment = create_manual_assignment_for_step(session, str(payload["step_run_id"]))
        return {
            "id": assignment.id,
            "status": assignment.status,
            "transport": assignment.transport,
            "api_verified": assignment.api_verified,
        }, [{"type": "specialist_assignment", "id": assignment.id}]
    if tool == "request_approval":
        if str(payload.get("status") or "PENDING").upper() != "PENDING":
            raise ControlPlaneError("SELF_APPROVAL", "MCP cannot decide an approval")
        request = request_approval(
            session,
            approval_type=str(payload.get("approval_type") or ""),
            subject_type=str(payload.get("subject_type") or ""),
            subject_id=str(payload.get("subject_id") or ""),
            subject_hash=str(payload.get("subject_hash") or ""),
            requested_by=str(payload.get("requested_by") or "mcp"),
            workflow_run_id=payload.get("workflow_run_id"),
            step_run_id=payload.get("step_run_id"),
        )
        return {
            "id": request.id,
            "status": request.status,
            "approval_type": request.approval_type,
        }, [{"type": "approval_request", "id": request.id}]
    raise ControlPlaneError("PROHIBITED", f"{tool} is not exposed")


def _audit(
    session: Session,
    caller: str,
    operation: str,
    payload: dict[str, Any],
    affected: list[dict[str, str]],
    result: dict[str, Any],
) -> None:
    session.add(
        McpAuditLog(
            caller=caller,
            interface="MCP",
            operation=operation,
            input_json=payload,
            affected_records=affected,
            result_json=result,
            created_at=utcnow(),
        )
    )
    session.flush()


def tool_names() -> dict[str, list[str]]:
    return {
        "read": sorted(READ_TOOLS),
        "mutation": sorted(MUTATION_TOOLS),
        "prohibited": sorted(PROHIBITED_TOOLS),
    }
