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
ruff check src tests
ruff format --check src tests
mypy src
pytest
```

## What the import preserves

- 15 skills. The imported production-spec-qa text still says “tomorrow”
- A working production-spec-qa version whose GOOD example says “today”, without changing the snapshot
- The current Target story lock, whose floating hook is “today” and whose total is $19.23
- 19 regression cases
- Supplemental visual hashes, dimensions, and only the relationships the notes state

Creative values come from the current approved story lock. A human correction appends a version, records approval, and marks assets bound to the previous version stale. It does not rewrite the old version.

Provider execution is stubbed and returns `NOT_IMPLEMENTED`.
