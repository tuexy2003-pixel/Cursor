# CURRENT MANUAL WORKFLOW (as it actually runs today; one story-led creative)
"Grok" means the Grok Bot agent (an LLM) reading the markdown skills. There is no orchestrator: each stage is a chat turn that Tyrel authorizes.

| # | Stage | Trigger | Performed by | Inputs / files read | Outputs / files written | Human decision | What can fail → recovery | Next |
|---|---|---|---|---|---|---|---|---|
| 1 | Research (optional) | Tyrel's authorization message ("RUN …") | Grok + scout skills; web search; TikTok scrapers (ScrapeCreators/Apify); computer-use browser | scout SKILL.md, viral-story-learning/*.md | shared/research/<run>/ *.md/*.json cards | yes, scope set by Tyrel | Wrong life-world, fabricated evidence → Tyrel rejects; rerun narrower | 2 |
| 2 | Concept generation | Tyrel ("GENERATE N CONCEPTS") | Grok via synthetic-story-generator → commercial-aware-synthesis → adaptation-blitz-match | pattern banks, Family D cards, gate skills | premise/concept cards in chat or shared/research/ssg-*/ md | yes | Adult/generic, commerce-first, contrived → reject, regenerate | 3 |
| 3 | Concept selection/lock | Tyrel picks | Human | concept cards | lock noted in chat + memory | MUST | n/a | 4 |
| 4 | Surface + transaction spec | Tyrel authorization | Grok; reference bank lookup | target-reference-bank-v2, dd_step_refs | ssg-orchestration-test/BENCHMARK_SURFACE_TRANSACTION_SPEC.md, *_MATH_SPEC.md | yes | Fake UI fields, wrong math → fix | 5 |
| 5 | Story development: Pass 1 propulsion | after lock | Grok + story-development skill | concept, spec | draft STORY_LOCK sections (hook, trigger, action, expected consequence, reveal) | review | Hook without trigger → smallest causal beat repair | 6 |
| 6 | Pass 2 viral texture / comment surfaces | after P1 | Grok + skill; occasional product research (web) | retailer pages | micro-details 0–3/slide, comment-door map | review | Random or ad-like details, discount filler → firewall drop | 7 |
| 7 | Pass 3 continuity | after P2 | Grok + skill | all slide facts | ledger, state-transition check, story date | review | Tomorrow/today conflict, stale ref date → change the smallest field | 8 |
| 8 | STORY_LOCK | after P1–P3 | Grok writes; Tyrel approves | — | outputs/<story>_vN/STORY_LOCK.md | MUST | Later correction → edit lock, list STALE assets (STALE_ASSETS.md) | 9 |
| 9 | Commerce integration | inside the lock | Grok | math spec | economics block (subtotal, mydashperks.com discount, tax, total) labeled FICTIONAL/STAGED | MUST (economic premise) | Shock discount, headroom item → reject | 10 |
| 10 | Production routing | per slide | Grok + production-spec-qa router | lock, skill | route per region (A message / B commerce UI / C camera-roll / D scene), S1 hook gate | optional | Wrong route (generate when base exists) → reroute | 11 |
| 11 | Visual acquisition | route B/C | Grok → computer-use subagent (box browser): Pinterest, Google Images, retailer sites; visual-surface-acquisition skill | queries | candidate refs saved under shared/research/<topic>/ or outputs/.../refs | yes, if ambiguous | Long queries return nothing → short queries; unknown rights → REFERENCE ONLY | 12 |
| 12 | UI base selection | route A/B | Grok; Tyrel sometimes supplies his own screenshot (preferred) | reference bank, templates | chosen base path recorded in lock/QA | yes, when ambiguous | Base can't fit rows → pick another base, never squeeze | 13 |
| 13 | Image editing | per slide | computer-use subagent drives chatgpt.com (signed-in box browser), uploads BASE + INGREDIENTS with a literal edit prompt | base png, ingredient photos | downloaded png in outputs/<story>_vN/ | no | Drift, text errors, no image → resend once; refusal → stop and show Tyrel; redo from ORIGINAL base | 14 |
| 14 | Camera-roll production | route C | same as 13, using a Pinterest REFERENCE + product photos; or an edit of a cleared base | refs | s3_*.png | no | AI-perfect look, wrong product → re-edit from original | 15 |
| 15 | Deterministic touch-ups (rare) | small defect | Grok via Python/PIL on the box | png | png (disclosed) | no | n/a | 16 |
| 16 | Production QA | each asset | Grok + production-spec-qa (story-dev mirror, continuity mirror), visual inspection via Read | lock, asset | pass/fail notes in chat; sometimes QA_*.md | no | Fail → back to 13 | 17 |
| 17 | Human review | delivery | Tyrel in chat | pngs | approve or corrections | MUST | Correction → lock update → stale → reproduce | 18 |
| 18 | Final approval / posting | Tyrel | Human, posting manually on TikTok (not done by the bot) | finals | — | MUST | — | end |
Performance data: Tyrel reports numbers in chat. Grok stores them in memory or md (account_review_20261002.md). There is no ingestion.
