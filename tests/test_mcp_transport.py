"""Standards-compliant MCP client against the streamable HTTP server. OpenClaw is not required."""

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from creative_os.config import repo_root
from creative_os.mcp.server import MUTATION_TOOLS, READ_TOOLS
from creative_os.models.company import McpAuditLog

pytestmark = pytest.mark.core

TOKEN = "mcp-secret-do-not-leak"
SEED = """
from creative_os.db import make_engine, make_session_factory
from creative_os.models import Base, Program
from creative_os.util import utcnow

engine = make_engine()
Base.metadata.create_all(engine)
session = make_session_factory(engine)()
program = Program(slug="mcp", name="MCP", created_at=utcnow())
session.add(program)
session.commit()
print(program.id)
"""


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_tools(port: int) -> None:
    url = f"http://127.0.0.1:{port}/api/mcp/tools"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    last = ""
    for _ in range(50):
        try:
            response = httpx.get(url, headers=headers, timeout=0.5)
            if response.status_code == 200:
                return
            last = response.text
        except httpx.HTTPError as exc:
            last = str(exc)
        time.sleep(0.2)
    raise AssertionError(f"MCP server did not start: {last}")


def _payload(result: object) -> dict:
    structured = getattr(result, "structured_content", None)
    if isinstance(structured, dict) and structured.get("result") and isinstance(structured["result"], dict):
        return structured["result"]
    if isinstance(structured, dict) and {"status", "calculated_by", "id"} & set(structured):
        return structured
    content = getattr(result, "content", None) or []
    for block in content:
        text = getattr(block, "text", None)
        if isinstance(text, str) and text.startswith("{"):
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
    raise AssertionError(f"tool result had no JSON payload: {result!r}")


@pytest.fixture
def mcp_server(tmp_path: Path):
    database = tmp_path / "mcp.db"
    env = os.environ.copy()
    env["COS_DATABASE_URL"] = f"sqlite:///{database}"
    env["COS_MCP_TOKEN"] = TOKEN
    env["COS_API_HOST"] = "127.0.0.1"
    env["PYTHONPATH"] = str(repo_root() / "src")
    port = _free_port()
    seed = subprocess.run(
        [sys.executable, "-c", SEED],
        cwd=repo_root(),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if seed.returncode != 0:
        raise AssertionError(seed.stderr)
    log_path = tmp_path / "uvicorn.log"
    log_file = log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "creative_os.api.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=repo_root(),
        env=env,
        stdout=log_file,
        stderr=subprocess.STDOUT,
    )
    try:
        _wait_for_tools(port)
    except Exception:
        process.terminate()
        log_file.close()
        raise
    yield {"port": port, "program_id": seed.stdout.strip(), "database": database, "log_path": log_path}
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)
    log_file.close()


def test_streamable_http_initializes_lists_and_audits(mcp_server: dict) -> None:
    import asyncio

    import httpx2
    from mcp import ClientSession
    from mcp.client.streamable_http import streamable_http_client

    port = mcp_server["port"]
    base = f"http://127.0.0.1:{port}"
    missing = httpx.post(f"{base}/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert missing.status_code == 401
    assert TOKEN not in missing.text
    bad = httpx.post(
        f"{base}/mcp",
        headers={"Authorization": "Bearer wrong-token"},
        json={"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
    )
    assert bad.status_code == 401
    assert TOKEN not in bad.text
    assert "wrong-token" not in bad.text
    debug = httpx.get(f"{base}/api/mcp/tools")
    assert debug.status_code == 401
    listed = httpx.get(f"{base}/api/mcp/tools", headers={"Authorization": f"Bearer {TOKEN}"})
    assert listed.status_code == 200
    body = listed.json()
    assert body["role"] == "MCP_REGISTRY_DEBUG"
    assert TOKEN not in listed.text

    async def exercise() -> tuple[list[str], dict, dict, object]:
        headers = {"Authorization": f"Bearer {TOKEN}"}
        async with httpx2.AsyncClient(headers=headers) as http_client:
            async with streamable_http_client(f"{base}/mcp", http_client=http_client) as streams:
                read, write = streams
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    names = sorted(tool.name for tool in tools.tools)
                    for tool in tools.tools:
                        assert TOKEN not in (tool.description or "")
                    status = await session.call_tool("get_company_status", {})
                    created = await session.call_tool(
                        "create_work_order",
                        {"goal": "Harmless MCP work order", "program_id": mcp_server["program_id"]},
                    )
                    denied = await session.call_tool("approve_request", {})
                    for hidden in ("decide_story_lock", "select_concept", "geelark", "shell"):
                        hidden_result = await session.call_tool(hidden, {})
                        assert hidden_result.is_error
                    return names, _payload(status), _payload(created), denied

    names, status, created, denied = asyncio.run(exercise())
    assert names == sorted(READ_TOOLS | MUTATION_TOOLS)
    assert "approve_request" not in names
    assert "decide_story_lock" not in names
    assert "select_concept" not in names
    assert status["calculated_by"] == "control_plane"
    assert created["status"] == "READY"
    assert getattr(denied, "is_error", False)

    engine = create_engine(f"sqlite:///{mcp_server['database']}")
    with Session(engine) as session:
        rows = list(session.scalars(select(McpAuditLog).where(McpAuditLog.operation == "create_work_order")))
        assert len(rows) == 1
        audit = rows[0]
        assert audit.interface == "MCP"
        assert audit.caller == "mcp-streamable-http"
        assert audit.request_id
        assert audit.input_hash
        assert audit.affected_records[0]["id"] == created["id"]
        assert TOKEN not in json.dumps(audit.input_json)
        assert TOKEN not in json.dumps(audit.result_json)
        read_row = session.scalar(select(McpAuditLog).where(McpAuditLog.operation == "get_company_status"))
        assert read_row is not None
    log_text = Path(mcp_server["log_path"]).read_text(encoding="utf-8")
    assert TOKEN not in log_text
