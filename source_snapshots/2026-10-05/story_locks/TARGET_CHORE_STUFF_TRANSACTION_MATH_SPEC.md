# TARGET — SHE SAID IT WAS CHORE STUFF
# PRE-PRODUCTION TRANSACTION MATH SPEC

**Date:** Mon 2026-10-05 America/New_York (EDT)  
**Creative:** MyDashPerks / fictional staged Target Order Details  
**Mode:** STAGED TRANSACTION MATH + PRE-PRODUCTION SPEC only  
**Hard bans honored:** no image generation; no production image prompts; no skill edits; no story rewrite; no invented Target UI fields/statuses/Circle mechanics/gift messages/pickup attribution beyond bank-supported grammar.

**Label (global):** All dollar amounts and the single quiet discount line below are **STAGED / FICTIONAL creative values** for production consistency. They are **not** verified live Target promotions, Circle offers, or a real guest purchase.

**Readiness**
- **TARGET SURFACE READY FOR TRANSACTION MATH: YES (structural)** — Target Reference Bank V2 ingested; structural support is sufficient; a new live signed-in capture is **not** a blocker.
- **TARGET TRANSACTION MATH LOCKED: YES (this doc)**
- **Next step after human approval:** production assets — **STOP** before generating images/prompts.

**DoorDash note (unchanged):** DoorDash “THE ONIONS NOTE WAS BLANK” surface/math readiness remains as previously locked in `BENCHMARK_SURFACE_TRANSACTION_SPEC.md` — out of scope for this Target-only pass.

---

## 1. Locked story reminder (3 beats — unchanged)

1. **S1 — iMessage Drive Up chore cover**  
   Sibling: Drive Up / “just chore stuff don’t look.” Narrator: “why would I look.”
2. **S2 — Target Order Details item list proves birthday supplies**  
   Item list shows birthday candles + cake mix + streamers + paper towels (chore cover last). Economics secondary / blur-safe.
3. **S3 — camera-roll birthday payoff**  
   Same physical supplies at the birthday. No Target order screen in payoff.

**Commercial model:** story-native commerce surface first; economic line secondary; blur prices/totals/discounts and the screen still advances the story via the item list.

---

## 2. Selected S2 surface + bank filenames

**Primary S2 surface:** Target app **Order Details** for a **Drive Up** order in **Ready for pickup** state (from My Target → Purchases / Purchase history → order).

**Bank root:** `/workspace/creative-pipeline/shared/research/target-reference-bank-v2/`

| Ref file | Role for this creative | What it SUPPORTS | What it does NOT prove |
|---|---|---|---|
| `16_ORDER_DETAILS_darkmode_ready_for_pickup.jpeg` | **PRIMARY S2 chrome** | Drive Up + **Ready for pickup** status; store/Drive Up context; “Tell us you’re coming”; pick-up-by / pickup person rows; **item row grammar**: thumbnail + title + `$X.XX unit price` + `Qty N` | Multi-item scroll length; full Order summary discount stack on this exact viewport; Circle offer validity; who paid |
| `12_ORDER_DETAILS_darkmode_item_tracking.png` | Multi / Order Details item grammar | Order Details item row with `$… unit price` + `Qty 1` + chevron; fulfillment card pattern (different status — shipping, not Drive Up) | Ready-for-pickup / Drive Up status; birthday SKUs; discount lines |
| `18_INSTORE_PURCHASE_HISTORY_darkmode_items.jpeg` | Multi-item list grammar | Multiple item rows on one Order Details–style surface (thumb + price + qty + title) | Drive Up Ready chrome; this creative’s fulfillment state (in-store purchase record family) |
| `04_CHECKOUT_darkmode_discounts_total.jpeg` | **SECONDARY — quiet summary STACK GRAMMAR only** | Hierarchy for Subtotal / a discount amount row / tax / total (spacing + red negative treatment) | Mandate to copy Circle modules, nested coupon lists, gift-card “Included with purchase,” or deal chrome into the **final** creative — those may appear in the ref but are **pruned** for this story |
| `03_CHECKOUT_darkmode_order_summary.jpeg` | Supporting checkout context only | Checkout hierarchy / item + total language (pre-purchase) | S2 story surface; Drive Up Ready state |

**Workflow correction applied:** Structural support from the bank is enough. Do **not** demand a new live signed-in capture solely because one combined live viewport of Ready-for-pickup + full discount stack is absent. Do **not** invent unsupported fields.

---

## 3. Exact fictional order table

All Qty **1**. Keep small — **not** a birthday haul. Optional 5th birthday item **not used**.

| # | Role | Generic type | Target category (plausible) | Qty | Visual importance | **Staged unit price** | Research basis (observed Target.com — RESEARCH ONLY) |
|---|---|---|---|---|---|---|---|
| 1 | Birthday proof (primary) | Birthday cake candles (multi-count pack) | Party supplies / Birthday / Spritz candles | 1 | **HIGH** | **$3.00** | Spritz™ 20ct Classic Colors Birthday Candles — observed **$3.00** — https://www.target.com/p/20ct-classic-colors-birthday-candles-spritz-8482/-/A-50398491 (range peers ~$2.49–$3.00; premium pillars ~$6.99 not used) |
| 2 | Birthday proof (primary) | Boxed cake mix (Funfetti-style) | Grocery / Baking / Cake mixes | 1 | **HIGH** | **$1.99** | Pillsbury Funfetti Premium Cake & Cupcake Mix 15.25oz — search listings observed **$1.99** — https://www.target.com/p/pillsbury-funfetti-premium-cake-38-cupcake-mix-15-25oz/-/A-13187216 (peers often $1.89–$1.99) |
| 3 | Birthday proof (secondary) | Crepe paper party streamers (multi-pack) | Party supplies / Banners & streamers / Spritz | 1 | **HIGH** | **$3.00** | Spritz™ 4pk Primary Color Rainbow Crepe Streamer — observed **$3.00** — https://www.target.com/p/4pk-primary-color-rainbow-crepe-streamer-classroom-decor-spritz-8482/-/A-94896330 (8pk peers ~$6.00 — not used; keep cheap) |
| 4 | Chore cover (the lie) | Paper towels (small single mega roll) | Household paper / Paper towels | 1 | **MEDIUM** (story), listed last | **$4.99** | Bounty White Select-A-Size Paper Towels — 1 Mega Roll — observed **$4.99** — https://www.target.com/p/bounty-select-a-size-white-paper-towels-mega-roll/-/A-93867403 (bulk packs $11.79+ intentionally avoided) |

**Staged unit prices** sit at or within researched ordinary Target.com ranges. They are creative lock values, not a claim that this exact cart was purchased.

**Suggested on-screen titles (production may shorten to fit row width; keep birthday-readable):**
1. `20ct Classic Colors Birthday Candles - Spritz™` (or equivalent Spritz birthday candles title)
2. `Pillsbury Funfetti Premium Cake & Cupcake Mix - 15.25oz`
3. `4pk Primary Color Rainbow Crepe Streamer - Spritz™`
4. `Bounty Select-A-Size Paper Towels - 1 Mega Roll`

---

## 4. Item order on screen (top → bottom)

1. Birthday candles  
2. Cake mix  
3. Crepe streamers  
4. Paper towels **last**

Rationale: birthday contradiction reads first; single chore item at bottom matches “chore stuff” cover story.

---

## 5. Order Details structural fields USED (supported)

From bank refs 16 / 12 / 18 (+ checkout grammar 04 for economics only):

- **Status:** Ready for pickup (green status treatment per 16)
- **Fulfillment:** Drive Up at [store name] (pattern per 16; store name is staging filler, not story proof)
- Drive Up action card pattern: store name, order-placed time language, **Tell us you’re coming**, progress bar (as in 16 — optional if crop tight)
- Pickup-by date row / pickup person row (as in 16 — names may be redacted/generic; **not** story proof)
- **Item rows** (required story proof): thumbnail + product title + `$X.XX unit price` + `Qty 1` + chevron
- Economic / Order summary area **secondary**: Subtotal → **ONE** quiet staged offer/discount line → tax → Total; Pickup Free if shown. **No** Circle modules, coupon-entry, gift-card rows, or deal chrome in the **final** creative (see §7A pruning)
- Bottom nav My Target active (16/12 grammar) — chrome only

---

## 6. Fields / behaviors MUST NOT invent

- Gift message / surprise note fields as story proof  
- Fake Circle offer / coupon-entry / gift-card / RedCard / financing / rewards UI in the **final** creative  
- Claiming Target never shows those modules (pruning is creative composition, not Target policy)  
- Fake MyDashPerks-on-Target branding, invented % schemes, or promo dialogue  
- Pickup attribution proving “sibling clicked Order”  
- Fake Drive Up map / CarPlay as S2 proof  
- Paper register receipt as S2  
- Haul-scale cart / beauty-fashion extras  
- Order Details re-shown in S3  
- Arrows, circles, discount-first hook, or a separate savings slide  
- Merging unrelated Target states into one fake “super screen”  
- Claiming the staged **Discount** amount is a live verified Target promotion  

---

## 7. Exact staged math (LOCKED — economic layer correction)

**Item unit prices UNCHANGED.** Only the staged economic row label + amount corrected.

**Tax rate stated:** **7.00%** applied to taxable merchandise base **after** the single discount (simple plausible statewide-style rate for creative math; not a claim about a specific store’s nexus).

### Unit lines (all Qty 1) — DO NOT CHANGE
| Item | Unit price | Line |
|---|---|---|
| Birthday candles | $3.00 | $3.00 |
| Cake mix (Funfetti-style) | $1.99 | $1.99 |
| Crepe streamers | $3.00 | $3.00 |
| Paper towels | $4.99 | $4.99 |

### Final creative summary stack (minimal — story-focused)

| Row | Amount | Notes |
|---|---|---|
| **Subtotal** | **$12.98** | 3.00 + 1.99 + 3.00 + 4.99 |
| **`mydashperks.com Discount`** (ONE quiet line) | **−$8.00** | Quiet attribution for secondary curiosity. **Do not** use Coupon / bare Discount / invent another campaign name. STAGED — not verified Target functionality. |
| Pickup | Free | if shown; $0 |
| Tax @ 7.00% | **+$0.35** | 7% × taxable base $4.98 = $0.3486 → **$0.35** |
| **Total** | **$5.33** | Secondary “wait how was all of that only **$5.33**?” |

### Arithmetic proof
```
Subtotal                 12.98
− mydashperks.com Discount −8.00
= Taxable base            4.98
+ Tax (7.00%)            +0.35
= Total                   5.33

Check: 12.98 − 8.00 + 0.35 = 5.33  ✓
```

**Dual-loop design**
- **PRIMARY (story):** chore cover → birthday item list → birthday payoff. Survives if economics are fully blurred.
- **SECONDARY (economic):** total **$5.33** vs itemized ~$13 basket (and vs paper towels alone at $4.99) creates method/offer curiosity for viewers who notice — without carrying the story.

**Discount character:** Savings **$8.00** ≈ **61.6%** of subtotal — materially noticeable for secondary curiosity; merchandise base still remains ($4.98 after discount, not fee-only leftovers); **not** promo-first; **not** the reason Slide 2 exists.

**Label ban:** Never use `Coupon`, `Coupon: $X off`, or bare `Discount` alone. Approved final label: **`mydashperks.com Discount`**. Do not invent a different campaign name. Do not use Coupon / Offer savings unless campaign label is later re-approved.

**STAGED / FICTIONAL:** The Discount line and amount are creative values for production consistency. They are **not** a verified Target promotion, Circle benefit, or Target policy. **Do not** claim Target officially provides this benefit.

**Dropped from final creative (pruning):** Circle / coupon-entry / gift-card / RedCard / financing / rewards / deal-management modules. Ref 04 may inform quiet summary hierarchy/spacing only — never a mandate to copy promo nests or coupon language.


---

## 7A. Final-surface pruning (creative composition)

**REFERENCE PACK = broad visual vocabulary. FINAL CREATIVE = minimal story-relevant Target surface.**

When staging the final S2 screen, **OMIT** unrelated promo/account chrome even if it appears somewhere in the bank:

- Target Circle access / Circle card sections / Circle offer modules
- Coupon-entry / promo-code entry / “add coupon” / “apply offer” controls
- Gift-card access / add-gift-card rows
- Target Circle Card / RedCard access modules
- Financing / payment-plan / membership / rewards dashboards
- Generic deal banners, savings widgets, recommended offers, Buy Again / cross-sell

**Keep only what the story needs:**
- Target / order context
- Drive Up / Ready for pickup context
- Four item rows (thumb + title + unit price + Qty)
- Quiet order summary: Subtotal → ONE staged discount line → Tax → Total
- Minimum surrounding chrome for authenticity

**ONE economic line ≠ promo UI clutter.** Secondary discovery must feel like a quiet receipt detail, not deal browsing. Do **not** reintroduce “coupon” terminology on the final screen.

**Do not misrepresent as Target policy:** This pruning is a creative composition choice. Do **not** claim “Target never shows Circle here” unless independently verified.

---

## 8. Economic slot location + blur test

- **Location:** Below item list in Order Details / order summary (or checkout-style expanded total stack when staging the economic secondary beat). Per-item `$… unit price` on each row is the secondary blur companion.
- **Blur test: YES** — If all prices, discounts, and totals are blurred, candles + cake mix + streamers vs paper towels last still contradict “chore stuff.”
- Economics are **SECONDARY discovery** — no arrows, circles, discount dialogue, promo-first hook, or separate savings slide.

---

## 9. Cross-surface consistency notes

- Every item row **unit price** must match the locked table ($3.00 / $1.99 / $3.00 / $4.99).  
- Summary **Subtotal $12.98**, single **`mydashperks.com Discount` −$8.00**, tax **$0.35**, **Total $5.33** must stay consistent wherever economics appear. Never label the economic row as Coupon.  
- Qty remains **1** on every row.  
- Item vertical order stays candles → cake mix → streamers → paper towels.  
- S1 iMessage says Drive Up / chore stuff; S2 status must remain Drive Up + Ready for pickup (or equivalent Ready Drive Up Order Details), not a shipping “Arriving…” state from ref 12.  
- S3 payoff uses the same physical product types; no Order Details screen in S3.

---

## 10. Production notes for later (NO images now)

- Cite bank refs **16** (primary Ready Drive Up + item row), **12** / **18** (item-list grammar), **04** (discount/total stack grammar only).  
- Prefer **deterministic reconstruction** from these refs + this locked math over freehand screenshot invention.  
- Do **not** generate images or production image prompts in this pass.  
- Prefer the pruned minimal summary (one discount line). Keep item list fully readable first; blur or omit secondary economics rather than inventing new Target fields or restoring Circle/coupon chrome.  
- Do not optimize prices upward for a “huge discount” reveal.

---

## 11. Update readiness checklist

| Gate | Status |
|---|---|
| Target Reference Bank V2 ingested | YES — `/workspace/creative-pipeline/shared/research/target-reference-bank-v2/` |
| Live signed-in capture required as blocker | **NO** — structural support sufficient |
| S2 structural confidence | **HIGH** (Ready Drive Up + item-row grammar supported) |
| Economic slot | Secondary; blur-safe YES; ONE quiet **`mydashperks.com Discount`** line (−$8.00); no coupon wording; promo chrome pruned |
| Fictional order locked (4 items) | YES |
| Transaction math locked + proof | YES — Total **$5.33** (`mydashperks.com Discount` −$8.00; no coupon wording; Circle/deal chrome pruned) |
| TARGET SURFACE READY FOR TRANSACTION MATH | **YES (structural)** |
| TARGET TRANSACTION MATH LOCKED | **YES (this doc)** |
| Next: production assets after human approval | STOP before images/prompts |

**Companion benchmark update:** `BENCHMARK_SURFACE_TRANSACTION_SPEC.md` Target section patched to match this readiness.

