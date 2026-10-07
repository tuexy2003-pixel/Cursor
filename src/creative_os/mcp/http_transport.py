"""Streamable HTTP MCP transport. This is the protocol endpoint, not the debug registry."""

from typing import Any

from starlette.routing import Route
from starlette.types import Receive, Scope, Send

from creative_os.db import make_engine, make_session_factory
from creative_os.mcp.auth import mcp_bearer_matches
from creative_os.mcp.server import _audit, invoke
from creative_os.services.control_plane import ControlPlaneError

try:
    from mcp.server.mcpserver import Context, MCPServer
    from mcp.server.mcpserver.exceptions import ToolError
except ImportError as exc:  # pragma: no cover - the dependency is declared
    raise RuntimeError("the mcp package is required for the streamable HTTP transport") from exc

_INSTRUCTIONS = (
    "Creative OS company tools. Read company state or request human action. "
    "These tools do not approve, post, purchase, or mutate a story lock."
)


def _request_id(ctx: Context) -> str | None:
    try:
        return str(ctx.request_id)
    except Exception:
        return None


def _call(ctx: Context, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    session = make_session_factory(make_engine())()
    request_id = _request_id(ctx)
    try:
        result = invoke(session, name, arguments, caller="mcp-streamable-http", request_id=request_id)
        session.commit()
        return result
    except ControlPlaneError as exc:
        session.rollback()
        _audit(
            session,
            "mcp-streamable-http",
            name,
            arguments,
            [],
            {"error": exc.code, "message": str(exc)},
            request_id=request_id,
        )
        session.commit()
        raise ToolError(f"{exc.code}: {exc}") from exc
    finally:
        session.close()


def _register(server: MCPServer) -> None:
    @server.tool(description="Read the company status calculated by Creative OS.")
    def get_company_status(ctx: Context) -> dict[str, Any]:
        return _call(ctx, "get_company_status", {})

    @server.tool(description="Read the work-order queue.")
    def get_work_queue(ctx: Context) -> dict[str, Any]:
        return _call(ctx, "get_work_queue", {})

    @server.tool(description="Read one work order by id.")
    def get_work_order(ctx: Context, work_order_id: str) -> dict[str, Any]:
        return _call(ctx, "get_work_order", {"work_order_id": work_order_id})

    @server.tool(description="Read one workflow run by id.")
    def get_workflow_run(ctx: Context, workflow_run_id: str) -> dict[str, Any]:
        return _call(ctx, "get_workflow_run", {"workflow_run_id": workflow_run_id})

    @server.tool(description="Read approval requests. This does not decide them.")
    def get_approval_queue(ctx: Context) -> dict[str, Any]:
        return _call(ctx, "get_approval_queue", {})

    @server.tool(description="Read one account summary.")
    def get_account_summary(ctx: Context, account_id: str) -> dict[str, Any]:
        return _call(ctx, "get_account_summary", {"account_id": account_id})

    @server.tool(description="Read one creative summary.")
    def get_creative_summary(ctx: Context, creative_id: str) -> dict[str, Any]:
        return _call(ctx, "get_creative_summary", {"creative_id": creative_id})

    @server.tool(description="Read declared reference gaps.")
    def get_reference_gaps(ctx: Context) -> dict[str, Any]:
        return _call(ctx, "get_reference_gaps", {})

    @server.tool(description="Create a work order through the company domain service.")
    def create_work_order(
        ctx: Context,
        goal: str,
        program_id: str,
        account_id: str | None = None,
        campaign_id: str | None = None,
        creative_id: str | None = None,
        priority: str = "NORMAL",
        notes: str | None = None,
        requested_by: str = "mcp",
    ) -> dict[str, Any]:
        return _call(
            ctx,
            "create_work_order",
            {
                "goal": goal,
                "program_id": program_id,
                "account_id": account_id,
                "campaign_id": campaign_id,
                "creative_id": creative_id,
                "priority": priority,
                "notes": notes,
                "requested_by": requested_by,
            },
        )

    @server.tool(description="Start NEW_CREATIVE_V1 for a work order.")
    def start_workflow(ctx: Context, work_order_id: str) -> dict[str, Any]:
        return _call(ctx, "start_workflow", {"work_order_id": work_order_id})

    @server.tool(description="Compile context for a workflow step that is ready.")
    def compile_context_for_step(ctx: Context, step_run_id: str) -> dict[str, Any]:
        return _call(ctx, "compile_context_for_step", {"step_run_id": step_run_id})

    @server.tool(description="Create a manual specialist assignment for a reasoning step.")
    def create_manual_specialist_assignment(ctx: Context, step_run_id: str) -> dict[str, Any]:
        return _call(ctx, "create_manual_specialist_assignment", {"step_run_id": step_run_id})

    @server.tool(description="Request a pending human approval. This does not approve it.")
    def request_approval(
        ctx: Context,
        approval_type: str,
        subject_type: str,
        subject_id: str,
        subject_hash: str,
        requested_by: str = "mcp",
        workflow_run_id: str | None = None,
        step_run_id: str | None = None,
    ) -> dict[str, Any]:
        return _call(
            ctx,
            "request_approval",
            {
                "approval_type": approval_type,
                "subject_type": subject_type,
                "subject_id": subject_id,
                "subject_hash": subject_hash,
                "requested_by": requested_by,
                "workflow_run_id": workflow_run_id,
                "step_run_id": step_run_id,
                "status": "PENDING",
            },
        )


class _BearerGate:
    """Reject MCP HTTP calls that do not present the dedicated bearer credential."""

    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") == "http":
            header = _authorization(scope)
            if not mcp_bearer_matches(header):
                body = b'{"detail":"MCP credential required"}'
                await send(
                    {
                        "type": "http.response.start",
                        "status": 401,
                        "headers": [
                            (b"content-type", b"application/json"),
                            (b"content-length", str(len(body)).encode()),
                        ],
                    }
                )
                await send({"type": "http.response.body", "body": body})
                return
        await self.app(scope, receive, send)


def _authorization(scope: Scope) -> str | None:
    for key, value in scope.get("headers") or []:
        if key.lower() == b"authorization":
            return value.decode("latin-1")
    return None


def _build() -> tuple[MCPServer, _BearerGate]:
    server = MCPServer(name="creative-os", instructions=_INSTRUCTIONS, version="0.4.1")
    _register(server)
    starlette_app = server.streamable_http_app(
        streamable_http_path="/mcp",
        json_response=True,
        host="127.0.0.1",
    )
    route = starlette_app.routes[0]
    if not isinstance(route, Route):
        raise RuntimeError("MCP transport route was not registered")
    return server, _BearerGate(route.endpoint)


mcp_server, mcp_asgi_app = _build()
mcp_session_manager = mcp_server.session_manager
