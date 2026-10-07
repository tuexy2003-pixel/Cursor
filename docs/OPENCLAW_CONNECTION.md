# OpenClaw connection

OpenClaw is not installed in this repository. This page is the connection contract for a later client. Do not install OpenClaw from here.

## Endpoint

- URL: `http://127.0.0.1:8000/mcp`
- Transport: `streamable-http`
- Binding: loopback only

Remote MCP deployment is unsupported until a remote authentication design exists. The API refuses to start when `COS_API_HOST` is not loopback.

`POST /api/mcp` is the MCP registry / debug API. It is not the MCP transport.

## Credential

Set `COS_MCP_TOKEN` in the Creative OS environment or `.env`. Every MCP HTTP request must send:

`Authorization: Bearer <COS_MCP_TOKEN>`

`COS_OPERATOR_IDENTITY` names the human operator. It is not this secret and it does not authenticate MCP.

Creative OS does not return the token from the API, write it to logs, store it in database metadata, or put it in tool descriptions. If the token is unset, MCP requests are rejected.

## Allowed tools

Reads:

- `get_company_status`
- `get_work_queue`
- `get_work_order`
- `get_workflow_run`
- `get_approval_queue`
- `get_account_summary`
- `get_creative_summary`
- `get_reference_gaps`

Controlled mutations:

- `create_work_order`
- `start_workflow`
- `compile_context_for_step`
- `create_manual_specialist_assignment`
- `request_approval`

`request_approval` creates a `PENDING` request. A future CEO may request human action. It may not perform human approval.

## Prohibited

These are not MCP tools: `approve_request`, `decide_story_lock`, `select_concept`, direct StoryLock mutation, Account DNA mutation, Creative Genome mutation, arbitrary SQL, shell, filesystem, GeeLark, posting, purchasing, and image execution.

## Example shape

```text
mcp.servers.creative_os.url = http://127.0.0.1:8000/mcp
transport = streamable-http
Authorization header from the environment secret COS_MCP_TOKEN
```

The port is `COS_API_PORT` (8000 by default). Keep the host on `127.0.0.1`.
