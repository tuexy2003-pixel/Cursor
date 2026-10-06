---
name: Live Heat Scout
description: >-
  Use before commercial-aware synthesis as the third independent scout feed.
  Finds what is currently circulating in live consumer culture (objects,
  behaviors, arguments, methods, moments, price phenomena) and returns
  VALIDATION_CARD heat cards. Does not invent concepts, discounts, or commercial
  premises; does not gate Story or Object findings.
---
# Live Heat Scout

## When to use
Before commercial-aware synthesis, in the same scout phase as Story & Conflict Scout and Object & Culture Scout. This skill finds **what is currently circulating** as live consumer/cultural heat and returns heat cards as a **third independent feed**.

It does **not** replace Story & Conflict, Object & Culture, commercial-aware synthesis, V1.1, V1.2, gates, adversarial research, or QA. It does **not** invent concepts, discounts, promotional amounts, storyboards, or MyDashPerks premises. Heat is **currentness evidence (input)**, not a viral gate.

Authoritative design (do not redesign during a run):
- Spec: `/workspace/creative-pipeline/shared/research/live-heat-scout-spec/FINAL_PROPOSED_LIVE_HEAT_SCOUT_SPEC.md`
- Query Hygiene (Apify / TikTok retrieval policy): `QUERY_HYGIENE_PLAYBOOK.md` in this skill folder (copy of the research playbook).

## Architecture position
```
Story & Conflict Scout  ─┐
Object & Culture Scout  ─┼─→  Commercial-aware synthesis
Live Heat Scout         ─┘     (third independent feed)
```

Synthesis orchestration may supply Live Heat cards externally. This skill does **not** require editing commercial-aware synthesis.

## Heat is not a gate
- No Live Heat finding is required for a Story or Object finding to remain useful.
- No concept must be based on a trend.
- Thin Live Heat is valid.
- **Zero VALIDATION_CARD cards is a successful possible outcome.**
- Live Heat cannot veto Story/Object findings merely because they are not currently hot.
- No universal viral score, creator-count law, comment-percentage law, or fake-scientific threshold.

## Responsibility boundary
| Owns | Does not own |
|------|----------------|
| What is *currently circulating* as culture heat | Plot writing |
| Discovery → mining → validation of live phenomena | Object-world breadth for its own sake |
| STRENGTHEN / WEAKEN of magnitude claims when native evidence is available | Commercial premise composition |
| Observing price/deal/dupe/restock/method/discount discourse as evidence | Deciding residual space, ownership, promo amounts, cheaper-same-outcome, viewer-state economics |

Overlap with Object & Culture is allowed. Keep provenance separate. Do not merge the jobs.

## Heat archetypes
One primary; optional secondary. Exact set only:
**OBJECT · BEHAVIOR · ARGUMENT · METHOD · MOMENT · PRICE**

Prefer the archetype that matches *why people care right now*, not the product category.

## Discovery channels (A–E)
All are complementary entrances into the same pattern. Do **not** solve Live Heat with endless phrase dictionaries.

| ID | Channel | Role |
|----|---------|------|
| A | Language probes | Colloquial show/try/hunt/method/price/argument/freshness — entrances, not infinite dictionaries |
| B | Category / world sweeps | Breadth across consumer worlds — strongest novelty engine in experiments |
| C | Retailer / community feeds | Sneak peeks, community language |
| D | Platform-native / proxies | Trends aggregators best-effort; corroborates more than discovers |
| E | Result Mining | **Required.** Extract unknowns from results → entity/behavior queries → second evidence |

**Balance:** scarcity + price families are a **minority** of initial probes (~≤15%). Positive/show is useful for inventory but weaker for novelty; do not let it dominate. Give category/world sweeps real budget.

**Banned starting seeds:** Do not open with famous defaults (iPad, MacBook, AirPods, Coach, Dyson, Labubu, Trader Joe's mini tote, close variants). If they appear organically, quarantine — do not prefer or expand by default.

## Core pattern (mandatory)
```
BROAD WORLD OBSERVATION
  → ENTITY / BEHAVIOR MINING (from results, not seed paraphrase)
  → QUERY EXPANSION (result-derived)
  → VALIDATION (second independent evidence; optional Apify)
```
Rephrasing the seed is **not** mining. Extracting a new proper noun or named ritual is.

## Discovery mode vs Validation mode

### Discovery mode
**When:** No crisp named entity/behavior yet.
**Allowed:** Candidate vocabulary — product names, challenges, ingredients, LTOs, hashtags, brand mentions, slang — plus noise-class notes (affiliate / ad / collision / promo / stale).
**Forbidden:** STRENGTHEN/WEAKEN or heat proof from broad SERP engagement alone.
**Output class:** `MODE = DISCOVERY_VOCABULARY_ONLY`

### Validation mode
**When:** Entity / challenge / ingredient / LTO already named.
**Query shape:** Most discriminating string available (exact challenge name; ingredient + domain; brand+SKU; descriptive alias if exact code collides).
**Evidence (qualitative):** topical relevance first; recency; creator/source diversity; replication across contexts; organic vs paid vs affiliate labels; native vocabulary when available.
**Output class:** may become `MODE = VALIDATION_CARD` only after validation.

```
IF named entity known → VALIDATION (entity-first)
ELSE → DISCOVERY → IF candidate survives noise labels → VALIDATION
NEVER promote Discovery SERP metrics to Validation heat judgment
```

## Synthesis handoff type boundary (mandatory)
- **Only `MODE = VALIDATION_CARD`** may enter a future commercial-aware synthesis heat-card handoff.
- **`MODE = DISCOVERY_VOCABULARY_ONLY` must NEVER** be passed as validated Live Heat evidence.
- Discovery vocabulary may stay in working output, a discovery appendix, provenance trail, or candidate list for later expansion.
- This is a **type boundary**, not a new creative gate.

## Result-mining loop
1. Run Channel A–D probes without naming the hoped-for entity.
2. Extract unknown terms from results.
3. Cluster aliases into phenomena.
4. Expand **unexpected** unknowns (prefer novelty over famous defaults).
5. Seek **second independent evidence**. Reject syndication mirages (many blogs, one TikTok).
6. Cap **one child branch** per parent.
7. Promote survivors to VALIDATION_CARD; leave promising-but-obvious seasonal items labeled, not forced into cards.

## Relevance gate (before metrics)
For each evidence item label **TOPICAL | OFF_TOPIC | UNCLEAR** against the named entity/behavior/ingredient.
1. Drop OFF_TOPIC from all metric pools.
2. High UNCLEAR → prefer alias or stop — do not guess.
3. Judge diversity/recency/engagement **only on TOPICAL** set.
4. Sparse authentic topical evidence is valid WEAKEN or INSUFFICIENT EVIDENCE — never rescue with off-topic megaviews.

## Organic / paid / affiliate
**Distribution:** ORGANIC | PAID | UNKNOWN (or MIXED with paid-share note).
Never blend ORGANIC + PAID into one engagement story when paid share is material (PDRN regression).

**Ecosystem:** INDEPENDENT ORGANIC REPLICATION | CREATOR-AFFILIATE ECOSYSTEM | BRAND-SEEDED | PAID AD | PROMO CALENDAR | UNKNOWN.
Affiliate describes ecosystem shape and may yield candidates. It does **not** count as independent organic replication for STRENGTHEN. Official promo calendar mechanics are not organic heat.

## Query Hygiene integration
Do **not** rewrite the Query Hygiene Playbook into this skill. For TikTok-native / Apify on-demand retrieval, follow:

**`QUERY_HYGIENE_PLAYBOOK.md`** (this folder)

Minimum rules always in force (web and Apify):
1. Name the question before scraping.
2. Relevance before metrics.
3. Entity-first when the entity is known.
4. Broad queries → vocabulary, not heat proof.
5. Record which query string produced evidence.
6. Keep ORGANIC / PAID / UNKNOWN separated.
7. Keep independent replication / affiliate / brand-seeded distinguishable.
8. Related search = query ideas, never heat evidence.
9. Comments only for a named unresolved question.
10. Escalate spend only to close a named information gap.
11. Collision checks for short/ambiguous strings.
12. On-demand ≠ always-on.

Detailed recipes (T01–T13) and full regression tables live in the playbook.

## Apify policy (optional)
| Decision | Value |
|----------|-------|
| Overall Apify value | **MODERATE** |
| On-demand under Query Hygiene | **YES** |
| Permanent connect | **NOT YET** |

**Role:** TikTok-native **validation / correction** (tightly scoped discovery→candidates only when specifically justified). Not the primary discovery brain, not always-on, not a firehose, not a viral-score engine, **not a mandatory dependency**.

**Live Heat must function correctly WITHOUT Apify.**
Invoke Apify only when **both** are true:
1. The capability is available, and
2. A **named unresolved TikTok-native question** justifies it (e.g. independent creator replication; current vs old residue; web overstating TikTok heat; mostly paid?; native vocabulary; named behavior spreading?).

If Apify is unavailable or not used: **do not fail the run.** Record fields as **NOT CHECKED**, **UNTESTED**, **INSUFFICIENT EVIDENCE**, or an explicit blind spot. **Never** fabricate TikTok-native evidence.

Do not permanently connect Apify. Do not scrape merely because budget remains.

## Comments
Default: do not fetch comments.
Fetch only for a named unresolved question (want/buy intent, sourcing, method, availability, skepticism, child variants, watching vs replicating).
If Apify comments are used, follow playbook pack limits. Mark COMMENT_INTENT = NOT CHECKED when skipped.

## Budget / escalation
```
WEB Discovery / Validation first
  → RELEVANCE GATE
  → optional result-derived expansion / alias
  → optional on-demand Apify QUERY1 (entity-first if known; only if available + named question)
  → optional ALIAS scrape
  → optional COMMENT PACK (named unresolved question only)
  → STOP or ONE follow-up entity query
```
Escalate only to close a named gap. Prefer $0 analysis from saved results. No continuous/scheduled spend. One child branch max on the web path.

## Source priority
Prefer independent attestation and dating honesty over volume:
1. Native platform topical evidence (when available)
2. Named primary press with dates + independent corroboration
3. Official brand PR / PDP (existence/LTO/prices — not alone as organic heat)
4. Community feeds
5. Aggregator / SEO / deal blogs (vocabulary; high syndication risk)
6. Related-search / autocomplete (query ideas only)

## Recency and lifecycle
**Recency labels:** LIVE (~7d) · LIVE WINDOW (~30d) · CONTINUING · STALE · UNKNOWN.
Continuing mid-season heat is valid if current evidence exists. Reject stale recycled peaks. Do not invent dates.

**Lifecycle:** NEWBORN · ACTIVE · SCALING/MAINSTREAMING · CONTINUING SEASONAL · FADING · **UNKNOWN** (allowed). Descriptive input, not a kill switch.

## Heat card schema
```
HEAT CARD
- NAME:
- ARCHETYPE_PRIMARY: OBJECT | BEHAVIOR | ARGUMENT | METHOD | MOMENT | PRICE
- ARCHETYPE_SECONDARY: (optional)
- WHAT_IS_HAPPENING:
- WHY_PEOPLE_CARE:
- ORIGIN: channel (A–E) · seed · raw extract · expansion query(ies)
- MODE: VALIDATION_CARD | DISCOVERY_VOCABULARY_ONLY
- FIRST_OBSERVED: <date or UNKNOWN>
- MOST_RECENT_EVIDENCE: <date + source>
- LIFECYCLE: <label or UNKNOWN>
- RELEVANCE: topical / collision notes
- DISTRIBUTION: ORGANIC | PAID | MIXED | UNKNOWN
- ECOSYSTEM: INDEPENDENT ORGANIC REPLICATION | CREATOR-AFFILIATE ECOSYSTEM | BRAND-SEEDED | PROMO CALENDAR | UNKNOWN
- REPLICATION: qualitative note | NOT OBSERVED
- COMMENT_INTENT: summary | NOT CHECKED | INSUFFICIENT EVIDENCE
- PLATFORM_MAGNITUDE: STRENGTHEN | WEAKEN | UNTESTED | INSUFFICIENT EVIDENCE
- CROSS_PLATFORM: short note
- CONFIDENCE: HIGH | MED | LOW
- EVIDENCE: [{source, date, what it supports}]
- UNRESOLVED: [fields still open]
```
Legal values on hard fields include **NOT OBSERVED**, **NOT CHECKED**, **INSUFFICIENT EVIDENCE**, **UNKNOWN**. No fake percentages. No numeric viral score.

**Confidence:** HIGH = multiple independent topical sources + clear dating + replication observed (or native multi-creator proof). MED = multi-source with known blinds (default when blinds exist). LOW = single cluster or heavy caveats.

## Existing commercial conversation
Observe; do **not** auto-reject. Record as ecosystem evidence. Do not drop a phenomenon solely because affiliates or brands are present. Do not treat affiliate roundups or ad-heavy SERPs as independent organic replication. Official promo calendar → not organic heat (may note as MOMENT/PROMO awareness only).

Live Heat may **observe** price/deal/dupe/restock/method/discount discourse. It may **not** decide economic ownership, residual space, campaign discounts, promotional amounts, cheaper-same-outcome, or viewer-state economics. Those stay downstream.

## Zero-result behavior
Zero VALIDATION_CARD cards is success-compatible. Record probes + noise classes. Do not force a card. Do not burn budget paraphrasing near-null probes. Hand empty/thin Live Heat onward; Story and Object may still carry the run. Optional DISCOVERY_VOCABULARY appendix without promotion.

## Stop conditions
Stop when: decision reachable · collision resolved (exact + one alias) · discovery vocabulary captured · near-null language probe · related-search pollution · comment skip justified · budget ladder exhausted · candidate too weak · stale dating · syndication mirage.

## Anti-bias
Breadth before depth. Do not seed banned famous defaults. Cap scarcity/price probe share. Positive/show ≠ automatic novelty. Category sweeps get real budget. Result mining required. Syndication ≠ multi-source. Dating honesty. Seasonality awareness. Confirmatory Apify ≠ discovery. Do not prefer library-anchored objects merely because assets exist.

## Permanent regressions (authoring consistency — do not execute paid tests)
| Case | Required behavior |
|------|-------------------|
| Lunch in My City | Named challenge validation; forbid validating via `copied their order` |
| PDRN | Entity ingredient query; mandatory ORGANIC/PAID split |
| KUSTFYR | Collision fail before metrics; descriptive alias; WEAKEN magnitude if authentic reach sparse |
| new restaurant menu / The Menu | Discovery vocab only; discard movie related-search pollution |
| copied their order | Near-null ≠ behavior absent; switch to named challenge |
| home finds | Affiliate ecosystem; discovery vocabulary; not heat proof from category SERP |
| Free Mod Monday | Promo calendar → not organic heat |
| Lowe's pink buckets | Stale → reject for live heat |
| Chipotle rice hack | Syndication mirage → reject |
| Banned calibration seeds | Quarantine organic appearance; do not expand |

## Forbidden
- Modify V1.1, V1.2, Story & Conflict, Object & Culture, commercial-aware synthesis, gates, or QA from this skill.
- Install viewer-state / commercial-information transformation.
- Permanently connect Apify; always-on or firehose scraping.
- Use Live Heat as a pipeline gate or invent viral thresholds.
- Pass DISCOVERY_VOCABULARY_ONLY as synthesis heat evidence.
- Fabricate TikTok-native evidence when Apify is unavailable.
- Invent MyDashPerks economics, promo amounts, or residual-space decisions.
- Generate campaign concepts or start Run 6 from this skill alone.

## Handoff package
1. **VALIDATION_CARD** heat cards only (synthesis-facing).
2. Optional appendix: DISCOVERY_VOCABULARY_ONLY + noise notes (not synthesis evidence).
3. Corrections log (STRENGTHEN/WEAKEN vs prior web claims).
4. Blinds list (NOT CHECKED / UNTESTED / NOT OBSERVED).
5. Explicit statement: heat is input; thin/empty heat does not block synthesis.

## Future experiment note (not installed)
Viewer-state / commercial-information transformation is a **separate** research track. Do not wire it into this skill or into V1.2.
