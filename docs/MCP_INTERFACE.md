# MCP interface

MCP is another caller of the company services. It is not a second authority.

The HTTP entry is `POST /api/mcp` with `{ "tool", "arguments", "caller" }`. `GET /api/mcp/tools` lists the registry.

## Reads

- `get_company_status`
- `get_work_queue`
- `get_work_order`
- `get_workflow_run`
- `get_approval_queue`
- `get_account_summary`
- `get_creative_summary`
- `get_reference_gaps`

`get_company_status` is calculated by the service. A future CEO agent may summarize those facts. It does not decide them.

## Mutations

- `create_work_order`
- `start_workflow`
- `compile_context_for_step`
- `create_manual_specialist_assignment`
- `request_approval`

`request_approval` always creates a `PENDING` request. Passing any other status is rejected. There is no MCP tool that approves, posts, or mutates a story lock.

## Prohibited

These names are rejected and audited as prohibited: arbitrary SQL, shell, direct StoryLock mutation, direct Account DNA mutation, approval bypass, posting, GeeLark, device start, and purchasing.

## Audit

Every mutation, including a rejected mutation, writes `McpAuditLog` with the caller, interface `MCP`, operation, input, affected record ids, timestamp, and result. Human approval rules are the same for the UI, the API, and MCP: the server operator identity decides, and a specialist identity cannot.
