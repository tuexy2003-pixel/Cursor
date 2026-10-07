# VIRAL CREATIVE CORPUS INVENTORY: MyDashPerks viral-story learning

Built: Mon 2026-10-05, ~2:14–2:30 PM ET; **Family D section updated ~2:55 PM ET** (executor subagent). **This is a RESEARCH-MODE artifact.** Every metric and comment here comes from a file on disk; the source is named in each row. Nothing is estimated or invented. "—" means no data on disk.

## How the search was done (broad inventory)
- **Roots searched:** `/workspace/creative-pipeline/` (all of `outputs/`, `shared/`, `sources/`, `HANDOFF_ASSETS/`, `shared/context/golden-example-assets/`, `_examples_stage/`, `assets/`), `/home/box/agent-data/` (`agents/*/attachments`, `agents/*/assets`, `workflows/`, `managed-skills/`), and `/workspace/uploads`.
- **Images indexed:** 745 unique images, deduped by content hash, in `_w/attach_index.json`. Contact sheets are in `_w/sheets/`.
  - "A###" = user-sent attachment.
  - "S###" = agent browser screenshot (scraping or QA). These are not corpus unless noted.
- **Images opened with Read and inspected:** every image cited in the cards, plus the contact sheets of all 745 (see `_w/sheets/`).
- **Text sources:**
  - `outputs/account_review_20261002.md`
  - `outputs/viral_comments_all_20261003.txt`
  - `outputs/tut_pinned_comments_20261004.txt`
  - `shared/context/mydashperks-golden-examples.md`
  - `shared/context/CURSOR_TASTE_AND_TRASH.md`
  - `outputs/dd_carousel_library_20261002/{LIBRARY,SLIDE_EXEC_BRIEF,AGENT_BRIEF}.md`
  - `SYSTEM_PLAYBOOK.md`, `HANDOFF_LATEST.md`, `CATCHUP.md`
  - `shared/research/hooks-tutpinned-{20260925,20261002}/` (report.md, top_posts.csv, covers, review sheets)
  - `sources/cards/*.json` (30)
  - `shared/research/lane-b-fyp-probe/`
  - `shared/research/ser-diagnostic/SER_DIAGNOSTIC_FINAL_REPORT.md` (its comment analysis is reused; the co-location direction is retired)
  - `shared/research/benchmark-run6/STORY_CONFLICT_FINDINGS.md`
  - `HANDOFF_ASSETS/*/README.txt`
- **Excluded as NOT corpus:** pipeline-generated concepts (viewer-state, commercial-occupation and benchmark-run concept outputs), agent QA renders, Pinterest/purchase-screen scrape screenshots, and unrelated-project images (skincare WIP chats, persona selfies, Nintendo/Target checkout refs of unknown origin). The unrelated-project images are listed in §G so nothing is hidden.

## Legend
- **STATUS**
  - POSTED: on one of our TikTok accounts.
  - REFERENCE: sent by the user/owner as a model.
  - TUTORIAL-PINNED: external competitor in the "tutorial pinned" niche.
  - EXTERNAL: other external post with a source card.
  - UNPOSTED: built or drafted internally, not posted.
  - UNKNOWN.
- **FAMILY:** STORY-LED / DESIRE-UTILITY-LED / HYBRID / OTHER. "ECON-LED" is noted where the only engine is the price drop. That is not a family the user named, so it is filed under OTHER or HYBRID with a note.
- **VISUAL ASSETS:** YES = slide images on disk and inspected. PARTIAL = some slides. COVER = video cover/keyframe only. NO.
- **CONFIDENCE** that the row is described correctly: H / M / L.
- **Performance tier** (from the playbook rule of promote ≥3% like rate, kill <1%, plus absolute reach): WIN / MID / WEAK / LOSER / UNKNOWN.

---
## A. OWN POSTED (11 posts, plus 1 with unknown posting status)

| ID | Creative | Account / origin | Status | Performance (source, snapshot) | Comment evidence | Family | Visual assets | Conf |
|---|---|---|---|---|---|---|---|---|
| P01 | "soo I overslept my DoorDash delivery 😭". Pink iPad. Dasher hid the Target bag behind the AC unit. 3 slides. **Tier: WIN.** | @hauls_bybrooke (Brooke), posted Sep 17 | POSTED | 2.32M plays / 162K likes (7.0%) / 655 cmts / 1,482 shares / 3,159 saves (account_review, Oct 2). 2.3M / 163.9K / 656 / 3,182 fav / 1,496 shares (viral_comments, Oct 3). | 18 top comments captured, e.g. "wait this is very nice of them" 96.4K; "how tf u fall asleep with a whole iPad on the way" 35.2K; "why is no one talking about the discount" 22.8K. | STORY-LED (with a desire object) → HYBRID | YES: `outputs/_account_review_assets/hauls_bybrooke_7686672779399204109_s0.png`, `_s1.png`; slide 3 = A605 (`agents/adee5ede…/attachments/63e6b01a…webp`); also A669, A546, A475 | H |
| P02 | "Dre" Chick-fil-A. Chat: "no eating out until friday" … "THAW IT" … "i got dinner handled" → CFA order. 2 slides. **Tier: WIN.** | @mariaaxo.x0 (Maria), Sep 25 (built as cand01) | POSTED | 334K plays / 39.4K likes (11.8%) / 168 cmts / 2,455 shares / 1,098 saves (account_review, Oct 2). 338.8K / 39.9K (viral_comments, Oct 3). Early: 81K / 7.2K at 21h (playbook). | 15+ captured, e.g. "WHERE TF… CHICKEN STRIPS ARE $30" 5.4K; "Why couldn't he cook?" 2.7K; "Both of yall wrong" 117. Early screenshot A535. | STORY-LED | YES: `_account_review_assets/mariaaxo…_s0/_s1.png`, `HANDOFF_ASSETS/01_dre_posted/`, `outputs/cand01_final_916/` | H |
| P03 | "I'm so pissed @DoorDash". McChicken order; the porch photo shows only the tea, straw in. 3 slides. Same post as GE-005. **Tier: MID.** | @mariaaxo.x0, Sep 20 | POSTED | 217.6K plays / 6.3K likes (2.9%) / 79 cmts / 215 shares / 287 saves (account_review). Owner: "did not convert, read as an ad" (golden-examples GE-005). | Captured: tipping culture 866 (661 replies); "with the straw in??! refund" 859; "dasher was hungry too"; "$20 off how??" 39; "undisclosed scam ad" 6. | HYBRID (complaint story + receipt-first) | YES: `shared/context/golden-example-assets/GE-005-*` (3 slides) | H |
| P04 | Maria part 2, "Cooking tonight 😌" (#chickfila). Overlay "part 2: he found out". Order bubble inside the chat. **Tier: WEAK.** | @mariaaxo.x0, Sep 27 | POSTED | 63.9–64.9K plays / 1.4K likes (2.1%) / 14 cmts (account_review) | No comment text captured | STORY-LED (sequel) | NO (slides not on disk; the account review describes them. It may be the cand04b Jalen part 2 build re-cast, but that is unverified) | L |
| P05 | "Jose" dasher, MacBook Neo. Dasher hid the bag. mydash −$430, total $508. **Tier: WEAK–MID** (4.1% like rate on 150K, but near-zero comments/shares). | @haulsbysaraah (Sarah), Sep 19 | POSTED | 150K plays / 6.1K likes (4.1%) / 13 cmts / 22 shares / 81 saves (account_review) | Captured: "How did you get that discount????" 54; "ur welcome by the way" 221; "Not them hiding it in the bush" 10; "door dashing a laptop is risky work" 12 | STORY-LED attempt → effectively ECON/DESIRE (HYBRID) | NO (slides not found anywhere on disk; the structure is known from the account review) | M |
| P06 | "ordered an iPad on DoorDash and my dasher got nosy 😭". SMS with dasher "Kiana" → Best Buy receipt → porch. 4 slides. Built as cand03. **Tier: LOSER; format killed.** | @haulsbysaraah, Sep 25 | POSTED | 62.7K plays / 285 likes (0.45%) / 5 cmts / 15 shares / 53 saves (account_review). 42.8K / 176 at ~21h (playbook). | 5 comments; no text captured beyond counts | OTHER (ECON-LED in story clothing) | YES: `HANDOFF_ASSETS/07_dasher_nosy_posted/`, `outputs/cand03_dasher_receipt/` (3 porch variants; which one was posted is unknown) | H |
| P07 | Boyfriend pink-iPad sequel. Meme chat "boyfriend = makes expensive things affordable" → unboxing "Shoutout to my bf" → Target order "$378 off applied". **Tier: LOSER.** | @hauls_bybrooke, Oct 1 | POSTED | ~4.6–5.1K plays / 159–166 likes / **0 comments** / 6–7 shares / 6–7 saves (account_review; viral_comments) | 0 comments | DESIRE/ECON flex (OTHER) | PARTIAL: order slide A457 (`agents/71956b4e…/attachments/7bf3c114…png`); slides 1–2 described only | M |
| P08 | "Jalen" part 1. "just spent $140 at kroger" … "chicken in the freezer" … "i got dinner handled" → Wingstop −$25 = $34.01. 2 slides. A near-clone of P02's beats. **Tier: MID** (healthy rate, low reach). | "account 3" (handle not on file), ~Sep 26 | POSTED | 29K views / 1,500 likes (~5.2%) / 21 cmts / 18 saves (playbook, Sep 27 7:26 AM). Earlier 12.4K / 752. | No comment text | STORY-LED | YES: `outputs/cand04_groceries_wingstop/slide1_chat_916.png`, `slide2_order_916.png` | H |
| P09 | Lindy Chick-fil-A breakfast. Order + Photos-Info meta slide. **Tier: LOSER.** | @lindybom94p (secondary account) | POSTED | 2.9K plays / 39 likes (1.4%) (account_review) | — | OTHER (receipt-led) | PARTIAL: `_account_review_assets/lindybom94p_…_s0.png` | M |
| P10 | Jenny video "#spoiled #pinkipad". Video, not a slideshow. **Tier: WEAK.** | Jenny account (account_review) | POSTED | ~22K plays / 683 likes (3.1%) (account_review) | — | DESIRE (flex) | NO | L |
| P11 | "She still has a cent". The Dre cent chat on Maria. **Tier: UNKNOWN** (owner judged it qualitatively weak). | @mariaaxo.x0 (per AGENT_BRIEF Oct 3: "already posted on Maria") | POSTED per AGENT_BRIEF wording ("Maria's already-posted Dre cent"); not in the Oct 2 account review, so unverified | Numbers not on file. Owner (AGENT_BRIEF): "that post is terrible next to the ones that did numbers" (the referent is ambiguous: it may mean the proposed remix) | — | STORY-LED (permission/budget argument) | YES: `outputs/carousel_banger_dre_maria_20261002/` (dre_chat.png, kai_chat.png variant); also `outputs/the_cent/` | M |
| P12 | "Cam / Cent". "ok i got 8.09. talk me out of spicy" → Cash App $0.01. 11 bubbles. **Tier: UNKNOWN.** | `outputs/carousel_banger_20261002`, marked "shipped" Oct 2 | UNKNOWN (no evidence it was posted) | — | — | STORY-LED | YES | M |

## B. OWN UNPOSTED / INTERNAL (built or drafted; zero performance evidence)

| ID | Creative | Path | Status | Family | Visual | Conf |
|---|---|---|---|---|---|---|
| U01 | Jalen part 2. PayPal "$34??", "frozen chicken 🙄", totals-crop image bubble. The "wait how" bubble consumes the viewer's method question. | `outputs/cand04b_jalen_part2/` | UNPOSTED (READY). Possibly P04; unverified. | STORY-LED sequel | YES | M |
| U02 | McDonald's "broke": Cash App $8.09 vs an $8.08 order | `outputs/cand02_broke/` | UNPOSTED / UNKNOWN (iPad device test never reported) | STORY-LED | YES | M |
| U03 | Terrence / Cheesecake Factory ("one for now one for later. that's called budgeting") | `outputs/cand05_terrence_cheesecake/` | UNPOSTED (superseded) | STORY-LED | YES | H |
| U04 | Isaiah / Chipotle ("you said you wasn't hungry earlier") | `outputs/cand06_isaiah_chipotle/` | UNPOSTED (on hold) | STORY-LED | YES | H |
| U05 | Sarah iPad lock→proof. Lock screen "Heading to you" 5:24 → proof $449 / −$374 / $89.23 | `outputs/sarah_ipad_20261002/` | UNPOSTED / UNKNOWN | HYBRID | YES | M |
| U06 | Lock-screen McDonald's draft | `outputs/our_lock_mcd*` | UNPOSTED | STORY-LED | YES | M |
| U07 | `our_versions_20261003` chats (lena, wes_priya, imani, greta, soren, hope) | `outputs/our_versions_20261003/` | UNPOSTED drafts | STORY-LED | YES | M |
| U08–U27 | LIBRARY: 20 internal carousel ideas (boards built from real reference assets) | `outputs/dd_carousel_library_20261002/LIBRARY.md` | UNPOSTED concepts | mixed | YES (boards) | M |

## C. REFERENCE (owner/user-sent models; performance only where the owner stated it)

| ID | Creative | Origin | Performance | Comments | Family | Visual | Conf |
|---|---|---|---|---|---|---|---|
| R01 / GE-001 | Target cart + "Dad" $180 "not stinky" chat (AI-deal family) | golden-examples GE-001 | Not on file | — | HYBRID (deal + family chat) | YES: A656, `shared/context/golden-example-assets/GE-001*` | H |
| R02 / GE-002 | Walmart MacBook $47 + Dad $60 | GE-002 | Not on file | — | HYBRID | YES: A688 | H |
| R03 / GE-003 | Pandora + Grandma $45 | GE-003 | Not on file | — | HYBRID | YES: A702 | H |
| R04 / GE-004 | Green-screen cat-meme reaction over a Coach order | GE-004 | Owner: high engagement (no number) | — | OTHER (meme reaction + order) | YES: A628 | M |
| R05 / GE-006 | @jakyriamarkia "What did I do to deserve him?" selfie → dream-camera chat with cart $998 → Canon SX740 + DualSense on the bed | GE-006 | Not on file | — | HYBRID (gift romance + desire object) | YES (GE-006 assets) | H |
| R06 / GE-007 | Chick-fil-A rewards alert | GE-007 | Not on file | — | DESIRE-UTILITY (notification) | YES: A617 | M |
| R07 / GE-008 | @basiccutiee7 "not waiting for nobody to feed me" → Wingstop past orders | GE-008 | Not on file | — | STORY-LED (identity/defiance) | YES: A663, A567, A545 | H |
| R08 | @suziegotdauzi: sister wants $640 for the light bill / "you had my kids 3 weeks" | owner-sent, called "mega-viral" (no number) | Qualitative only | — | STORY-LED (money ask, judgment) | YES: A691 | M |
| R09 | @suziegotdauzi: $85 field trip / "that's what the child support is for" / $327 court | owner-sent | Qualitative only | — | STORY-LED | YES: A612 | M |
| R10 | @suziegotdauzi: Cash App +$300 "for birthday stuff for lil man" → girlfriend "send at least $150 back, our lights are due Monday" | owner-sent | Qualitative only | — | STORY-LED | YES: A552, A565 | M |
| R11 | @maddiequinn51: crying selfie "i'm 24… best friend cancelled… saw her story… then she texted me this…" → lock-screen apology notification (dog wallpaper, "Your 20s" app notification) | owner-sent | Not on file | — | STORY-LED (friendship betrayal, reveal on lock screen) | YES: A689, A678 | M |
| R12 | @ricc5ever meme "bank acct 11.38 / combo 11.37 / make sure my fries fresh" (origin of the Cent idea) | owner-sent | Not on file | — | OTHER (meme, broke-identity) | YES: A727 | H |
| R13 | Meme "IDC how broke I am ima buy some to eat…" | owner-sent | — | — | OTHER (meme) | YES: A739 | M |
| R14 | Couple chat "mama wyd… so i texted… going through your repost" | owner-sent | — | — | STORY-LED (relationship) | YES: A733 | L |
| R15 | Lock-screen notification-stack template (Tyler Starbucks / Apple Cash $10 / Life360 82mph) | owner-sent (named in AGENT_BRIEF) | — | — | OTHER (surface template) | YES: A596, A682 | M |
| R16 | @kelsitopsecret food-identity selfie carousel ("Told them I struggle with food", "4 servings for 1 girl", "what should I make for lunch", "I skip meals too sometimes", "serving size is 1") | sent to the New Bot agent | Not on file | — | OTHER (identity humor, food) | YES: A411, A418, A419, A464, A524 | M |
| R17 | Phone photos of long emotional text chats (family letter-style) | owner-sent | — | — | STORY-LED | YES: A711, A714, A720 | L |

## D. EXTERNAL: FYP source cards (story/chat family; metrics from source cards)

| ID | Creative | Account | Performance | Comments | Family | Visual | Conf |
|---|---|---|---|---|---|---|---|
| X01 | Coach gift chat "money comes back babygirl" | ieatkungpao | 421.5K likes / 11.6K saves / 7,037 shares (source card). A 3.3M-play variant tile was seen (S341). | — | STORY-LED (gift + relationship logic) | COVER/keyframes: `shared/research/lane-b-fyp-probe/screenshots/` | H |
| X02 | Credit card "pay so I can swipe again" | ashley.almodovar | 136.2K likes | — | STORY-LED (money ask/relationship) | COVER | H |
| X03 | "$680 Marriott charge… you have a dorm" | frank.music23 | 29.2K likes | — | STORY-LED (parent audit/caught) | COVER | H |
| X04 | Vinted "do u have biceps" discount chat | tenaweng | 18.7K likes | — | STORY-LED (absurd negotiation) | COVER | H |
| X05 | $1/second math meme | ron7_editz | 11.4K likes | — | OTHER (math hypothetical) | COVER | H |

## E. EXTERNAL: desire/utility slideshow source cards (**UPDATED Mon 2026-10-05 Family D expansion**)

Prior note said "no media and no comments on disk." That was incomplete: slide CDN URLs were already inside `sources/cards/*.json`. The Family D expansion materialized slides + fetched comments for a priority set.

| ID | Niche | Account(s) | Performance (source card) | Family | Visual | Comments | Conf |
|---|---|---|---|---|---|---|---|
| X06 / D-FD01 | Meal prep | jalalsamfit | 41.7M views / 1.79M likes | DESIRE-UTILITY | YES (`family-d-expansion/slides/jalalsamfit_*`) | YES ORGANIC | H |
| X07 / D-FD02 | Meal prep | elliem650 | 9.97M views | DESIRE-UTILITY | YES | YES ORGANIC | H |
| X08 / D-FD03 | Soft glam | cya_scy | 8.38M | DESIRE-UTILITY | YES | YES ORGANIC | H |
| — / D-FD04 | Soft glam tut | bluberriella | 663K | DESIRE-UTILITY | YES | YES ORGANIC | H |
| X10 / D-FD06 | Amazon must-haves | silicon.finds | 2.4M | DESIRE-UTILITY | YES | YES ORGANIC | H |
| X11 / D-FD07 | Gift baskets | xcbadr (+reborn on disk) | 0.76–1.6M | DESIRE-UTILITY | YES | YES ORGANIC | H |
| — / D-FD05 | Protein lunch method | meals2glow | 1.98M | DESIRE-UTILITY | YES | YES ORGANIC | H |
| — / D-FD08 | Grocery haul+prices | cammyfurlong | 255K | DESIRE-UTILITY | PARTIAL (3/26) | YES ORGANIC | H/M |
| — / D-FD09 | Groceries vs prep | hagyans | 271K | DESIRE-UTILITY | YES | YES ORGANIC | H |
| — / D-FD10 | Cart→5 preps | success.mealprep | 790K / 52K saves | DESIRE-UTILITY | YES | metrics only | M |
| X12 | Target hauls | mspvrker / theglowjourney / maeg (D-FW04) | 55K–439K | DESIRE-UTILITY / weak | YES | — | M |
| X13 / D-FW01–03 | Uber Eats night | 3 accounts | 4–8K (weak) | DESIRE-UTILITY (weak) | YES | trivial | H |

Full cards: `family-d-expansion/FAMILY_D_CARDS.md`. Tut-pinned S6 desire shells with comments remain D-FD11/D-FD12.

## F. TUTORIAL-PINNED (external competitor niche): 75 unique posts across the 2026-09-25 and 2026-10-02 runs
All are videos (covers/first frames on disk; covers reviewed on the contact sheets). Comments were captured for 17 posts (`outputs/tut_pinned_comments_20261004.txt`); 1 of those returned 0 comments (aubreyvera4).

Shells:
- **S1** "this is your sign"
- **S4** "me at my big age running"
- **S5** price-only find / reaction
- **S6** "broke but [method] kept X full / made Y"

The 2026-10-02 run's verdicts are FLIP or SKIP. **Comment-contamination warning:** in the S6 threads, many 0–2-like "tried the method, worked tysm" comments and handle-plugging comments look SEEDED. Two threads also contain "this is MY video" / "literally not even your video", which suggests the shell accounts repost stolen footage.


### F-key. Tutorial-pinned posts with captured comments (carded in EXAMPLE_CARDS)
- **TP002 yasminaaa859, S6 boo basket.** 181K likes / 1.36M plays / 21K saves.
  - Organic-looking: "sold my Xbox to make her a boo basket" 6,057; "The basket was 12$" 3,080; price audits.
  - Suspected seeded: many 0–2-like "tried it, worked".
- **kissffkquk6, boo basket.** 27.7K likes / 125.6K plays: "What's the target method?" 336; "I work at target and this is true" 87; "Ts was not 3 dollars" 146.
- **donnam46z2, S6 "Moving in broke but the Aldi method kept the fridge full".** Organic comments are Aldi love; "where's the tutorial" 902.
- **sheissandra, Costco.** 150.8K plays / 4.1K likes: "My Costco method is getting my mom to take me" 47; "literally not even your video" 18.
- **Costco poster.** Commenter "This is MY video and none of this is from Costco" 82.
- **zita4807, B&M.** Price audits; "who gets Halloween gifts".
- **aubreyvera4, G7X "$67 at Target" sister reaction.** 134.8K likes / 1.15M plays. The API returned 0 comments.
- **Others with comments:** claudiamar_tin, dailaaa68, idamabwajui ×2, jesica64319, justurfavour, kim702926, margaretjkp9ky, nanneayzolp, user44741142415635 (Sam's Club "Moving day had me BROKE…"), yasminaaa859 #2. Mostly method-ask and thanks comments, many of them suspected seeded.

### F-full. All 75 tutorial-pinned posts (generated from both `top_posts.csv` files)
| ID | Author | Date | Likes | Plays | Cmts | Shares | Saves | Fmt | Shell | Verdict (2026-10-02 run) | On-screen hook (as captured) | Cover on disk | Comments captured | Runs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TP001 | ruthturners | 2026-09-26 | 186,248 | 1,401,083 | 782 | 19891 | 19087 | video | S5 | SKIP | $5.99 leopard heated blanket at Target | YES | no | 20261002 |
| TP002 | yasminaaa859 | 2026-09-26 | 181,071 | 1,359,725 | 259 | 5747 | 21027 | video | S6 | FLIP | Guess who's broke but still making bae a 10/10 boo basket using the Target method | YES | YES | 20261002 |
| TP003 | emma.harlow735 | 2026-09-17 | 169,674 | 948,866 | 265 | 28674 | 11603 | video | S4 | SKIP | me at my big age running to Build A Bear after they announced snoopy are $2 till September 24th 😭 | YES | no | 20261002,20260925 |
| TP004 | aubreyvera4 | 2026-08-21 | 134,778 | 1,152,589 | 102 | 3628 | 7293 | video | S5 | — | My sisters reaction after getting them their dream canon g7x camera for $67 at Target | YES | YES | 20260925 |
| TP005 | lazygtab9tk | 2026-09-29 | 50,470 | 299,159 | 135 | 7657 | 5136 | video | S1 | SKIP | this is your sign to run to Build-a-bear cos Lalaloopsy is back and it's only $1.99 till Oct 6th | YES | no | 20261002 |
| TP006 | tiffany.parker36 | 2026-09-14 | 44,878 | 339,449 | 81 | 3588 | 3783 | video | S4 | — | Not me losing myself at Coach bc all bags are 80% with the fall discount code | YES | no | 20260925 |
| TP007 | azeezmaryam09 | 2026-09-17 | 44,687 | 243,550 | 50 | 5236 | 4232 | video | S1 | SKIP | your sign to get the snoopy plush for the fall szn at Walmart cuz they are only $2 til September 25th | YES | no | 20261002,20260925 |
| TP008 | idamabwajui | 2026-09-29 | 41,048 | 204,971 | 25 | 1104 | 4369 | video | S6 | FLIP | guess who's broke but still making bae a 10/10 fall boo basket for boyfriend day using the target method | YES | YES | 20261002 |
| TP009 | haulsbypariis | 2026-09-11 | 39,633 | 180,713 | 62 | 2124 | 1739 | video | S5 | — | a man will look at this and think its $60 | YES | no | 20260925 |
| TP010 | dailaaa68 | 2026-09-27 | 38,943 | 327,913 | 77 | 1579 | 6572 | video | S6 | FLIP | guess who's broke but still making bae a 10/10 boo basket using the Target method | YES | YES | 20261002 |
| TP011 | yankovitchreffner615 | 2026-10-01 | 37,771 | 184,971 | 49 | 3329 | 4345 | video | S3 | SKIP | Ladies I beg you to run to build a bear bc all Hello kitty are $1.56 til October 10th | YES | no | 20261002 |
| TP012 | camila.eleanor87 | 2026-09-27 | 34,472 | 275,274 | 47 | 6212 | 5689 | video | S5 | SKIP | $5.99 leopard heated blanket at Target | YES | no | 20261002 |
| TP013 | quinn.harper6 | 2026-08-28 | 34,286 | 2,028,594 | 245 | 23052 | 8661 | video | S3 | NEW_PAGE | Who else is running to Target after finding out the Cloud Couch is only $65 til Sep 3rd 😭 | YES | no | 20261002,20260925 |
| TP014 | ahriadaily1 | 2026-09-28 | 31,265 | 1,654,994 | 363 | 25344 | 6962 | video | S1 | SKIP | ur sign to drag ur boyfriend to Best Buy because the Vizio 100inch Smart TV is only $180 until October 10th | YES | no | 20261002 |
| TP015 | mashenvjk10 | 2026-09-30 | 30,236 | 299,050 | 183 | 3331 | 3662 | video | S2 | SKIP | Friendly reminder Hollister fur jackets are $10 until Oct 3rd 😩😩 | YES | no | 20261002 |
| TP016 | idamabwajui | 2026-09-22 | 27,937 | 274,551 | 33 | 721 | 3505 | video | S6 | FLIP | when you wanna spoil your bf for halloween but your broke so you use the target method to make a 10/10 fall bo | YES | YES | 20261002,20260925 |
| TP017 | kissffkquk6 | 2026-08-25 | 27,709 | 125,603 | 104 | 911 | 2883 | video | S6 | FLIP | Guess who's broke this fall but still making bsf a 11/10 boo basket using the target method | YES | YES | 20261002 |
| TP018 | sheisdivea | 2026-08-22 | 27,293 | 370,483 | 52 | 7287 | 2087 | video | S4 | SKIP | me at my big age running to Build A Bear after they announced build a bear bats are $4 till August 26th | YES | no | 20261002 |
| TP019 | briannaclaire2002 | 2026-09-17 | 26,956 | 378,589 | 73 | 11502 | 3511 | video | S1 | — | your sign to get a pooh for the fall szn cuz they are only $1.99 til September 21st | YES | no | 20260925 |
| TP020 | user5633365600619 | 2026-09-17 | 26,531 | 210,613 | 248 | 4327 | 3297 | video | S2 | — | Friendly reminder to abandon all your plans and sprint to Costco cuz wdym fugglers baddies are only $2 til Sep | YES | no | 20260925 |
| TP021 | tabatovoph2 | 2026-09-18 | 26,467 | 217,054 | 239 | 6774 | 1878 | video | S2 | SKIP | Friendly reminder to abandon all your plans and sprint to home bargains cuz wdym fugglers baddies are only £2  | YES | no | 20261002,20260925 |
| TP022 | vanna0453 | 2026-09-29 | 24,663 | 220,849 | 154 | 4379 | 2366 | video | S3 | SKIP | Ladies I beg you to run to build a bear bc all oogie boogie are $2 till October 6th | YES | no | 20261002 |
| TP023 | divas.thorne | 2026-09-27 | 22,223 | 823,697 | 85 | 7076 | 4240 | video | S3 | SKIP | Moms! RUN to Walmart because they have the Skylight Calendar for the price of $58 until October 5th | YES | no | 20261002 |
| TP024 | sephoramethod11 | 2026-09-01 | 19,832 | 467,050 | 122 | 409 | 3655 | video | S6 | — | 🙎: son why are you always going to Sephora your broke... | YES | no | 20260925 |
| TP025 | kayla.berry266 | 2026-09-11 | 19,173 | 187,746 | 90 | 5507 | 1554 | video | S3 | — | Girls with besties I beg you to RUN to Windsor bc every clothes are $6 till September 18th | YES | no | 20260925 |
| TP026 | donnam46z2 | 2026-09-24 | 17,792 | 114,392 | 76 | 591 | 2229 | video | S6 | — | Moving in broke but the Aldi method kept the fridge full😭🙏 | YES | YES | 20260925 |
| TP027 | jesica64319 | 2026-09-27 | 15,755 | 124,212 | 31 | 1090 | 2434 | video | S6 | FLIP | pov u moved in broke with ur bf but the Aldi method kept the fridge full 😭🙏 | YES | YES | 20261002 |
| TP028 | melisa98820 | 2026-09-08 | 15,224 | 135,933 | 48 | 3163 | 1198 | video | S3 | — | Run don't work this fall season cos the viral snoopy teddy are only $3.99 til September 11th | YES | no | 20260925 |
| TP029 | briannaclaire2002 | 2026-09-21 | 13,066 | 138,735 | 31 | 4905 | 1824 | video | S1 | — | your sign to grab ur girls and run to Build A Bear cuz Hello Kittys are only $1.[9]9 till September 27th ✨ | YES | no | 20260925 |
| TP030 | zita4807 | 2026-09-15 | 12,338 | 210,560 | 158 | 3921 | 1141 | video | S6 | — | Mumss!! this is your sign to stop overthinking your girls halloween gift and make her a boo basket using the b | YES | YES | 20260925 |
| TP031 | patriciaallen_8199 | 2026-09-13 | 12,321 | 1,002,839 | 260 | 15433 | 4030 | video | S2 | SKIP | Friendly reminder: Target has a 65" Roku TV for $49 until September 18th 🎯 | YES | no | 20261002,20260925 |
| TP032 | yasminaaa859 | 2026-09-28 | 11,862 | 72,736 | 48 | 371 | 1568 | video | S6 | FLIP | Guess who's broke but still making bae a cute boo basket with the target method 😭 | YES | YES | 20261002 |
| TP033 | margaretturner_742010 | 2026-09-20 | 11,516 | 137,032 | 85 | 3441 | 1245 | video | S1 | SKIP | Your sign to get a pooh for the fall szn cuz they are only $1.99 til Sep 22nd | YES | no | 20261002,20260925 |
| TP034 | margaretjkp9ky | 2026-09-23 | 11,149 | 129,568 | 36 | 416 | 1971 | video | S6 | FLIP | Moving in broke but the costco method kept the fridge full😭🙏 | YES | YES | 20261002,20260925 |
| TP035 | meganlily689 | 2026-09-20 | 10,436 | 199,473 | 65 | 3886 | 1033 | video | S4 | — | me and my side quest partner sprinting to build a bear cuz Oogie Boogie are only $3.99 til September 25th 🎃 | YES | no | 20260925 |
| TP036 | cutieceline0 | 2026-09-09 | 9,578 | 106,325 | 13 | 2988 | 1412 | video | S4 | — | me at my big age running to Build A Bear after they announced Giant jumbo Bat are $4 till September 15th | YES | no | 20260925 |
| TP037 | aylaemery2003 | 2026-09-24 | 9,566 | 110,422 | 42 | 4807 | 607 | video | S1 | — | POV: ur cue to rush to ur local Build-A-Bear bcz Minions are only $2.99 til September 30th 🤣✨ | YES | no | 20260925 |
| TP038 | claudiamar_tin | 2026-09-27 | 7,779 | 257,753 | 56 | 397 | 1638 | video | S6 | FLIP | Moving in broke but at least I figured out how to save on groceries with Sam's Club method 😭 | YES | YES | 20261002 |
| TP039 | christi1561 | 2026-09-14 | 7,394 | 36,104 | 50 | 543 | 688 | video | S4 | — | me after bed rotting all day then running to Barnes & Noble cuz wdym all Calico Critters are $3 til September  | YES | no | 20260925 |
| TP040 | ava.blenda | 2026-10-01 | 6,850 | 135,078 | 25 | 3210 | 845 | video | S3 | SKIP | MUMSS!!! don't walk Run to Hobby Lobby bc Halloween Decor are $2 till October 15th | YES | no | 20261002 |
| TP041 | elowen6852 | 2026-09-20 | 6,812 | 97,417 | 52 | 1917 | 1453 | video | S1 | — | lego lovers!!! your sign to get the lego storage unit at target cuz they are only $2 til September 27th | YES | no | 20260925 |
| TP042 | mariaroberts_5604786 | 2026-09-27 | 5,952 | 45,027 | 59 | 854 | 894 | video | S3 | SKIP | u need run now to build-a-bear bc My Little Pony is back and is only $1.89 till September 30th | YES | no | 20261002 |
| TP043 | tiya_barbz | 2026-09-16 | 5,909 | 100,140 | 63 | 490 | 936 | video | S1 | NEW_PAGE | this is your sign to use that student discount at Best Buy & get $400 off the MacBook Neo!! | YES | no | 20261002 |
| TP044 | andy.lasy7 | 2026-09-23 | 5,860 | 154,989 | 29 | 4145 | 676 | video | S1 | — | POV: ur cue to run to ur local build a bear bcz Grinch are only $4.99 till September 30th ✨ | YES | no | 20260925 |
| TP045 | lilymorganfinds | 2026-09-06 | 5,731 | 513,472 | 59 | 1880 | 1304 | video | S3 | — | LADIES!! RUN to Walmart for this couch with $250 gift card for the Labor Day till September 7th | YES | no | 20260925 |
| TP046 | aylaemery2003 | 2026-09-21 | 5,697 | 58,858 | 19 | 1001 | 615 | video | S1 | — | your sign to run to build a bear bc Hello Kitty is only $2.[?]9 till September 2[?]th ✨ | YES | no | 20260925 |
| TP047 | kim702926 | 2026-09-18 | 5,460 | 95,108 | 11 | 631 | 960 | video | S5 | FLIP | My fav part about being a student rn 😭🍝 | YES | YES | 20261002,20260925 |
| TP048 | emma.harlow735 | 2026-09-26 | 5,338 | 47,222 | 49 | 788 | 586 | video | S3 | SKIP | U need ran to build a bear coz My Little pony is BACK and are only $2 til Sep 30th | YES | no | 20261002 |
| TP049 | magancarter7 | 2026-09-29 | 5,202 | 122,708 | 35 | 1215 | 700 | video | S3 | SKIP | grab ur bestie and RUN bc macbook is $119 till 30th September 🏃‍♀️ | YES | no | 20261002 |
| TP050 | deborahharris_2720122010 | 2026-09-28 | 5,176 | 164,328 | 209 | 4178 | 2040 | video | S5 | SKIP | $5.99 leopard heated blanket at Target till October 2nd | YES | no | 20261002 |
| TP051 | avathompsonhall | 2026-09-12 | 5,106 | 322,185 | 78 | 5406 | 2355 | video | S2 | — | Friendly reminder to run to Target bc this Vanity Desk is only $49 until September 24th | YES | no | 20260925 |
| TP052 | i.liyahbanks | 2026-09-23 | 5,053 | 136,403 | 25 | 2171 | 1474 | video | S3 | NEW_PAGE | Girls grab your bf and RUN! to Target bcs Cloud Couch $65 until 28th Sept 🌸🥹 | YES | no | 20261002,20260925 |
| TP053 | donna.hall06 | 2026-09-11 | 4,828 | 159,094 | 43 | 4363 | 1303 | video | S2 | — | Friendly reminder to RUN to Spirit Halloween you can get any costume for $7 till September 19th 🥹 | YES | no | 20260925 |
| TP054 | elianxeo00r | 2026-09-13 | 4,367 | 161,910 | 150 | 1486 | 933 | video | S3 | — | Mommas, If u need a stroller, RUN 🏃 This Evenflo one is only $49 at Walmart until September 20th! 🌺 | YES | no | 20260925 |
| TP055 | sheissandra | 2026-09-26 | 4,127 | 150,802 | 7 | 86 | 336 | video | S6 | FLIP | pov u moved in broke with ur bf but the Costco method kept the fridge full 😭🙏 | YES | YES | 20261002 |
| TP056 | brian.val626 | 2026-09-27 | 3,779 | 48,385 | 23 | 921 | 622 | video | S2 | SKIP | Friendly reminder to grab two Oogie Boogie at Build-A-Bear with your sis for $1.86 till October 3rd 🤯 | YES | no | 20261002 |
| TP057 | nanneayzolp | 2026-09-30 | 3,558 | 43,267 | 3 | 53 | 533 | video | S1+S6 | FLIP | your sign to make your bf a 10/10 boyfriend day boo basket even though your broke by using the target method | YES | YES | 20261002 |
| TP058 | user4891611006758 | 2026-09-08 | 3,518 | 77,176 | 33 | 1820 | 894 | video | S2 | — | Friendly reminder to take advantage of Build a bear discount promo and build a bear for $5 till Halloween | YES | no | 20260925 |
| TP059 | sophilghjwq | 2026-09-30 | 3,009 | 22,950 | 41 | 756 | 339 | video | S2 | SKIP | Friendly reminder Fugglers are $3 at Walmart till Oct 5th 🥹 | YES | no | 20261002 |
| TP060 | justurfavour | 2026-09-26 | 2,986 | 47,885 | 3 | 87 | 457 | video | S6 | FLIP | pov u moved in broke but the Costco method kept the fridge full 😭🙏 | YES | YES | 20261002 |
| TP061 | user44741142415635 | 2026-09-24 | 2,941 | 36,602 | 7 | 88 | 237 | video | S6 | FLIP | Moving day had me BROKE but pantry's going to be full thanks to the samsclub method 🙏🏽 | YES | YES | 20261002 |
| TP062 | andy.lasy7 | 2026-09-24 | 2,892 | 32,445 | 10 | 1469 | 307 | video | S1 | — | ur cue to run to build-a-bear rn bc Scooby Doo is back and is only $9 till September 30th 😉 | YES | no | 20260925 |
| TP063 | emma.harlow735 | 2026-09-27 | 2,740 | 45,664 | 35 | 1652 | 346 | video | S4 | SKIP | POV: U going to Build a bear coz big Snoopy they're only $2 til October 2nd | YES | no | 20261002 |
| TP064 | alishxbgi5k | 2026-09-07 | 2,213 | 40,670 | 22 | 785 | 368 | video | S4 | NEW_PAGE | POV: we skipped all our evening plans just to sit at red lobster bcs meals are $4 till september 13th 😭🏃 | YES | no | 20261002,20260925 |
| TP065 | christi42779 | 2026-09-12 | 2,049 | 134,451 | 58 | 948 | 614 | video | S2 | — | Friendly reminder to use ur Best Buy Student Discount on iPhonr 18 pro before September 16th | YES | no | 20260925 |
| TP066 | terranlikekaren | 2026-09-28 | 1,985 | 41,595 | 119 | 268 | 618 | video | S5 | SKIP | How to make $200 a day on DoorDash (dasher earnings) | YES | no | 20261002 |
| TP067 | user2995962818686 | 2026-09-21 | 1,981 | 18,244 | 7 | 208 | 330 | video | S3 | — | RUN DONT WALK to ur local Lego bc The nightmare before Christmas are only $3.99 till September 25th | YES | no | 20260925 |
| TP068 | charlotteoliviayy | 2026-09-07 | 1,874 | 42,694 | 72 | 883 | 518 | video | S4 | NEW_PAGE | POV: we skipped all our evening plans just to sit at red lobster bcs meals are $4 till september 13th 😭🏃 | YES | no | 20261002,20260925 |
| TP069 | peyton7042 | 2026-09-23 | 1,860 | 79,556 | 24 | 2188 | 292 | video | S3 | — | Moms with kids under 5 years old RUN to Kohl's because kids clothes are $1 this week | YES | no | 20260925 |
| TP070 | jenniferphillips_759 | 2026-09-15 | 1,700 | 80,243 | 24 | 1384 | 534 | video | S3 | — | Who else is running to Target after finding out this cozy heated faux fur throw is only $5.99 😭🐆🔥 | YES | no | 20260925 |
| TP071 | deborahjones_8647141 | 2026-09-22 | 1,043 | 14,597 | 12 | 340 | 163 | video | S3 | — | RUN DONT WALK to ur local build a bear bc Oogie Boogie are $2.99 till September 25th | YES | no | 20260925 |
| TP072 | slidimsh6um | 2026-09-22 | 996 | 7,827 | 34 | 44 | 88 | video | S5 | — | How are we supposed to act normal when windsor just dropped $6 hoco dresses | YES | no | 20260925 |
| TP073 | iyana5385 | 2026-09-23 | 946 | 34,202 | 5 | 1250 | 145 | video | S3 | — | Moms if you have kids under 5 RUN to Kohl's because baby clothes are $1 all week | YES | no | 20260925 |
| TP074 | penny.a.sinnott | 2026-09-07 | 884 | 78,530 | 26 | 371 | 254 | video | S4 | — | girlss im RUNNING to target finding this GRACO slimfit is only $39.99 after applying the coupon lasting till S | YES | no | 20260925 |
| TP075 | elenayolnmg | 2026-09-23 | 789 | 29,746 | 33 | 183 | 340 | video | S4 | — | not me RUNNING to WALMART because this Samsung bespoke was only $168 🏃😭 | YES | no | 20260925 |

## G. Found but NOT corpus (listed for transparency)
- **Unrelated-project images in agent attachments:**
  - Skincare chat WIP: "yellow cleanser… my face is mad at me / it's just adjusting keep going" (A412, A415, A425, A512, A526), plus acne/persona selfies.
  - Nintendo Switch and Target checkout refs.
  - Origin and project are unknown, so they are **not used** as evidence.
  - The skincare chat is noted as a possible beauty-family **surface** example only (confidence L).
- **Agent browser screenshots (S###):** Pinterest purchase screens, DoorDash store pages, TikTok grids. These are infrastructure, not creatives. Exception: S341, the 3.3M-play Coach-chat tile, is noted on X01.
- **Pipeline-generated concepts** (viewer-state, commercial-occupation, benchmark runs): these are our own outputs, not evidence of virality. Excluded.

## H. Real-world event ingredient bank (RESEARCH-mode only; not creatives)
- **What it is:** `shared/research/benchmark-run6/STORY_CONFLICT_FINDINGS.md` holds 25 web-researched real events (SCF-R6-001…025).
- **How it may be used:** as RESEARCH-mode situation ingredients, e.g. "this social rule is currently argued about".
- **What it is not:** viral creatives. It carries no evidence about creative performance.
- **Do not present** a fictional premise as one of these events, or the reverse.

---
## COUNTS (after inventory)

| Bucket | Count | With visual assets on disk | With performance numbers | With captured comment text |
|---|---|---|---|---|
| Own POSTED (P01–P11) | 11 | 8 YES/PARTIAL (P01, P02, P03, P06, P07 partial, P08, P09 partial, P11) | 10 (P11 has none) | 4 (P01, P02, P03, P05) |
| Own unknown-posted (P12) | 1 | 1 | 0 | 0 |
| Own UNPOSTED (U01–U07 builds + 20 LIBRARY ideas) | 7 + 20 | all | 0 | 0 |
| REFERENCE (R01–R17; GE-005 = P03 and GE-009 = P01, so not double-counted) | 17 | 17 | 0 numeric (owner qualitative on 4) | 0 |
| EXTERNAL FYP story/chat cards (X01–X05) | 5 | 5 (cover/keyframes) | 5 | 0 |
| EXTERNAL desire/utility cards (X06–X13; 25 underlying cards) | 8 groups / 25 cards | 0 | 25 | 0 |
| TUTORIAL-PINNED (TP001–TP075) | 75 | 75 (covers) | 75 | 16 non-empty threads (17 fetched) |
| Real-event ingredients (not creatives) | 25 | — | — | — |
| **Usable creative examples total** | **11 + 1 + 27 + 17 + 5 + 25 + 75 = 161** | | | |
| **Carded examples** (EXAMPLE_CARDS) | **37 examples in 28 card blocks** | | | |

**Performance-tier pairs available for contrast:**
- Same account and same object family with opposite outcomes:
  - P01 vs P07 (Brooke, pink iPad)
  - P01 vs P05 (hide-bag kit, iPad vs MacBook)
  - P01 vs P06 (iPad + dasher)
  - P02 vs P08 / P04 (food chat)
  - P03 (mid)
- External:
  - TP002 vs TP001/TP003 (S6 method story vs S5/S4 price-only; all high-performing, but with different comment shape)
  - X01–X04 vs X05
