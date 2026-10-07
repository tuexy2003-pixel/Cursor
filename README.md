# Creative OS

Versioned infrastructure around the existing MyDashPerks creative workflow. The 15 Markdown skills stay the creative-policy layer. This application versions story locks, skills, assets, approvals, and the records around them.

The imported snapshot in `source_snapshots/2026-10-05/` is read-only source. Do not edit it. Historical paths such as `/workspace/creative-pipeline/` are provenance, not runtime paths.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
creative-os migrate
creative-os import-handoff
creative-os import-examples
creative-os apply-baseline
creative-os serve
```

`creative-os reset-db --seed` deletes the local SQLite file, migrates, imports the core snapshot, attaches the supplemental visuals, and applies the working policy. It does not keep operator verification edits.

Operator UI:

```bash
cd apps/web
npm install
npm run dev
```

The UI expects the API at `http://127.0.0.1:8000`. Override with `NEXT_PUBLIC_API_BASE`.

## Checks

```bash
ruff check
ruff format --check
mypy
pytest
```

A source-review archive omits the large visual binaries. Its documented check is:

```bash
PYTHONPATH=src pytest -m core
```

`pytest -m full_assets` needs the supplemental image archives. If those files are absent, those tests skip.

## Local operator only

The API binds to loopback by default. Operator routes trust the server-side `COS_OPERATOR_IDENTITY`. `COS_API_HOST` must stay `127.0.0.1`, `localhost`, or `::1`. Any other host refuses to start. Remote mutation routes are not supported until operator authentication exists. Provider code cannot approve a story lock. Human approval uses `COS_OPERATOR_IDENTITY`, not an `actor` string from request JSON.

`/mcp` is a streamable HTTP MCP server. It requires `Authorization: Bearer <COS_MCP_TOKEN>`. That token is separate from `COS_OPERATOR_IDENTITY`. See `docs/OPENCLAW_CONNECTION.md`.

Text reasoning can run only for concept generation and story-development audit, and only against an already frozen context bundle. A configured API key is not permission to spend. `COS_LIVE_TEXT_REASONING_ENABLED` defaults to false. A paid call also needs a human `RunAuthorization` for that bundle id and hash, an explicit `COS_XAI_MODEL` or `COS_OPENAI_MODEL`, and one idempotency key. Those provider values are read from the process environment or from `.env`. A process variable overrides the file. Research, image, posting, and purchasing execution stay disabled. See `docs/V0_3_2_SAFE_EXECUTION.md`.

The company queue at `/company` runs `NEW_CREATIVE_V1` through a manual specialist import. A selected concept can become a pending StoryLock draft. QA reviews that draft and cannot approve it. The run reaches production routing only after a human approves the StoryLock, then stops on reference readiness. See `docs/COMPANY_CONTROL_PLANE.md`, `docs/MCP_INTERFACE.md`, and `docs/WORKFLOW_NEW_CREATIVE_V1.md`.

## What the import preserves

- 15 skills. The imported production-spec-qa text still says “tomorrow”
- A working production-spec-qa version whose GOOD example says “today”, without changing the snapshot
- The current Target story lock, whose floating hook is “today” and whose total is $19.23
- 19 regression cases
- Supplemental visual hashes, dimensions, and only the relationships the notes state

Creative values come from the current approved story lock. A human correction appends a version and records approval. Only deliverables whose declared field dependencies intersect the change go stale. Reusable bases and ingredients stay current. See `docs/V0_2_INTEGRITY_HARDENING.md`, `docs/V0_2_1_TRUST_CONTEXT.md`, `docs/V0_3_CONTEXT_FIDELITY.md`, `docs/V0_3_1_CREATIVE_SELECTION.md`, and `docs/V0_3_2_SAFE_EXECUTION.md`.

Prepare the first live smoke task without calling a provider:

```bash
creative-os prepare-smoke-tests
```

A context bundle freezes a creative task plus the authoritative context. Export the provider packet without calling a model:

```bash
creative-os export-context-bundle <bundle_id> --format markdown
creative-os export-context-bundle <bundle_id> --format json
```

The manual evaluation packets are in `evaluation/model_transfer_v1/`. `REVIEWER_RUBRIC.md` stays out of those packets. Import the recorded scores with `creative-os import-evaluations`. Those rows are external evaluations, not provider executions.

`creative-os apply-baseline` also clears a product identifier when the current lock text says that identifier belongs to a superseded model. It does not invent a replacement id.
