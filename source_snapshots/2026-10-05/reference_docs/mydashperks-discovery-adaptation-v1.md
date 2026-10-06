# MyDashPerks Discovery + Adaptation System — V1

**Status:** LOCKED 2026-09-23 (owner final prompt)  
**Scope:** MyDashPerks ONLY. Ignore other brands/sites/projects. Not generic affiliate marketing.  
**Companion teaching evidence:** `mydashperks-golden-examples.md` (GE-001…; study before evaluating sources).  
**Hard stop:** Do **not** generate final images from discovery/adaptation. Stop at candidate approval. Production gets only an approved locked spec.

---

## Core idea

We are NOT primarily searching for existing affiliate posts.

Some of the strongest ideas originate from normal viral content with nothing commercial about it.

Pipeline:

1. find entertaining format  
2. understand why humans care  
3. extract transferable mechanic  
4. invent an original situation  
5. determine whether MyDashPerks fits naturally  
6. only then consider production  

**MyDashPerks should generally be a secondary inspectable element, not the reason the post exists.**

Good test: *Would this post still be interesting if the viewer never noticed MyDashPerks?* Prefer **YES**.

---

## What we currently know works

Study `mydashperks-golden-examples.md` before evaluating sources.

Those examples are human-selected evidence about the **types of mechanics** we care about. Do not copy them mechanically.

Use them to understand:

- human stakes  
- visual/social situations  
- information gaps  
- inspectable evidence  
- unexpected purchase/order details  
- delivery complications  
- gift/budget mismatches  
- coordinated-product/meme reactions  
- judgment/share motives  
- final visual payoffs  

Owner pattern lock (from golden intake): viral first without the brand → food/delivery/order as *evidence of a human story* → perk as secondary inspectable math — avoid “ad from frame one” (see GE-005 caution).

---

## Discovery has three lanes

### Lane A — User FYP / human discovery (critical)

Search queries alone will NOT necessarily find the kinds of posts the owner notices while scrolling.

When the owner provides screenshots, screen recordings, TikTok links, or saved posts:

- label `source_type`: **`user_provided_fyp`**
- prioritize understanding mechanics

### Lane B — Browser FYP experiment

If TikTok is authenticated in Grok Bot’s browser through the owner’s authorized session, test whether native computer-use can inspect the actual For You feed.

- Do **NOT** claim this works until tested.  
- Do **NOT** bypass TikTok access controls, CAPTCHAs, restrictions, or authentication.  
- If available: inspect posts sequentially; distinguish photo/carousel/video; capture canonical URL/post ID; publication time; visible metrics; screenshots/slides for vision; record `first_seen_at`.  
- Label: **`user_fyp_browser`**.  
- Do **NOT** treat browser scrolling as a neutral API feed.  
- Avoid unnecessary liking/commenting/following or other interactions that intentionally alter recommendations.  
- If unreliable: report clearly; continue with user-supplied examples + ScrapeCreators/public discovery.

### Lane C — ScrapeCreators

Use for: public post discovery; ordered carousel retrieval; metrics; publication timestamps; re-fetching candidates.

Treat Top Search primarily as **mechanic mining** unless freshness testing proves otherwise. Do not assume “top” means “currently emerging.”

---

## Vision before mechanic

Search category/caption alone is NOT enough.

Before calling a source highly adaptable, inspect the actual ordered slides.

For each relevant slide record:

- visible text  
- major objects/products  
- what new information appears  
- viewer question created  
- viewer question answered  

Then identify: **expectation → escalation/information change → payoff**

A category such as “haul” / “gift basket” / “food” / “Target” is **NOT** itself a mechanic.

---

## Adaptation test

For promising sources answer:

1. Why does a normal viewer care?  
2. What information makes them continue?  
3. What is the payoff?  
4. What detail makes them inspect closely?  
5. What might make them send it to somebody?  
6. How can the mechanic be substantially mutated rather than copied?  
7. Can MyDashPerks naturally exist inside that new situation?  

---

## MyDashPerks fit

**Strong natural territory:** delivery orders; takeout/food; order totals; unusual delivery situations; budget/order mismatches; desirable orders; customer/Dasher situations; food memes where an order naturally belongs; delivery-related screenshots/evidence.

**Do NOT force MyDashPerks into:** unrelated beauty content; unrelated concert posts; generic memes; random products — just because the source performed well.

Those can still teach mechanics, but mark: **`NO_NATURAL_MYDASHPERKS_FIT`**.

---

## Commercial bridge

For each MyDashPerks candidate specify:

- **primary_story** — what the viewer consciously thinks the post is about  
- **secondary_commercial_detail** — inspectable detail where MyDashPerks is relevant  
- **viewer_discovery_path** — how somebody might independently notice/question that detail  

Never solve weak commercial fit by inventing unsupported financial proof or representing staged transaction evidence as factual.

---

## Output (shortlist)

Show **maximum 3 adaptation candidates at a time**. Quality over volume.

For each shortlisted source return:

- source ID  
- discovery lane  
- source format  
- publication time  
- first-seen time  
- current metrics + observed timestamp  
- vision-verified mechanic  
- human reason to care  
- information gap  
- payoff  
- inspectable detail  
- share/judgment motive  
- MyDashPerks fit: HIGH / MEDIUM / LOW / NONE  
- proposed mutation  
- primary story  
- secondary commercial detail  
- must-be-visible objects/details  
- production difficulty  
- clone risk  

---

## Important

- Do **not** generate final images yet.  
- Discovery and adaptation stop at **candidate approval**.  
- Production receives only an **approved locked specification**.  
- Goal is not lots of ideas — goal is ideas where the owner immediately thinks: **“yeah, I see how this becomes ours.”**

---

## Related paths

- Golden examples: `/workspace/creative-pipeline/shared/context/mydashperks-golden-examples.md`  
- Golden assets: `/workspace/creative-pipeline/shared/context/golden-example-assets/`  
- Source cards skill: `/home/box/agent-data/workflows/source-card/SKILL.md`  
- Adaptation skill: `/home/box/agent-data/workflows/adaptation-blitz-match/SKILL.md`  
- ScrapeCreators probe/batch: `/workspace/creative-pipeline/shared/research/scrapecreators-probe/`  
