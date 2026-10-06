# ENGINEERING INVENTORY
VERY LITTLE EXECUTABLE CODE DRIVES THE CURRENT PIPELINE. The system is markdown skills interpreted by an LLM agent, plus manual image editing through the ChatGPT web UI. There is no package, CLI, service, test suite, database, Dockerfile or Makefile for the creative pipeline. The scripts that do exist are one-off or legacy renderers and research utilities. Copies are in engineering_source/ (same relative paths under /workspace/creative-pipeline/).

| Path | Type | Purpose | Used now | Called by | Depends on | Input → Output | Side effects | Safe to modify |
|---|---|---|---|---|---|---|---|---|
| outputs/_tools/build_imessage_ios26.py | py CLI | Deterministic iOS 26 dark Messages screenshot renderer from spec.json | NO (finals now edit the real keyboard base in ChatGPT); possible fallback | Grok manually | Pillow, fonts | spec.json → png (1080×1920 + native 1206×2622) | writes png | YES |
| assets/phone_plates/composite_on_plate.py + quads.json + sr_cache.py | py CLI | Composite flat screen onto Tyrel's phone photos (plates) | NO/UNCLEAR (legacy 1080×1920) | manual | opencv, numpy, Pillow | plate name + screen png → slide png | writes png | YES |
| assets/phone_plates/_w/*.py | py | Quad fitting / rectify utilities | NO | manual | opencv | — | — | YES |
| _catchup_work/{stage.py,gen.py,patch.py,mkzip.py,setup.sh,smoke_test.sh,requirements.txt} | py/sh | Builds a portable CATCHUP bundle (copies sources, venv, smoke test) | NO (one-off export, ~late Sept) | manual | requirements.txt | repo → zip | writes _catchup_work/stage | YES |
| outputs/proof_cand01_s2/_work, _w2/*.py | py | Legacy deterministic DoorDash Order Complete rebuild (font match, rows, composite) | NO (freehand UI rebuild is now forbidden for finals) | manual | Pillow/opencv | base png → png | — | YES |
| outputs/cand0*/_w/*.py, cashcard*.py | py | Per-candidate legacy builders (McD, Wingstop, Cheesecake, Chipotle, Cash Card) | NO | manual | Pillow | spec → png | — | YES |
| outputs/*/_w*/chat_spec*.json, dre_spec.json | json | Specs for the iMessage renderer | NO | build_imessage_ios26.py | — | — | — | YES |
| logs/creative-tests.jsonl | jsonl | Early creative test log (cand05/cand06 Dre format) | NO (stale) | manual | — | — | — | YES |
| shared/research/hooks-tutpinned-*/sc.sh, merge.py, summ.py | sh/py | ScrapeCreators TikTok keyword pulls + merge/summarize | occasional research | manual | curl, SCRAPECREATORS_API_KEY | keywords → raw/*.json, top_posts.csv/json | network API spend | YES |
| shared/research/commercial-occupation-diagnostic/_w/{build,corpus}.py | py | Diagnostic corpus build | NO (one-off) | manual | — | — | — | YES |
| shared/research/apify-instrumentation-test/*.json | json | Apify run inputs, outputs, cost log, decisions | NO (test) | — | APIFY_TOKEN | — | — | YES |
| shared/research/benchmark-run6/*_SUMMARY.json | json | Run 6 scout summaries | reference | — | — | — | — | NO (evidence) |
| _examples_stage/EXAMPLES/source_cards/cards/*.json | json | Historic source-card instances (de facto schema) | reference | source-card skill | — | — | — | WITH CARE |
| specs/spec_draft_20260923_cand01_dinner_handled.json | json | Early carousel spec draft | NO | — | — | — | — | YES |
| /home/box/agent-data/workflows/*/SKILL.md | md | THE ACTIVE LOGIC (LLM-interpreted) | YES | Grok | — | — | — | NO without authorization |
| outputs/<story>_vN/STORY_LOCK.md | md | Authoritative story record | YES | story-development | — | — | — | via human approval only |
Ad hoc: during production Grok writes throwaway Python/PIL snippets inline (dimension checks, a 14px emoji nudge, contact sheets). These aren't saved as files.
