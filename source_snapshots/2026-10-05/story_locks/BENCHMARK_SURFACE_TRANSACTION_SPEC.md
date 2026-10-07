# BENCHMARK SURFACE-REFERENCE + TRANSACTION-SPEC

**Date:** Mon 2026-10-05 America/New_York (EDT)  
**Mode:** SURFACE-REFERENCE + TRANSACTION-SPEC only  
**Hard bans honored:** no final amounts invented for the benchmarks; no images generated; no production prompts; no skill edits; no new concepts; do not invent Target/DoorDash UI fields.

**Locked stories (unchanged unless UI forces minimal note below):**

1. **TARGET — SHE SAID IT WAS CHORE STUFF**  
   S1 sibling iMessage: Drive Up / chore stuff don’t look  
   S2 Target order details prove birthday supplies in the order  
   S3 camera-roll birthday payoff (no order screen in payoff)

2. **DOORDASH — THE ONIONS NOTE WAS BLANK**  
   S1 food photo with onions + overlay “he said he copied my order exactly”  
   S2 iMessage claim fight  
   S3 DoorDash order details prove whether no-onions was submitted

**Commercial model:** story-native commerce surface first; economic line secondary; blur prices/totals/discounts and screen still necessary.

**Research method:** exhaust workspace refs under `/workspace/creative-pipeline/` and `/workspace/target-e2e/` (Read on key images), then WebSearch/WebFetch for current fields. **Target bank V2** at `/workspace/creative-pipeline/shared/research/target-reference-bank-v2/` is now the primary structural bank for SHE SAID IT WAS CHORE STUFF. Workflow: structural support from the bank is enough; do not demand a new live signed-in capture unless a required field/behavior is unsupported.

---

# TARGET — SHE SAID IT WAS CHORE STUFF

## 1. VERIFIED SURFACE

**Primary story surface (S2):** Target app **Order Details** for a **Drive Up / Order Pickup** order reached from **My Target → Purchases / Purchase history → [order]**.

What this surface must show for the story (item proof, not haul flex):
- Fulfillment context readable as Drive Up or Order Pickup / Ready for Pickup (or post-pickup order details with the same item list)
- Itemized product rows: thumbnail + product title (birthday candles, cake mix, streamers, paper towels)
- Order-level economics present but **blur-safe** (not required to read for story)

**Not the story surface:** cart-only, checkout-only, paper register receipt, review-request email, Buy Again carousel, or S3 camera-roll payoff.

**Navigation (verified via Target Help + workspace captures):**
- App: name/Account tab → **Purchases** / **Purchase history** → select order → **Order Details**  
  Sources: Target Help “How can I find or track my Target order?”; “Can I cancel my Drive Up or Order Pickup order?”; Drive Up & Order Pickup hub  
  https://www.target.com/help/article/000062910  
  https://www.target.com/help/articles/delivery-options/drive-up-order-pickup
- Ready state: when ready, Order Details / popup supports **Tell us you’re coming**, **Show pickup barcode / View barcode**, and **Switch to Drive Up / Switch to in-store pickup**  
  https://help.target.com/help/TargetGuestHelpArticleDetail?articleId=ka95d000000geSnAAI&articleTitle=Can+I+switch+between+Drive+Up+and+Order+Pickup+after+the+order+is+placed%3F

## 2. REFERENCE(S) FOUND (paths + what each shows)

### Target Reference Bank V2 — PRIMARY for S2 (ingested)

| Path | What it shows | Use for S2 |
|---|---|---|
| `/workspace/creative-pipeline/shared/research/target-reference-bank-v2/16_ORDER_DETAILS_darkmode_ready_for_pickup.jpeg` | Drive Up **Ready for pickup** + item row (`$… unit price`, `Qty`) | **Primary S2 chrome** |
| `/workspace/creative-pipeline/shared/research/target-reference-bank-v2/12_ORDER_DETAILS_darkmode_item_tracking.png` | Order Details item grammar (unit price + Qty) | Multi / item-row support |
| `/workspace/creative-pipeline/shared/research/target-reference-bank-v2/18_INSTORE_PURCHASE_HISTORY_darkmode_items.jpeg` | Multi-item list on Order Details–style surface | Multi-item list grammar |
| `/workspace/creative-pipeline/shared/research/target-reference-bank-v2/04_CHECKOUT_darkmode_discounts_total.jpeg` | Subtotal / Discounts (`Coupon: $X off`, `ONE quiet `Discount` line −$8.00 (no coupon wording; Circle/deal chrome pruned)`) / tax / total | **STACK GRAMMAR only** (secondary economics) |

Handoff rule: `00_READ_FIRST_CURRENT_HANDOFF.md` — structural support ≠ require exact live-pixel combined capture.

### Workspace — earlier / supporting

| Path | What it shows | Use for S2 |
|---|---|---|
| `/workspace/target-e2e/run2-zelda-orderdetails/hip2save-2018-order-ready-phone.jpg` | Real phone photo of Target **Ready for Pickup** chrome: bullseye + **Order #**, status “Your order is ready at [store]!”, green **Pick up by [date]**, store name/address card. **No item list, no prices.** | Status/header grammar for Ready for Pickup. **Dated ~2018 — do not treat as current pixel chrome.** |
| `/workspace/target-e2e/run2-zelda-orderdetails/signed-in/purchase-history-no-purchases.png` | Signed-in **Purchase history** (web, empty): Online / In-store tabs, search/filters; footer lists **Drive Up** as a service. | Navigation shell only. |
| `/workspace/target-e2e/run2-zelda-orderdetails/yt-purchase-history-thumb.jpg` | Marketing thumb: app **Purchases** header + Online / In-store toggle. | Entry chrome only. |
| `/workspace/target-e2e/run2-zelda-orderdetails/apkmirror-2026-07-buyagain-shop-past-orders.jpg` | Jul 2026 marketing of **Buy Again** + “Shop past orders”; item cards show image + price + title/brand. | Current app visual language for product rows; **not** Order Details. |
| `/workspace/target-e2e/run2-zelda-cart/mobile-cart.png` | **Current** signed-in mobile **Cart**: item thumbnail + title + unit price + qty; est. total; Order summary (promo, estimated total). | Best workspace grammar for **item row + price placement** (pre-purchase). |
| `/workspace/target-e2e/run2-zelda-cart/mobile-checkout.png` | Mobile **Checkout**: Cart summary with total + thumbnail; Order Pickup person; **Order summary** = Subtotal / Pickup Free / Estimated taxes / Total. | Economic line pattern for Target pickup orders (pre-purchase). |
| `/workspace/target-e2e/run2-zelda-cart/signed-in-checkout-review-full.png` | Web checkout review: same Order summary lines; pickup person; Ready within 2 hours. | Confirms summary labels. |
| `/workspace/target-e2e/run2-zelda-order/rge-order-review.png` | Post-purchase **review-request email** (©2019): order # + product image/title, **no prices**. | Item naming/image style only — **not** Order Details. |
| `/workspace/target-e2e/price-gap/jules-22sep2026-receipt-higher-total.jpg` | Physical store paper receipt (TikTok). | **Out of scope** for app Order Details. |

### Web — current fields (no invented UI)

- Drive Up & Order Pickup help: Order Details hosts barcode, I’m on my way / I’m here, switch Drive Up ↔ in-store, receipts/invoices, order summary/total, cancel items.  
  https://www.target.com/help/articles/delivery-options/drive-up-order-pickup
- Packing-slip/receipt help: Order Details → Receipts and invoices; on web, select order total → Order summary.  
  https://help.target.com/help/TargetGuestHelpArticleDetail?articleId=ka95d000000wpJBAAY&articleTitle=What+should+I+do+if+my+packing+slip+is+missing%3F

### Product existence (category verification — not haul)

- Birthday candles: Spritz 20ct Silver Birthday Candle — https://www.target.com/p/20ct-silver-birthday-candle-spritz-8482/-/A-92290030 (Pickup/Delivery listed)
- Cake mix: Pillsbury Funfetti Premium Cake & Cupcake Mix 15.25oz — https://www.target.com/p/pillsbury-funfetti-premium-cake-38-cupcake-mix-15-25oz/-/A-13187216
- Streamers: Spritz 8pk crepe streamers — https://www.target.com/p/8pk-crepe-streamer-spritz/-/A-95015765
- Paper towels: Bounty / paper towels sold at Target (generic chore cover item)

## 3. CURRENT UI CONFIDENCE: **HIGH** (S2 structural)

**Bank V2 ingested:** `/workspace/creative-pipeline/shared/research/target-reference-bank-v2/`

**Why HIGH (structural):** Primary S2 refs now in-bank — `16_ORDER_DETAILS_darkmode_ready_for_pickup.jpeg` (Drive Up + Ready for pickup + item row with `$… unit price` / `Qty`), `12_ORDER_DETAILS_darkmode_item_tracking.png` (Order Details item grammar), `18_INSTORE_PURCHASE_HISTORY_darkmode_items.jpeg` (multi-item list grammar), `04_CHECKOUT_darkmode_discounts_total.jpeg` (discount/total **stack grammar only**). Workflow correction: **structural support is enough**; a new live signed-in combined viewport is **not** a production blocker.

**Still secondary / not pixel-forensic:** Economic discount nest on post-purchase Order Details may follow checkout summary grammar (ref 04) rather than a single live Ready+summary screenshot. That does **not** block transaction math when economics remain secondary and blur-safe.

**Do not invent:** unsupported Target fields, statuses, Circle mechanics beyond discount LINE labels shown in ref 04, gift messages, or pickup attribution.

## 4. EXACT FICTIONAL ORDER CONTENTS

Small Drive Up — cheap, not a haul. Four lines. Optional fifth birthday item **not** used (four is enough).

| # | ITEM ROLE | GENERIC PRODUCT TYPE | PLAUSIBLE TARGET CATEGORY | QTY | WHY IT BELONGS | VISUAL IMPORTANCE | Verified existence |
|---|---|---|---|---|---|---|---|
| 1 | Birthday proof (primary) | Birthday cake candles (multi-count pack) | Party supplies / Birthday / Spritz candles | 1 | Instantly reads “party,” not chores | **HIGH** | Yes — Spritz birthday candles on Target.com (e.g. A-92290030) |
| 2 | Birthday proof (primary) | Boxed cake mix (funfetti / birthday-coded) | Grocery / Baking / Cake mixes | 1 | Cake = birthday; packaging readable in thumb | **HIGH** | Yes — Pillsbury Funfetti A-13187216 |
| 3 | Birthday proof (secondary) | Crepe paper party streamers (multi-pack) | Party supplies / Banners & streamers / Spritz | 1 | Décor = surprise party, not detergent run | **MED** | Yes — Spritz 8pk crepe streamers A-95015765 |
| 4 | Chore cover (the lie) | Paper towels (small multipack / select-a-size) | Household paper / Paper towels | 1 | Matches “chore stuff” text; bottom of list = cover story | **MED** (story), **LOW** as birthday flex | Yes — paper towels sold at Target (use generic type; do not invent unlisted SKU/price) |

**Do not invent:** Circle offer copy, gift message text, unlisted SKUs, or haul extras. Real SKUs above are optional titles only if production later copies verified PDP names — quantities stay 1 each.

## 5. ITEM ORDER ON SCREEN

Recommended on-screen order (top → bottom), matching story reveal (birthday first, chore cover last):

1. Birthday candles  
2. Cake mix  
3. Streamers  
4. Paper towels  

Rationale: viewer reads birthday contradiction before the single chore item that “explains” the sibling’s text. Matches locked premise “one pack of paper towels at the bottom.”

## 6. STORY INFORMATION THE SCREEN LITERALLY PROVES

- This Target account has a real Drive Up / pickup order (Order Details / Ready chrome).  
- Cart contents are **birthday supplies** (candles + cake mix + streamers), not “just chore stuff.”  
- Exactly one chore-plausible item (paper towels) exists as cover.  
- Sibling’s iMessage claim is contradicted by item titles/thumbnails alone.

Does **not** need to prove: who paid, Circle savings, exact dollars, surprise intent (S3 camera roll does payoff).

## 7. FIELDS THE REAL UI SUPPORTS

Confirmed by Help + workspace captures (do not invent beyond these):

- **Purchases / Purchase history** list; Online vs In-store  
- **Order Details** page for a selected order  
- Order / status messaging including **Ready for Pickup**  
- **Order #** (seen on Ready chrome + emails)  
- Store / pickup location context  
- **View barcode** / Show pickup barcode; **I’m on my way** / **I’m here** (Drive Up)  
- Switch **Drive Up ↔ in-store Order Pickup** when ready (app)  
- Pickup person / shopping partner controls (checkout + Order Details edit paths per Help)  
- Item identity: product image + title (+ brand where Target lists it)  
- Quantity  
- Item price (cart/Buy Again grammar; Order Details/receipt expected to show purchasable economics — exact post-purchase mobile layout needs live capture)  
- **Order summary** / order total / receipts & invoices (Help)  
- Typical summary lines from **current checkout** (proxy): Subtotal, Pickup (Free), Estimated taxes, Total; Promo code slot  

## 8. FIELDS / BEHAVIORS WE MUST NOT INVENT

- Fake “gift message” / “surprise note” fields as story proof  
- Fake Circle / MyDashPerks / invented % off rows beyond discount **LINE labels** visibly supported by bank ref 04 (`Coupon: $X off`, `ONE quiet `Discount` line −$8.00 (no coupon wording; Circle/deal chrome pruned)`) — and never claim staged amounts are live offers  
- Fake Drive Up map animations or CarPlay-only chrome as the proof surface  
- Paper register receipt as S2  
- Invented item categories that Target doesn’t sell  
- Haul-scale cart (many beauty/fashion lines)  
- Showing Order Details again in S3 (locked: camera-roll payoff only)  
- Pixel-copying 2018 Ready UI as “current” without noting age  

## 9. ECONOMIC SLOT LOCATION

- **Primary:** below the item list in **Order Details** — **Order summary** / order total (Help: receipts/invoices; web “select the order total to view the Order summary”).  
- **Secondary (blur together):** per-item prices on each row (cart/Buy Again grammar).  
- **Do not use as story proof:** Circle marketing banners, financing upsells, empty Purchase history.

## 10. ECONOMIC SLOT VIABILITY: **SECONDARY — usable (blur-safe)**

**Why:** Bank ref 04 supplies Subtotal / Discounts (`Coupon: $X off`, `ONE quiet `Discount` line −$8.00 (no coupon wording; Circle/deal chrome pruned)`) / tax / total **stack grammar**. Item-list proof remains primary; economics are secondary discovery. Exact staged amounts are locked in `TARGET_CHORE_STUFF_TRANSACTION_MATH_SPEC.md` and labeled **STAGED / FICTIONAL** — not verified Target promotions. Live capture is **not** required to proceed.

## 11. STORY STILL WORKS WITH ALL ECONOMICS BLURRED: **YES**

Candles + cake mix + streamers vs one paper towel pack still contradict “chore stuff.” Dollars are optional.

## 12. ANY MINIMAL STORY ADJUSTMENT REQUIRED

**NONE** for locked S1–S3 structure.

Optional production note (not a story rewrite): prefer **Order Details item list** (with Ready for Pickup or after-pickup details) over the Ready status-only card — hip2save Ready screen alone **does not** list items.

### Transaction math lock (Target)

**File:** `/workspace/creative-pipeline/shared/research/ssg-orchestration-test/TARGET_CHORE_STUFF_TRANSACTION_MATH_SPEC.md`  
**Staged total:** $5.33 (subtotal $12.98 − discounts $2.55 + tax $0.73 @ 7.00%) — **STAGED / FICTIONAL**.  
**TARGET TRANSACTION MATH LOCKED: YES**

---

# DOORDASH — THE ONIONS NOTE WAS BLANK

## 1. SELECTED MERCHANT / FOOD TYPE

**Merchant:** McDonald’s  
**Food:** **1 × Double Cheeseburger** (or **Cheeseburger** if Double unavailable) + optional **1 × Medium soft drink** (keep order simple: 1 main + optional drink).  

**Why this wins:**
- Diced onions are default and **visually obvious** on the burger (S1 food photo).  
- DoorDash exposes structured removals as **“No Diced Onions”** (not free-text).  
- Workspace contains a real **Order Complete** capture with that exact modifier string.  

**Limitation noted:** some McDonald’s locations have restricted “no diced onions” in-app after grill-process changes (public reports). If a live store blocks the modifier, keep the same DoorDash Order Complete grammar with another burger merchant that exposes structured `No onions` / `No diced onions`, or stop — do not invent a blank special-instructions field. For this spec, McDonald’s remains the clean researched option with verified UI.

## 2. VERIFIED SURFACE

**Primary story surface (S3):** DoorDash customer **Order Complete / order details** sheet (post-delivery or opened from Orders): merchant header + item rows with **gray modifier line under item name** + economic stack + payment.

**Not the story surface:** Dasher map-only, Live Activity lock screen, support chat, grocery substitution receipt (unless modifiers shown the same way).

## 3. REFERENCE(S) FOUND

| Path | What it shows | Relevance |
|---|---|---|
| `/workspace/creative-pipeline/outputs/proof_cand01_s2/base_mcd_order_complete.png` | **Real** DoorDash **Order Complete** McDonald’s: item “1 × 2 Cheeseburger Meal” with modifiers `French Fries · No Diced Onions · No Mustard · Hi-C® Orange · Medium`; Subtotal / Delivery Fee / Service Fee / Estimated Tax / Dasher Tip / Total; Payment; Address. | **Gold ref** for onion modifier + economic slot. |
| `/workspace/creative-pipeline/outputs/dd_step_refs_round3_20261002/pin_checkout_items.jpg` | Cart: Big Mac Meal modifiers include truncated `No...` after Extra American Cheese. | Confirms structured `No …` removals on McD carts. |
| `/workspace/creative-pipeline/outputs/dd_step_refs_20261002/checkout_items_total.jpg` | Checkout items: meal modifiers comma/gray under name; Total section Subtotal / Delivery Fee / Fees & Estimated Tax. | Checkout economic grammar. |
| `/workspace/creative-pipeline/outputs/dd_step_refs_round3_20261002/pin_order_complete_total.jpg` | Order Complete (Pasta Beach): gray modifier under item; full fee stack + credits + tip + Total + Payment + Address. | Same Order Complete skeleton. |
| `/workspace/creative-pipeline/outputs/cand06_isaiah_chipotle/order_screen_flat.png` | Order Complete Chipotle: gray ingredient list under Burrito Bowl. | Modifier-under-name pattern (inclusions). |
| `/workspace/creative-pipeline/HANDOFF_ASSETS/03_jalen_wingstop_posted/order_screen_flat_850x1850.png` | Order Complete Wingstop: gray flavor/combo modifiers. | Same pattern. |
| `/workspace/creative-pipeline/outputs/dd_carousel_library_20261002/board_assets/receipt_items.jpg` (+ round3 reddit twin) | Grocery receipt: items + Subtotal/fees/tips — **substitution** labels, not restaurant onion removals. | Economic stack only. |
| Web: NY Post / similar coverage of DoorDash McD checkout listing `no diced onions` among structured removals (2024 viral empty-box order). | External confirmation of the modifier string in DoorDash McD UI. |

## 4. CURRENT UI CONFIDENCE: **HIGH** (modifier + Order Complete layout)

Multiple real Order Complete / cart captures show gray structured modifiers under the item name, including **“No Diced Onions.”** Economic lines are consistent across refs.

**Residual caveat (not a UI invention ban):** merchant-side availability of the onion-removal option can vary by McD location/year — does not change how DoorDash **displays** the modifier when present.

## 5. EXACT FICTIONAL ORDER CONTENTS

| # | Item | Qty | Notes |
|---|---|---|---|
| 1 | Double Cheeseburger (or Cheeseburger) | 1 | Main; onions visible in S1 photo |
| 2 | Medium soft drink (optional) | 0 or 1 | Keep simple; omit if frame is tight |

No sides required. No multi-merchant cart.

## 6. EXACT CUSTOMIZATION STATE

**Story-true state for “the onions note was blank” / not submitted:**

- Under the burger item, the gray modifier line **does not** include `No Diced Onions` (or `No Onions`).  
- Other default/selected modifiers may appear (e.g. nothing, or drink size if meal) but **onion removal is absent**.  
- Roommate’s claim in S1/S2 (“copied my order exactly” / put no onions) is false relative to what DoorDash recorded.

**Do not stage:** a labeled empty “Special instructions:” text field unless a live capture proves that field exists on this merchant’s Order Complete (workspace refs show **structured modifiers**, not a blank note box).

## 7. HOW THE REAL UI REPRESENTS THAT CUSTOMIZATION

From `base_mcd_order_complete.png` and cart refs:

- Bold: `1 × [Item Name]`  
- Next line, smaller gray text: structured options separated by `·` or commas  
- Removals appear as **`No Diced Onions`**, `No Mustard`, etc. when selected  
- **Absence** of `No Diced Onions` in that gray line = not submitted  
- Long modifier strings may truncate with `...` on cart; Order Complete in gold ref shows full `No Diced Onions` readable

## 8. STORY INFORMATION THE SCREEN LITERALLY PROVES

- A DoorDash McDonald’s order was placed and completed.  
- Whether **no-onions was submitted** is answerable from the gray modifier line.  
- In the locked “blank/not submitted” outcome: onion removal was **never on the order** → roommate (or copy error) failed, not “restaurant ignored a note that was present.”  
- Prices can be unreadable; proof still holds.

## 9. FIELDS THE REAL UI SUPPORTS

- Order Complete title + timestamp / arrived time  
- Progress icons (store → car → house)  
- Merchant name + logo + item count  
- Item rows: thumbnail, qty × name, **gray modifiers**, item price  
- Economic stack commonly including: Subtotal, Delivery Fee (often strike → $0), Service Fee and/or Fees & Estimated Tax, Estimated Tax, Promo/Credits (when present), Dasher Tip, **Total**  
- Payment method + charge time  
- Address  
- Help / close controls  

## 10. FIELDS / BEHAVIORS WE MUST NOT INVENT

- A dedicated empty **“Special instructions”** / “Notes to store” row as the proof unless live-captured for that order  
- Fake “Onions: blank” checkbox UI  
- Invented Dasher chat proving kitchen error as the S3 surface  
- Grocery “Substituted with” chrome for this burger story  
- Fake MyDashPerks / promo copy unless a later math pass uses a verified native promo row (out of scope here — no amounts)  

## 11. ECONOMIC SLOT LOCATION

Directly **under the last item row**, right-aligned fee stack, then bold **Total**, then Payment — before Address. (Verified on Order Complete refs above.)

## 12. ECONOMIC SLOT VIABILITY: **STRONG**

Clear, consistent Subtotal → fees/tax → tip → Total column on Order Complete; easy to blur while leaving modifiers readable. Secondary discovery only.

## 13. STORY STILL WORKS WITH ALL ECONOMICS BLURRED: **YES**

Modifier line alone answers “was no-onions submitted?”

## 14. CAN THE UI CLEANLY PROVE THE ONION MISTAKE: **YES**

Via **presence vs absence** of structured `No Diced Onions` under the burger on Order Complete. Cleaner than free-text.  
**Requires** S1 food photo showing visible onions + S2 claim fight so absence on S3 closes the argument.

## 15. ANY MINIMAL STORY ADJUSTMENT REQUIRED

**MINIMAL UI-FORCED CLARIFICATION (not a rewrite of beats):**

- Locked title/premise language about a blank “note” / special-instructions field maps to DoorDash’s **real** proof: the gray **structured modifier** row under the burger.  
- S3 proves the mistake by showing **`No Diced Onions` absent** (submitted state = blank/not sent), **not** by inventing an empty labeled notes field.  
- S1–S3 sequence stays the same.

---

# CROSS-CHECK

## TARGET SURFACE READY FOR TRANSACTION MATH? **YES (structural)**

**Update (2026-10-05 EDT):** Target Reference Bank V2 ingested. Structural support for S2 Drive Up Ready + item-list proof is **HIGH**. Live signed-in combined viewport is **no longer a blocker**.

**Locked math + pre-production spec:**  
`/workspace/creative-pipeline/shared/research/ssg-orchestration-test/TARGET_CHORE_STUFF_TRANSACTION_MATH_SPEC.md`  
→ **TARGET TRANSACTION MATH LOCKED: YES** (staged/fictional amounts; item list is story proof; economics secondary).

**Residual honesty (not a blocker):** Discount nest uses checkout summary **label grammar** from bank ref 04 applied as secondary economics — do not invent fields beyond those labels.

## DOORDASH SURFACE READY FOR TRANSACTION MATH? **YES**

Order Complete economic stack is repeatedly verified (Subtotal, Delivery Fee, Service Fee / Fees & Estimated Tax, Estimated Tax, tip, Total, Payment). Modifiers and economics coexist on one screen; blur policy is clear.

---

# CAPTURE GAP SUMMARY (honesty)

| Need | Status |
|---|---|
| Target Order Details (Ready for Pickup) with item list + Order summary | **Bank V2 structural support YES** (`16`+`12`+`18`; economics grammar `04`) — live combined capture **not a blocker**; math locked in `TARGET_CHORE_STUFF_TRANSACTION_MATH_SPEC.md` |
| DoorDash McD Order Complete with `No Diced Onions` | **Present** (`base_mcd_order_complete.png`) |
| Browser live capture | Not required for Target S2 — bank V2 structural support elevates confidence without faking a live combined viewport |

