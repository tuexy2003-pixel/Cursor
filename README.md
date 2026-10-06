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
creative-os serve
```

Reset the local SQLite database and import again:

```bash
creative-os reset-db --seed
```

Operator UI:

```bash
cd apps/web
npm install
npm run dev
```

The UI expects the API at `http://127.0.0.1:8000`. Override with `NEXT_PUBLIC_API_BASE`.

## Checks

```bash
ruff check src tests
ruff format --check src tests
mypy src
pytest
```

## What the import preserves

- 15 skills, including the production-spec-qa example that still says “tomorrow”
- The current Target story lock, whose floating hook is “today” and whose total is $19.23
- 19 regression cases
- Asset-index metadata without inventing missing binaries or rights

Creative values come from the current approved story lock. A human correction appends a version, records approval, and marks assets bound to the previous version stale. It does not rewrite the old version.

Provider execution is stubbed and returns `NOT_IMPLEMENTED`.
