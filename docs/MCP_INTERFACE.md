# MCP interface

MCP is another caller of the company services. It is not a second authority.

## Transport

The MCP server is streamable HTTP at `/mcp`.

It supports initialization, tool discovery, tool invocation, structured tool results, and protocol errors through the MCP SDK. An arbitrary REST body is not treated as MCP.

Requests require `Authorization: Bearer <COS_MCP_TOKEN>`. The token comes from the environment or `.env`. `COS_OPERATOR_IDENTITY` is not accepted as that credential. A missing or wrong token is rejected. The token is not returned, logged, stored in plaintext metadata, or copied into tool descriptions.

The default API bind stays loopback-only. Remote MCP is unsupported.

## Registry / debug API

`GET /api/mcp/tools` and `POST /api/mcp` are the MCP registry / debug API. They call the same tool registry and require the same bearer token. They are not the MCP transport.

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

`request_approval` always creates a `PENDING` request. Passing any other status is rejected. There is no MCP tool that approves, selects a concept, decides a StoryLock, posts, or mutates Account DNA or Creative Genome.

## Prohibited

These names are not registered on the MCP server. The debug registry rejects and audits them: arbitrary SQL, shell, filesystem, direct StoryLock mutation, `decide_story_lock`, `select_concept`, direct Account DNA mutation, Creative Genome mutation, approval bypass, `approve_request`, posting, GeeLark, device start, purchasing, and image execution.

## Audit

Every tool invocation writes `McpAuditLog` with the MCP client/interface, tool name, request id when the transport has one, a hash of the redacted input, the redacted input, affected record ids, result, and timestamp. Secret-like fields are redacted. Human approval rules are unchanged: the server operator identity decides, and a specialist identity cannot.
