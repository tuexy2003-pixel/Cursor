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

The API binds to loopback by default and has no authentication. `COS_API_HOST` must stay `127.0.0.1`, `localhost`, or `::1`. Any other host refuses to start. Remote mutation routes are not supported until operator authentication exists. Provider code cannot approve a story lock. Human approval uses `COS_OPERATOR_IDENTITY`, not an `actor` string from request JSON.

Provider execution still returns `NOT_IMPLEMENTED`.

## What the import preserves

- 15 skills. The imported production-spec-qa text still says “tomorrow”
- A working production-spec-qa version whose GOOD example says “today”, without changing the snapshot
- The current Target story lock, whose floating hook is “today” and whose total is $19.23
- 19 regression cases
- Supplemental visual hashes, dimensions, and only the relationships the notes state

Creative values come from the current approved story lock. A human correction appends a version and records approval. Only deliverables whose declared field dependencies intersect the change go stale. Reusable bases and ingredients stay current. See `docs/V0_2_INTEGRITY_HARDENING.md`, `docs/V0_2_1_TRUST_CONTEXT.md`, and `docs/V0_3_CONTEXT_FIDELITY.md`.

A context bundle freezes a creative task plus the authoritative context. Export the provider packet without calling a model:

```bash
creative-os export-context-bundle <bundle_id> --format markdown
creative-os export-context-bundle <bundle_id> --format json
```

The manual evaluation packets are in `evaluation/model_transfer_v1/`. `REVIEWER_RUBRIC.md` stays out of those packets.

Provider execution is stubbed and returns `NOT_IMPLEMENTED`.
