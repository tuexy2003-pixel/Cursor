# TOOL & PROVIDER MAP (no secrets)
| Tool/provider | Role | When | Input → Output | Strength | Known failure | Replaceable | Context needed if replaced |
|---|---|---|---|---|---|---|---|
| Grok Bot (LLM agent, this bot) | Creative intelligence + orchestration; reads skills, writes locks/specs/QA | every stage | chat + md → md/json, tool calls | nuanced judgment, follows prose skills | drift to stale memory, verbosity, forgets newer corrections | yes with care | all ACTIVE skills, current lock, MEMORY_ONLY_KNOWLEDGE, precedence rules |
| Teammate bots (Discovery, Slide Exec, Production) | Older role split (source cards / slide ordering / production QA) | historical; UNCLEAR today | messages → md | — | UNCLEAR | yes | their descriptions |
| ChatGPT web image editing (chatgpt.com, signed in on box browser) | Localized image edits on BASE + INGREDIENT, aspect changes, scene creation from REFERENCE | production | pngs + literal prompt → png | best native-looking edits | text errors, drift, no image returned, policy refusals, ~50 imgs/3h | yes | base pixels, ingredient photos, exact "change only" prompt, re-edit-from-original rule |
| computer-use subagent (box desktop, 1280×800) | Drives ChatGPT, Pinterest, retailer sites, DoorDash cart | acquisition/production | task text → files/screens | uses real logged-in sessions | slow, loops, one at a time | yes (Playwright etc.) | logins, stop rules (never checkout/send) |
| Pinterest (box browser) | Camera-roll/real-life visual search | route C | short query → pin images | organic real photos | long queries empty; rights unknown | yes | REFERENCE ONLY rule |
| Google Images / web search | Product photos, packaging, live prices | INGREDIENT acquisition, product checks | query → image/URL | real product pixels | cached/stale results | yes | "check live retailer" rule |
| Target / DoorDash apps and sites | Live price, product generation, UI references; Tyrel's own screenshots | spec + production | — | ground truth | marketing composites ≠ app UI | no (source of truth) | — |
| ScrapeCreators API (env SCRAPECREATORS_API_KEY) | TikTok search/scrape for research | research runs (hooks-tutpinned, probes) | keyword → JSON | bulk data | cost, rate limits | yes | query sets in sc.sh |
| Apify (env APIFY_TOKEN; clockworks TikTok actor) | Instrumented TikTok scraping test | apify-instrumentation-test | input JSON → items JSON | structured | cost (cost_log.json) | yes | decisions.json |
| Fish Audio (env FISH_API_KEY) | Voice; not used in the carousel pipeline (UNCLEAR) | — | — | — | — | — | — |
| Python3 + Pillow/numpy/opencv (box) | Deterministic checks, small nudges, composites, contact sheets, legacy renderers | QA/touch-up | png → png/metrics | exact, reproducible | legacy renderers produced fake-looking UI (now retired for final UI) | yes | — |
| Filesystem (/workspace, /home/box/agent-data) | All state | always | — | simple | no versioning/provenance | yes | path map (CONFIG_AND_ENVIRONMENT.md) |
| Agent memory (off-box) | Durable facts and preferences | always | — | persistence | stale facts resurfacing | yes | MEMORY_ONLY_KNOWLEDGE.md |
No single provider owns the system. Skills (markdown) + locks + reference banks are the portable core.
