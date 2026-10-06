# QUERY-HYGIENE PLAYBOOK — Apify TikTok as On-Demand Live Heat Tool

**Status:** Operational playbook (not a Live Heat install; not a permanent connect)  
**Evidence base:** Apify instrumentation experiment only (`FINAL_REPORT.md`, `SUMMARY.md`, `decisions.json`, Arm A/B saved datasets)  
**Experiment date:** 2026-10-05 EDT · **Spend:** $1.128 / $5.00 · **Actor:** clockworks/tiktok-scraper  
**Overall Apify value (unchanged):** **MODERATE**  
**Permanent connect (unchanged):** **NOT YET**  
**On-demand availability:** Decided in §§15–17

**Non-goals of this document:** viral scores, giant numeric heat thresholds, databases, continuous monitoring, more APIs, more seed families, new creative gates, concept generation, installing Live Heat, modifying V1.2, starting Run 6, or running new paid Apify scrapes.

**Accepted premise (user):** Apify is stronger as TikTok-native **VALIDATION / CORRECTION** than as blind discovery.

---

## 1. QUERY-HYGIENE PRINCIPLES

Interpretable rules. No fake precision.

1. **Name the question before you scrape.** Every Apify call answers a named Live Heat question (validate entity X; correct magnitude claim Y; check whether behavior Z is native). No open-ended firehose.
2. **Relevance before metrics.** Filter topical relevance **before** median plays, creator diversity, engagement, or any heat judgment. Off-topic megaviews (KUSTFYR streamer collision) must never enter the numerator.
3. **Entity-first when the entity is known.** Do not use a broad discovery query to validate a named phenomenon if a cleaner entity query exists. Arm B category/language seeds missed Lunch, PDRN, and KUSTFYR; Arm A entity queries decided them.
4. **Broad queries produce vocabulary, not heat proof.** Discovery-mode engagement on `home finds` / `trending beauty products` is ecosystem noise until an entity is isolated and re-queried.
5. **Record which string produced evidence.** Alias expansions come only from known evidence; log the winning alias (see §5).
6. **Split ORGANIC / PAID / UNKNOWN before interpreting engagement.** PDRN was 50% ads — permanent regression for unlabeled aggregates.
7. **Affiliate is a label, not an auto-reject.** Home-finds sludge is informative about ecosystem shape; do not treat Amazon/Temu roundups as independent organic replication without evidence (§8).
8. **Related search = query ideas, never heat evidence.** Topical relevance required. *The Menu* movie pollution is the regression case (§9).
9. **Comments only for named unresolved questions.** Default = skip. Experiment skipped comments at $0 when captions/authors sufficed (§10).
10. **Escalate spend only to close a named gap.** Prefer QUERY1 → relevance → optional alias → optional comment pack → stop or one follow-up. Experiment total $1.128 proved the pattern (§11–12).
11. **Collision detection is mandatory for short/ambiguous strings.** Homographs, creator usernames, film titles, and generic English phrases fail silently if unchecked (§7).
12. **On-demand ≠ always-on.** This playbook authorizes scoped validation/correction calls. It does not authorize continuous monitoring or permanent wiring.

---

## 2. DISCOVERY MODE VS VALIDATION MODE

### Discovery mode

| Rule | Detail |
|------|--------|
| **When** | No crisp named entity yet; exploring a category/language surface for *candidate vocabulary only* |
| **Query shape** | Broad allowed (`home finds`, `trending beauty products`, retailer haul language) |
| **Output allowed** | Candidate product names, hashtags, phrases, brand mentions, SKU strings worth a later entity query |
| **Output forbidden** | Treating broad SERP engagement, play medians, or ad-boosted beauty clips as heat proof for a named phenomenon |
| **Evidence bar** | Vocabulary list + notes on noise class (affiliate / ad / collision). No STRENGTHEN/WEAKEN card from discovery alone |
| **Experiment anchor** | Arm B: returned MagFlow-adjacent tech, brown mascara, POV brand, Dollar Tree finds, P.F. Chang’s LTO — listed as handoff only; **none elevated to SUPPORTED heat cards** |

### Validation mode

| Rule | Detail |
|------|--------|
| **When** | Entity / challenge / ingredient already named (usually from web Live Heat or a discovery candidate that earned an entity check) |
| **Query shape** | Most discriminating query available (exact challenge name; ingredient + domain; brand+SKU; descriptive alias if exact code collides) |
| **Evidence =** | Recency (last ~30d window), creator diversity, replication across contexts, organic vs paid split, native vocabulary (hashtag method text, captions), **and** relevance gate pass |
| **Do not** | Use discovery queries to validate a named phenomenon if a cleaner entity query exists |
| **Experiment anchor** | Arm A: Lunch **STRENGTHEN**, PDRN **STRENGTHEN** (ad caveat), KUSTFYR **WEAKEN** (collision + low authentic reach) |

### Mode switch rule

```
IF named entity known → VALIDATION (entity-first)
ELSE → DISCOVERY (broad → candidates only) → IF candidate survives noise labels → VALIDATION entity query
NEVER promote Discovery SERP metrics to Validation heat judgment
```

---

## 3. QUERY-TYPE TAXONOMY

Thirteen types. **Not merged:** experiment outcomes differ enough (collision vs clean challenge vs ad-dense ingredient vs affiliate category vs movie-polluted menu vs failed copy-language) that collapsing would hide failure modes.

| ID | Type | Experiment exemplar | Instrument quality (observed) |
|----|------|---------------------|-------------------------------|
| T01 | EXACT_SKU_OR_CODE_NAME | `KUSTFYR` | Poor (homograph / creator-name collision) |
| T02 | DESCRIPTIVE_PRODUCT_ALIAS | `IKEA ghost lamp` | Fair (better topical; lamp-generic noise) |
| T03 | NAMED_CHALLENGE_OR_RITUAL | `Lunch in My City` | Excellent |
| T04 | INGREDIENT_CLUSTER | `PDRN skincare` | Good (ad contamination) |
| T05 | CATEGORY_HOME_FINDS | `home finds` | Ecosystem / affiliate-heavy |
| T06 | CATEGORY_BEAUTY_TRENDING | `trending beauty products` | Usable vocabulary; ads present |
| T07 | CATEGORY_RESTAURANT_MENU | `new restaurant menu` | Mixed geo + brand LTOs; related-search movie pollution |
| T08 | CATEGORY_TECH_ACCESSORIES | `personal tech accessories` | Niche SKUs + organic banned-seed risk |
| T09 | RETAILER_HAUL_LANGUAGE | `look what I got Target haul` | Inventory surface; modest reach |
| T10 | COPY_TRY_BEHAVIOR_LANGUAGE | `copied their order` | Near-null for restaurant copy without named challenge |
| T11 | BRAND_PLUS_LTO_OR_NAMED_MENU | P.F. Chang’s Autumn in Kyoto (surfaced under T07) | Prefer over bare “menu” once brand known |
| T12 | CREATOR_BRAND_OR_NAMED_LAUNCH | POV / Point of View by Mikayla (under T06) | Entity-check when creator-brand string known |
| T13 | RELATED_SEARCH_FOLLOWUP | Arm B related words | Query ideas only; high pollution risk on food |

**Mode default:** T01–T04, T11–T12 → Validation. T05–T10 → Discovery (vocabulary). T13 → neither heat mode; ideation only.

---

## 4. QUERY RECIPE FOR EACH TYPE

Default actor inputs (from experiment, unless a named gap requires change): `searchSection=/video`, last ~30 days (`oldestPostDateUnified=30 days`, `videoSearchDateFilter=PAST_MONTH`), `videoSearchSorting=MOST_RELEVANT`, downloads/AI off, `commentsPerPost=0` unless §10 fires. Related words only when §9 allows.

For each type below: PURPOSE · PRIMARY QUERY RECIPE · ALIAS/DISAMBIGUATION RECIPE · WHEN BROAD · WHEN ENTITY-FIRST · EXPECTED NOISE · RELEVANCE CHECK · ORGANIC/AD HANDLING · SECOND QUERY · STOP · RELATED SEARCH USEFUL? · COMMENTS LIKELY ADD VALUE?

---

### T01 — EXACT_SKU_OR_CODE_NAME

| Field | Rule |
|-------|------|
| **PURPOSE** | Validate whether a short product/SKU string has *topical* native TikTok presence (not username/homograph noise). |
| **PRIMARY QUERY RECIPE** | Exact code/name as sold/press-named (`KUSTFYR`). One string. resultsPerPage ≈ 20. |
| **ALIAS/DISAMBIGUATION RECIPE** | Immediately pair with T02 descriptive alias (`IKEA ghost lamp`) and/or brand+code (`IKEA KUSTFYR`) when collision risk is plausible. Record which alias produced topical hits. |
| **WHEN TO USE BROAD QUERY** | Almost never for validation. Broad (`home finds`) will not retrieve the SKU (Arm B: KUSTFYR absent from home finds). |
| **WHEN TO USE ENTITY-FIRST QUERY** | Always when validating this entity. |
| **EXPECTED NOISE** | Creator username collision (`@kustfyr`), unrelated megaviews skewing medians, off-topic same-string hits. |
| **RELEVANCE CHECK** | Caption/hashtag must reference the product context (IKEA / Halloween ghost lamp / packaging). Streamer/gaming/unrelated lifestyle = FAIL before metrics. |
| **ORGANIC/AD HANDLING** | Label isAd/isSponsored if present; for KUSTFYR window ads were not the main failure—collision was. |
| **WHEN TO TRY A SECOND QUERY** | If topical hit rate ≪ majority (experiment: ~1–2/20 topical) → run T02 alias. Optional popularity sort / geo only if a named magnitude question remains. |
| **WHEN TO STOP** | After exact + one alias; if authentic topical reach is sparse/low, WEAKEN magnitude claims; do not keep scraping. |
| **RELATED SEARCH USEFUL?** | Low priority; only if topical posts exist and words stay on-product. |
| **COMMENTS LIKELY ADD VALUE?** | Only if topical videos have meaningful comment volume **and** a named question (e.g. packaging-meme intent). Experiment: topical KUSTFYR comments ≈0–4 → skip. |

---

### T02 — DESCRIPTIVE_PRODUCT_ALIAS

| Field | Rule |
|-------|------|
| **PURPOSE** | Disambiguate colliding SKU codes; recover topical recall when exact name fails. |
| **PRIMARY QUERY RECIPE** | Brand + distinctive object words (`IKEA ghost lamp`). Avoid lone generic (`ghost lamp`, `lamp`). |
| **ALIAS/DISAMBIGUATION RECIPE** | Alternate phrasings from known evidence only (press/PDP vocabulary already in web card). Log winning phrase. |
| **WHEN TO USE BROAD QUERY** | No — broad dilutes further. |
| **WHEN TO USE ENTITY-FIRST QUERY** | Yes; this *is* the entity-first path when T01 collides. |
| **EXPECTED NOISE** | Generic IKEA lamps, lava lamps, unrelated “ghost” content. |
| **RELEVANCE CHECK** | Must match the specific product (viral IKEA Halloween ghost lamp), not any lamp. |
| **ORGANIC/AD HANDLING** | Split if flags present; experiment alias hits were organic but low-play. |
| **WHEN TO TRY A SECOND QUERY** | One alternate alias max if first alias still polluted. |
| **WHEN TO STOP** | After 1–2 alias strings; modest authentic plays = corrective evidence, not a license to dig forever. |
| **RELATED SEARCH USEFUL?** | Sometimes for synonym ideas; gate for topicality. |
| **COMMENTS LIKELY ADD VALUE?** | Same as T01 — only named question + enough comments. |

---

### T03 — NAMED_CHALLENGE_OR_RITUAL

| Field | Rule |
|-------|------|
| **PURPOSE** | Validate multi-creator replication of a named behavior; recover native method text. |
| **PRIMARY QUERY RECIPE** | Exact challenge phrase as used natively (`Lunch in My City`). Prefer the name people tag/search, not paraphrase. |
| **ALIAS/DISAMBIGUATION RECIPE** | Hashtag form (`#lunchinmycity`) only if exact phrase under-retrieves; do not substitute copy-language (T10). |
| **WHEN TO USE BROAD QUERY** | Never for validation. Arm B `copied their order` did **not** retrieve Lunch. |
| **WHEN TO USE ENTITY-FIRST QUERY** | Always. Challenge name is the sharp key (experiment: Excellent). |
| **EXPECTED NOISE** | Low when name is unique; watch for unrelated “lunch” vlogs if phrase truncated. |
| **RELEVANCE CHECK** | Executes or instructs the ritual (search lunch in city → first result → tag restaurant / use hashtag). ~18/20 topical in experiment. |
| **ORGANIC/AD HANDLING** | Expect mostly organic; still label any ads. Experiment ads = 0. |
| **WHEN TO TRY A SECOND QUERY** | Only if first query weak; try hashtag-native string. Do not fall back to T10. |
| **WHEN TO STOP** | After one strong entity query: creator diversity + multi-context replication + method text is enough to STRENGTHEN/WEAKEN. |
| **RELATED SEARCH USEFUL?** | Optional for city/variant vocabulary; not required for heat judgment. |
| **COMMENTS LIKELY ADD VALUE?** | Only for named intent questions (want to try, city variants, skepticism). Default skip if captions already encode method. |

---

### T04 — INGREDIENT_CLUSTER

| Field | Rule |
|-------|------|
| **PURPOSE** | Validate ingredient/material mega-cluster presence; map brand ladder; separate paid vs organic. |
| **PRIMARY QUERY RECIPE** | Ingredient + domain qualifier (`PDRN skincare`). Bare ingredient may over-retrieve medical/unrelated. |
| **ALIAS/DISAMBIGUATION RECIPE** | Brand+ingredient (`Medicube PDRN`) only as follow-up for child SKUs — not as substitute for cluster check. Plant/rice-derived variants only if already evidenced. |
| **WHEN TO USE BROAD QUERY** | Discovery only (`trending beauty products`). Does **not** validate the ingredient (Arm B: PDRN absent from beauty slice). |
| **WHEN TO USE ENTITY-FIRST QUERY** | For STRENGTHEN/WEAKEN of the ingredient claim. |
| **EXPECTED NOISE** | Heavy sponsored density (experiment 10/20 = 50% ads), brand SERp domination. |
| **RELEVANCE CHECK** | Mentions PDRN (or target ingredient) in skincare/makeup context. Experiment topical 20/20. |
| **ORGANIC/AD HANDLING** | **Mandatory split.** Report ORGANIC cohort and PAID cohort separately. Never blend into one engagement story. Permanent PDRN regression. |
| **WHEN TO TRY A SECOND QUERY** | Optional brand+ingredient if organic cohort too thin to judge democratization. |
| **WHEN TO STOP** | After entity query + organic/ad split; do not scrape every brand on the ladder. |
| **RELATED SEARCH USEFUL?** | Beauty related words were useful-ish (“worth buying?”, lips/hair variants) as query ideas only. |
| **COMMENTS LIKELY ADD VALUE?** | Yes **if** question is buy-intent vs skepticism; not required to establish presence. Experiment skipped. |

---

### T05 — CATEGORY_HOME_FINDS

| Field | Rule |
|-------|------|
| **PURPOSE** | Discovery vocabulary: inventory of find-objects, retail channels, hashtags. Not heat proof. |
| **PRIMARY QUERY RECIPE** | `home finds` (or established native phrase). resultsPerPage ≈ 25. Related words optional. |
| **ALIAS/DISAMBIGUATION RECIPE** | N/A at category level. Promote specific SKUs to T01/T02. |
| **WHEN TO USE BROAD QUERY** | This type *is* the broad query. |
| **WHEN TO USE ENTITY-FIRST QUERY** | After a candidate SKU appears (experiment: KUSTFYR did **not** appear here — do not expect web survivors to fall out). |
| **EXPECTED NOISE** | Amazon/Temu/Dollar Tree affiliate roundups dominate; commercially obvious. |
| **RELEVANCE CHECK** | “Is this a home-find object video?” then label affiliate class (§8). Do not compute heat on the category SERP. |
| **ORGANIC/AD HANDLING** | Ads may be low; **affiliate ecosystem** is the main label. Experiment ads = 0 but affiliate-heavy. |
| **WHEN TO TRY A SECOND QUERY** | Only to entity-validate a named candidate (T01/T02). |
| **WHEN TO STOP** | After one category pass + candidate list. No expansion scrapes for weak candidates (experiment skipped expansions). |
| **RELATED SEARCH USEFUL?** | Mildly (“What does home finds mean on TikTok?”, small spaces) — ideation. |
| **COMMENTS LIKELY ADD VALUE?** | Rarely at category level. |

---

### T06 — CATEGORY_BEAUTY_TRENDING

| Field | Rule |
|-------|------|
| **PURPOSE** | Discovery vocabulary for products/launches/phrases; not proof of a named ingredient. |
| **PRIMARY QUERY RECIPE** | `trending beauty products` (or equivalent established seed). |
| **ALIAS/DISAMBIGUATION RECIPE** | Promote brown mascara / creator-brand strings to T12 or T01. |
| **WHEN TO USE BROAD QUERY** | Discovery. |
| **WHEN TO USE ENTITY-FIRST QUERY** | To validate PDRN or any named beauty entity — use T04/T12, not this. |
| **EXPECTED NOISE** | Ads (experiment 4/25), creator-brand launches, POV reviews, mascara waves — mix of useful vocab and hype. |
| **RELEVANCE CHECK** | Beauty product/routine context; then extract candidate names. |
| **ORGANIC/AD HANDLING** | Label ads; do not treat ad plays as organic ingredient heat. |
| **WHEN TO TRY A SECOND QUERY** | Entity check on strongest novel candidate only if Live Heat has a named question. |
| **WHEN TO STOP** | One pass → candidate list. Experiment: brown mascara / POV / REFY noted, not elevated. |
| **RELATED SEARCH USEFUL?** | Yes as ideas (“worth buying?”, lips/hair). |
| **COMMENTS LIKELY ADD VALUE?** | Only after entity promotion + named intent question. |

---

### T07 — CATEGORY_RESTAURANT_MENU

| Field | Rule |
|-------|------|
| **PURPOSE** | Discovery of local openings / brand LTOs; high collision risk with entertainment “menu” content. |
| **PRIMARY QUERY RECIPE** | `new restaurant menu` for vocabulary only. Prefer promoting hits to T11 ASAP. |
| **ALIAS/DISAMBIGUATION RECIPE** | Brand + menu name (`P.F. Chang’s Autumn in Kyoto`) once seen. |
| **WHEN TO USE BROAD QUERY** | Discovery only. |
| **WHEN TO USE ENTITY-FIRST QUERY** | For any specific LTO or restaurant claim. |
| **EXPECTED NOISE** | Mixed geo; brand LTOs; **related-search / SERP pollution from *The Menu* movie**, Ramsay skits, QR-code skits. |
| **RELEVANCE CHECK** | Real restaurant opening or brand LTO — not film scenes, not comedy skits about menus. |
| **ORGANIC/AD HANDLING** | Label if present; experiment ads = 0 on this query. |
| **WHEN TO TRY A SECOND QUERY** | T11 brand+LTO for any heat-relevant candidate. |
| **WHEN TO STOP** | One category pass; discard movie/skit cluster without further spend. |
| **RELATED SEARCH USEFUL?** | **Dangerous.** Experiment returned mostly *The Menu* movie endings/scenes. Treat as polluted unless clearly food-service topical. |
| **COMMENTS LIKELY ADD VALUE?** | Unlikely at category level. |

---

### T08 — CATEGORY_TECH_ACCESSORIES

| Field | Rule |
|-------|------|
| **PURPOSE** | Discovery vocabulary for accessory SKUs / charging / creator tools. |
| **PRIMARY QUERY RECIPE** | `personal tech accessories` (or established tech seed). |
| **ALIAS/DISAMBIGUATION RECIPE** | Promote MagFlow / SnapCool / Rorry / TORRAS etc. to T01/T12-style entity checks if needed. |
| **WHEN TO USE BROAD QUERY** | Discovery. |
| **WHEN TO USE ENTITY-FIRST QUERY** | Named accessory validation. |
| **EXPECTED NOISE** | Ads (experiment 6/25); Amazon charging stations; **organic appearance of banned-seed items** (AirPods) — quarantine, do not expand. |
| **RELEVANCE CHECK** | Personal tech accessory context; apply same banned-seed quarantine as web path. |
| **ORGANIC/AD HANDLING** | Split ads; affiliate-like Amazon posts → ecosystem label. |
| **WHEN TO TRY A SECOND QUERY** | Entity query only for a named Live Heat question. |
| **WHEN TO STOP** | One pass + candidates; no expansion for weak noise. |
| **RELATED SEARCH USEFUL?** | Mixed — Nintendo Switch Accessories / Tech Reviews useful-ish; Fashion/Hair Accessories = pollution. Gate topicality. |
| **COMMENTS LIKELY ADD VALUE?** | Rarely unless sourcing/availability question on a named SKU. |

---

### T09 — RETAILER_HAUL_LANGUAGE

| Field | Rule |
|-------|------|
| **PURPOSE** | Discovery inventory surface for a retailer+season (Target fall haul pattern). |
| **PRIMARY QUERY RECIPE** | Natural haul language (`look what I got Target haul`). |
| **ALIAS/DISAMBIGUATION RECIPE** | Season/retailer variants only from evidence (`#targetfall`). Promote specific SKUs out. |
| **WHEN TO USE BROAD QUERY** | This is a language seed (discovery). |
| **WHEN TO USE ENTITY-FIRST QUERY** | For a specific SKU seen in hauls. |
| **EXPECTED NOISE** | Expected haul pattern; modest reach (experiment med ~7.7k); assortment-obvious items. |
| **RELEVANCE CHECK** | Actual retailer haul/try-on; extract SKU names as vocabulary. |
| **ORGANIC/AD HANDLING** | Experiment ads = 0; still watch for seeded brand placements. |
| **WHEN TO TRY A SECOND QUERY** | Entity check on surprising SKU only. |
| **WHEN TO STOP** | One language pass. Matches web “positive show” lesson — inventory, not surprise heat by default. |
| **RELATED SEARCH USEFUL?** | Possible haul variants; topical gate. |
| **COMMENTS LIKELY ADD VALUE?** | Low unless “where to buy / sold out” is the named question. |

---

### T10 — COPY_TRY_BEHAVIOR_LANGUAGE

| Field | Rule |
|-------|------|
| **PURPOSE** | Probe whether generic copy/try language retrieves restaurant-copy behavior. **Experiment: near-null.** |
| **PRIMARY QUERY RECIPE** | Avoid as validation. If used for discovery: `copied their order` — expect failure to retrieve named challenges. |
| **ALIAS/DISAMBIGUATION RECIPE** | Do **not** treat this as alias for T03. Use the challenge’s real name. |
| **WHEN TO USE BROAD QUERY** | Only as a weak discovery probe; Google-working language ≠ TikTok-working language. |
| **WHEN TO USE ENTITY-FIRST QUERY** | Prefer T03 whenever a challenge name is known. |
| **EXPECTED NOISE** | Low plays (experiment med ~946); off-ritual content; false confidence if misread as “behavior absent.” |
| **RELEVANCE CHECK** | Must show copy-order restaurant behavior; do not infer challenge absence from this SERP alone. |
| **ORGANIC/AD HANDLING** | Label if present; not the main issue. |
| **WHEN TO TRY A SECOND QUERY** | Switch to T03 named challenge immediately if one is hypothesized. |
| **WHEN TO STOP** | After one failed/near-null pass — stop; do not burn budget paraphrasing. |
| **RELATED SEARCH USEFUL?** | Low. |
| **COMMENTS LIKELY ADD VALUE?** | No at this query type. |

---

### T11 — BRAND_PLUS_LTO_OR_NAMED_MENU

| Field | Rule |
|-------|------|
| **PURPOSE** | Validate a specific brand limited menu / LTO once identified (corrective path vs T07 movie noise). |
| **PRIMARY QUERY RECIPE** | `Brand + menu/LTO name` (e.g. pattern from experiment: P.F. Chang’s Autumn in Kyoto). |
| **ALIAS/DISAMBIGUATION RECIPE** | Official LTO name from caption/press; avoid bare “new menu.” |
| **WHEN TO USE BROAD QUERY** | No for validation. |
| **WHEN TO USE ENTITY-FIRST QUERY** | Always for the named LTO. |
| **EXPECTED NOISE** | Other brand content; still far cleaner than T07 related-search movie cluster. |
| **RELEVANCE CHECK** | Mentions that brand’s named menu/LTO. |
| **ORGANIC/AD HANDLING** | Label brand-seeded vs UGC if distinguishable. |
| **WHEN TO TRY A SECOND QUERY** | One alias of the LTO name if needed. |
| **WHEN TO STOP** | After entity confirmation/refutation. |
| **RELATED SEARCH USEFUL?** | Prefer not from T07 parent; generate from brand name instead. |
| **COMMENTS LIKELY ADD VALUE?** | Want-to-try / availability questions only. |

---

### T12 — CREATOR_BRAND_OR_NAMED_LAUNCH

| Field | Rule |
|-------|------|
| **PURPOSE** | Validate a creator-brand or named launch seen in beauty (or other) discovery. |
| **PRIMARY QUERY RECIPE** | Creator-brand product string (`Point of View` / Mikayla skincare naming as evidenced). |
| **ALIAS/DISAMBIGUATION RECIPE** | Hashtag forms from captions (`#pointofviewskincare`) if exact under-retrieves. |
| **WHEN TO USE BROAD QUERY** | Discovery parent (T06) only to find the name. |
| **WHEN TO USE ENTITY-FIRST QUERY** | For presence/replication check. |
| **EXPECTED NOISE** | Review spam, ads (REFY-like clusters), single-creator dominance. |
| **RELEVANCE CHECK** | About that launch/product, not unrelated POV storytelling. |
| **ORGANIC/AD HANDLING** | Split; first-try reviews may be organic but not multi-creator heat. |
| **WHEN TO TRY A SECOND QUERY** | Only if collision with generic “POV” storytelling. |
| **WHEN TO STOP** | After one entity pass; medium novelty ≠ auto SUPPORTED card (experiment listed, not elevated). |
| **RELATED SEARCH USEFUL?** | Low–medium. |
| **COMMENTS LIKELY ADD VALUE?** | Buy vs skepticism possible; not default. |

---

### T13 — RELATED_SEARCH_FOLLOWUP

| Field | Rule |
|-------|------|
| **PURPOSE** | Harvest **query ideas** from `scrapeRelatedSearchWords`. Never treat counts/relatedness as heat. |
| **PRIMARY QUERY RECIPE** | Enable related words on a Discovery parent only when ideation needed; then hand-pick topical follow-ups. |
| **ALIAS/DISAMBIGUATION RECIPE** | N/A — filter list manually. |
| **WHEN TO USE BROAD QUERY** | Parent may be broad; follow-ups must tighten. |
| **WHEN TO USE ENTITY-FIRST QUERY** | Convert good ideas into T01–T04/T11–T12. |
| **EXPECTED NOISE** | Film titles (*The Menu*), fashion/hair bleed from tech, generic questions. |
| **RELEVANCE CHECK** | Topical relevance to the Live Heat question **required** before any follow-up scrape. |
| **ORGANIC/AD HANDLING** | N/A at idea stage. |
| **WHEN TO TRY A SECOND QUERY** | At most one follow-up string that passed the topical gate. |
| **WHEN TO STOP** | If list is polluted (T07 movie case) — discard list, do not scrape it. |
| **RELATED SEARCH USEFUL?** | This type *is* related search; useful only when clean. |
| **COMMENTS LIKELY ADD VALUE?** | No. |

---

## 5. ALIAS / DISAMBIGUATION POLICY

1. **Expand only from known evidence** — web card vocabulary, PDP/press names already in the Live Heat finding, or captions/hashtags already returned by a prior on-demand scrape in the same ask. Do not invent creative aliases.
2. **Always prefer the most discriminating string** that still matches the entity.
3. **Collision-prone exact codes (T01)** get a planned alias (T02) in the same ask, not as an afterthought.
4. **Challenge names (T03)** are not aliased to copy-language (T10).
5. **Record provenance:** for every scrape, log `{query_string, type, alias_of?, topical_hit_rate, decision_contribution}`. Which alias produced evidence must be visible in the handoff.
6. **Cap:** primary + ≤1 alias (+ optional comment pack) unless §11 budget governor explicitly allows one more follow-up for a still-open named question.

---

## 6. RELEVANCE GATE

**Run before median plays / creator diversity / engagement / heat judgment.**

### Procedure (simple)

1. For each returned item, judge: **TOPICAL** | **OFF_TOPIC** | **UNCLEAR** against the named entity/behavior/ingredient.
2. Drop OFF_TOPIC from all metric pools (plays, authors, comments).
3. If UNCLEAR share is high, prefer an alias query rather than guessing.
4. Compute diversity/recency/engagement **only on TOPICAL** set.
5. If topical n is tiny, say so — sparse authentic evidence is a valid WEAKEN (KUSTFYR), not a reason to trust off-topic megaviews.

### Regression anchors

| Case | Gate behavior |
|------|----------------|
| **KUSTFYR** | Fail streamer `@kustfyr` and unrelated megaviews; keep only IKEA/Halloween ghost-product posts before any median. |
| **The Menu / new restaurant menu** | Fail film endings, Ramsay skits, QR skits; keep restaurant openings / brand LTOs only. Related-search movie strings never enter heat logic. |

### Pass / fail for proceeding to heat judgment

- **Proceed:** topical majority (or clear multi-creator topical core) after drops.
- **Do not proceed:** topical ≪ results and megaviews are off-topic → corrective WEAKEN or “instrument failed,” not “viral confirmed.”

---

## 7. QUERY-COLLISION DETECTION

Check **before** interpreting results:

| Collision class | Signal | Experiment example | Action |
|-----------------|--------|--------------------|--------|
| Homograph / SKU=username | Top authors are streamers/creators matching the string; captions lack product context | `KUSTFYR` / `@kustfyr` | Run T02 alias; relevance-fail collisions |
| Film / entertainment title | Related words or captions reference movie scenes, endings, cast | `new restaurant menu` → *The Menu* | Discard related list; prefer T11 |
| Generic English phrase | Results are everyday vlogs with no ritual/product | Weak T10 / bare “menu” | Tighten or stop |
| Category bleed | Related words jump domain (tech → hair/fashion) | T08 related words | Ignore cross-domain ideas |
| Brand-generic object | Alias still pulls category objects | IKEA lamps generally | Tighten brand+distinctive attributes |

**Rule:** If collision suspected, **do not** report play medians until relevance gate + alias path complete.

---

## 8. ORGANIC / PAID / AFFILIATE CLASSIFICATION

### A. Distribution channel (mandatory on Validation)

| Label | Minimum evidence |
|-------|------------------|
| **ORGANIC** | `isAd`/`isSponsored` false or absent **and** no clear “paid partnership” / spark-ads cues in caption metadata used by the actor |
| **PAID** | `isAd` or `isSponsored` true (experiment: usable flags on PDRN) |
| **UNKNOWN** | Flags missing/unreliable and caption inconclusive |

**PDRN permanent regression:** Never report a single blended engagement story when paid share is material (experiment 50%). STRENGTHEN presence ≠ STRENGTHEN organic demand.

Paid is **informative but labeled** — keep it; do not discard the scrape.

### B. Affiliate / seeding sludge (do not auto-reject)

| Label | Minimum evidence | Notes |
|-------|------------------|-------|
| **INDEPENDENT ORGANIC REPLICATION** | Multiple unrelated creators; varied captions; no shared storefront script; not all Amazon/Temu link-in-bio clones | Lunch multi-city pattern is the positive exemplar |
| **CREATOR-AFFILIATE ECOSYSTEM** | Dominant Amazon/Temu/Dollar Tree roundup pattern; repeated “finds” templates; storefront CTAs | `home finds` Arm B |
| **BRAND-SEEDED CAMPAIGN** | Coordinated talking points / brand accounts / dense identical claims across creators | Use sparingly; need caption-pattern evidence |
| **PAID AD** | Actor ad flags true | PDRN half-SERP |
| **UNKNOWN** | Cannot tell | Default when unsure |

**Rule:** Affiliate sludge describes *ecosystem shape*. It can still yield candidate SKUs. It must not be counted as independent organic replication for heat STRENGTHEN.

---

## 9. RELATED-SEARCH POLICY

1. Related search words = **QUERY IDEAS only**, never heat evidence, never engagement proxies.
2. **Topical relevance required** before any follow-up scrape (T13).
3. Enable `scrapeRelatedSearchWords` mainly on Discovery parents when ideation is needed; default off on clean Validation entity queries (Arm A did not need them).
4. **Reject lists** that are entertainment-polluted (*The Menu* endings/scenes, Gordon Ramsay skits, QR-code skits).
5. Accept mild ideation lists (beauty “worth buying?”, home “what does home finds mean”, tech “Nintendo Switch Accessories”) as optional QUERY1 alternatives — still not evidence.
6. **Regression:** `new restaurant menu` related words → movie cluster = **do not scrape**.

---

## 10. COMMENT-PURCHASE POLICY

**Default: do not buy comments.**

Buy a comment pack **only** when answering a **named unresolved question**, such as:

- want / buy intent  
- sourcing / where to get  
- method clarification  
- availability / sold out  
- skepticism / “does it work”  
- child variants  
- watching vs replicating  

**Not by default** for presence, creator diversity, or ad-split questions — captions + authors + timestamps usually suffice (experiment comments **SKIPPED** at $0).

**Pack limits (from experiment policy):** ≤4 videos × ≤30 comments; hard ≤~$1; only pre-qualified **TOPICAL** videos with non-trivial comment counts.

**KUSTFYR lesson:** topical videos with ≈0–4 comments will not recover packaging-meme discourse — skip.

---

## 11. BUDGET GOVERNOR

Experiment proof-of-cost: **$1.128** total (dry $0.001 + Arm A $0.376 + Arm B $0.751). Analysis/comments/expansions $0.

### Escalation ladder (per named Live Heat question)

```
QUERY1 (entity-first if known; else one discovery seed)
  → RELEVANCE GATE
  → optional ALIAS (collision or weak topical)
  → optional COMMENT PACK (named unresolved question only)
  → STOP  or  ONE follow-up entity query
```

### Governor rules

1. Escalate **only** to answer a named unresolved question.
2. Prefer $0 incremental analysis from saved results when possible.
3. Cap a single on-demand ask conservatively (experiment arms used maxTotalChargeUsd 1.0 / 1.5; on-demand validation should usually stay at **one Arm-A-sized** entity probe unless alias/comments required).
4. No expansion farms for “interesting but not strong” TikTok-only candidates (brown mascara, SnapCool, Tesco stool, etc. were correctly skipped).
5. No continuous / scheduled spend. On-demand only.
6. Observed event prices (evidence): result ~$0.0037 · date filter ~$0.0013 · comment ~$0.00125 · actor-start ~$0.001 — use for planning, not as precision targets.

---

## 12. STOP CONDITIONS

Stop the Apify path for this question when any fire:

1. **Decision reachable** — STRENGTHEN / WEAKEN / instrument-failed after relevance + (if needed) alias.
2. **Collision resolved** — exact + one alias done; further paraphrases unlikely to help.
3. **Discovery vocabulary captured** — one category/language pass listed candidates; no heat claim made.
4. **Near-null language probe** — T10-style failure; switch to named entity or abandon.
5. **Related-search pollution** — discard list; do not scrape movie/bleed ideas.
6. **Comment skip justified** — no named unresolved question, or topical comment volume too low.
7. **Budget ladder exhausted** — QUERY1 + alias + optional comments + one follow-up already used.
8. **Candidate too weak for expansion** — affiliate/ad-discounted novelty insufficient (experiment expansions skipped).

---

## 13. REGRESSION TESTS

Expected playbook behavior. No new scrapes — these encode experiment outcomes.

### R1 — Lunch in My City (T03 Validation)

| Step | Expected behavior |
|------|-------------------|
| Mode | Validation; entity-first `Lunch in My City` |
| Forbidden | Validating via `copied their order` (T10) |
| Relevance | High topical expected; keep ritual-executing posts |
| Organic/ad | Expect organic-heavy; label any ads |
| Related search | Optional; not required |
| Comments | Skip unless named intent question |
| Outcome shape | STRENGTHEN on creator diversity + multi-city replication + method hashtag text |
| Stop | After QUERY1 |

### R2 — PDRN (T04 Validation)

| Step | Expected behavior |
|------|-------------------|
| Mode | Validation; `PDRN skincare` (not T06 beauty category alone) |
| Relevance | Ingredient-in-skincare context |
| Organic/ad | **Mandatory split**; paid share may be ~half — label PAID vs ORGANIC |
| Affiliate | Brand ladder ≠ auto-reject; still not all independent replication |
| Comments | Only if buy vs skepticism is the named gap |
| Outcome shape | STRENGTHEN presence/democratization **with ad caveat** |
| Stop | After entity query + split |

### R3 — KUSTFYR (T01 → T02 Validation / Correction)

| Step | Expected behavior |
|------|-------------------|
| Mode | Validation/correction of magnitude claim |
| QUERY1 | `KUSTFYR` |
| Relevance gate | Drop `@kustfyr` streamer + off-topic megaviews **before** medians |
| Alias | Run `IKEA ghost lamp` (and/or `IKEA KUSTFYR` if still needed) |
| Comments | Skip if topical comment counts tiny |
| Outcome shape | WEAKEN high-volume TikTok virality claim for the window; product may remain real via press/PDP |
| Stop | After exact + alias |

### R4 — new restaurant menu (T07 Discovery → T11 / T13)

| Step | Expected behavior |
|------|-------------------|
| Mode | Discovery vocabulary only |
| Relevance | Keep openings/LTOs; drop film/skit |
| Related search | Expect *The Menu* movie pollution → **discard as heat; do not scrape** |
| Promotion | P.F. Chang’s-style hits → T11 entity if Live Heat asks |
| Outcome shape | Candidates + noise notes; no SUPPORTED card from category SERP alone |
| Stop | After one pass or after T11 if validating a named LTO |

### R5 — copied their order (T10)

| Step | Expected behavior |
|------|-------------------|
| Mode | Weak discovery probe at best |
| Expect | Near-null for restaurant-copy / named-challenge retrieval |
| Forbidden | Concluding “Lunch absent on TikTok” from this SERP |
| Correct path | If challenge known → T03 |
| Stop | After one near-null; do not paraphrase-spend |

### R6 — home finds (T05 Discovery)

| Step | Expected behavior |
|------|-------------------|
| Mode | Discovery vocabulary |
| Expect | Affiliate-heavy Amazon/Temu/Dollar Tree ecosystem |
| Classification | CREATOR-AFFILIATE ECOSYSTEM unless independent replication evidenced |
| Named survivors | Do **not** expect KUSTFYR to appear; entity-validate separately |
| Outcome shape | Candidate list; no heat proof from category engagement |
| Stop | After one pass; entity-follow only for named questions |

---

## 14. WHAT THIS PLAYBOOK STILL CANNOT SOLVE

Grounded in experiment limitations (§20 FINAL_REPORT):

1. **No sound/effect reuse graph** — challenge lineage via audio still invisible.
2. **No reliable comment intent by default** — still a blind spot unless §10 fires.
3. **Geo dilution** — without scrape-as-in-country, US Live Heat mixes GB/KR/JP/etc.
4. **Partial query fills** — actor may return &lt; requested n (IKEA ghost lamp 15/20).
5. **Category ≠ named phenomenon** — discovery will keep missing web survivors.
6. **Language non-transfer** — Google-working phrases can near-null on TikTok (T10).
7. **Affiliate domination** — vocabulary without independent replication signal.
8. **Empty captions** — hard cases may need comments later.
9. **Does not replace web dating honesty / anti-bias discipline.**
10. **Not a Creative Center replacement; not continuous monitoring; not a database.**
11. **Cannot invent aliases beyond evidence** — novel phrasings remain operator judgment with logging.
12. **Cannot make permanent connect safe** — that needs product integration (budget governor in skill, ops discipline) beyond a written playbook (§17).

---

## 15. WHETHER THE PLAYBOOK IS NOW SUFFICIENT TO MAKE APIFY AVAILABLE AS AN ON-DEMAND LIVE-HEAT TOOL

### Verdict (split — do not collapse)

| Decision surface | Answer |
|------------------|--------|
| **On-demand tool available under this playbook?** | **YES** — for TikTok-native **VALIDATION / CORRECTION** (and tightly scoped discovery→candidate vocabulary), if operators follow §§1–13. |
| **Permanent connect / always-on wiring into Live Heat?** | **NOT YET** — unchanged. |

**Honesty check:** The instrumentation experiment’s blocker for permanent connect was missing query hygiene (entity vs category vs language recipes, relevance gate, organic/ad split, related-search allowlisting, comment caps, budget governor). This playbook supplies those **as operational rules for humans/agents invoking Apify on demand**. That is enough to authorize **scoped calls**. It is **not** enough to flip permanent connect to YES: always-on would still burn budget on collision/affiliate/movie modes without productized enforcement and without continuous-monitoring design (explicitly out of scope).

**Overall Apify value remains MODERATE** — confirmatory instrument with known failure modes, not a discovery firehose.

---

## 16. IF YES: EXACT NARROW ROLE APIFY SHOULD HAVE

**Role name:** On-demand TikTok validation/correction probe.

**In scope**

1. Validate or correct web Live Heat survivors with entity-first queries (T01–T04, T11–T12).
2. Apply relevance gate → organic/paid split → creator diversity / recency / replication on topical sets only.
3. Optionally run one Discovery seed (T05–T10) to collect **candidate vocabulary**, then stop or promote one entity.
4. Optional ≤$1 comment pack only for named unresolved questions on pre-qualified topical videos.
5. Related words as ideation with topical gate; never as evidence.
6. Per-ask budget ladder in §11; prefer Arm-A-sized validation spends.

**Out of scope**

- Permanent / scheduled / always-on scraping  
- Blind discovery as heat proof  
- Viral scores, threshold dashboards, new APIs, new seed families, creative gates  
- Installing or modifying Live Heat / V1.2 / Run 6  
- Concept generation  

**Success metric for a call:** A clear STRENGTHEN / WEAKEN / instrument-failed / candidates-only handoff with query strings logged — not “more data.”

---

## 17. IF NO: EXACT REMAINING BLOCKER

**For on-demand VALIDATION/CORRECTION:** No remaining blocker **if this playbook is followed.** (§15 YES.)

**For PERMANENT CONNECT (still NOT YET) — remaining blockers:**

1. **No productized enforcement** — playbook is procedural text; Live Heat skill does not yet embed the budget governor, relevance gate, or organic/ad split as hard controls.
2. **No continuous-monitoring design** — and none should be added without a separate evidence pass; always-on was explicitly rejected.
3. **Unresolved instrument gaps** — sound/effect graph, geo scrape-as-in-country, comment-intent defaults still open (§14).
4. **Operational risk** — without enforcement, collision/affiliate/movie modes would still pollute Live Heat and burn budget at scale.

**Revisit permanent connect only after:** on-demand use under this playbook accumulates clean wins without budget incidents **and** the Live Heat skill gains an explicit governor (separate decision; not part of this deliverable).

---

## APPENDIX — Quick decision card

```
Named entity? 
  YES → Validation entity query (T01–T04/T11–T12)
        → Relevance gate → metrics on topical only
        → Collision? → alias once
        → Ingredient/ad-heavy? → ORGANIC/PAID split
        → Named intent gap? → optional comment pack
        → STOP with STRENGTHEN/WEAKEN/failed
  NO  → One Discovery seed (T05–T10)
        → Candidates + noise labels only
        → Related words? ideas with topical gate (drop movie bleed)
        → Promote at most one entity if Live Heat asks
        → STOP (no heat proof from broad SERP)
```

**Evidence refs:** `FINAL_REPORT.md` §§7–10, 12–16, 19–24 · `SUMMARY.md` · `decisions.json` · Arm A dataset `jHbso4fSrGYuupXhn` · Arm B dataset `fsgipVt9vW3nP4u0M` · total spend $1.128.

**Document written:** 2026-10-05 ~11:53– EDT · No new Apify spend · No Live Heat install · No Run 6 · No concepts.
