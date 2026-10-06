# AUTHORITY & PRECEDENCE (highest first)
1. Human explicit correction (Tyrel, most recent) wins over everything, then gets written into the lock or skill.
2. Latest human-approved STORY_LOCK (outputs/<story>_vN/STORY_LOCK.md; currently .../chore_stuff_target_20261005_v4/STORY_LOCK.md)
3. Active system skill (/home/box/agent-data/workflows/*/SKILL.md)
4. Approved account/profile configuration. NONE exists as a file today; it lives in memory and chat (see ACCOUNT_STATE_TODAY.md).
5. Reference-bank evidence (target-reference-bank-v2, dd_step_refs, user-supplied screenshots)
6. Current generated asset (finals listed in the lock)
7. Older story lock / earlier versions
8. Memory note
9. Old generated asset (anything in STALE_ASSETS.md or earlier vN folders)
10. Deprecated skill/rule (see SYSTEM_MANIFEST known_deprecated_rules)
11. Historical example (benchmarks, golden examples)

## Which source wins, by domain
- Creative truth (story values: dates, times, products, prices, hook text, item list): 1 > 2. Assets, memory and references never override the lock.
- System behavior (how stages run, gates, routing): 1 > 3. Memory may hold newer human rules not yet in a skill. Treat those as 1 until codified.
- Visual structure (layout, type, spacing, UI behavior, row heights): 5 (Reference Is Law) > generation. The exception is story-specific values (time, date, items, amounts), which come from 2.
- Research facts: real sources only. Staged content is never a fact. Live retailer checks beat cached snippets.
- Account preferences: 1 > memory/chat (no config file exists).
- Production values (resolution, format, base choice): 3 (production-spec-qa: 9:19.6, base-first) > older docs (SYSTEM_PLAYBOOK, HANDOFF_*.md, getting-started all mention stale 1080×1920).
## Stale handling
When a locked field changes, list the affected assets in the lock and in STALE_ASSETS.md as "STALE — REPRODUCTION REQUIRED". Never delete files or rewrite history unless asked.
## Overlapping-authority hazards
SYSTEM_PLAYBOOK.md, CATCHUP.md, HANDOFF_LATEST.md and HANDOFF_2026-09-26.md predate the 2026-10-05 changes. They are historical and lose to the skills and the lock.
