# Target AirPods + birthday candle options (researched 2026-10-05, ~8:10 PM ET)

Method: target.com product-page HTML (titles, TCINs, canonical URLs, scene7 image IDs, DPCI) fetched directly.
Target loads prices client-side, and the redsky price API and a headless render both hit a PerimeterX bot block,
so **no price below was read live off target.com on Oct 5**. Prices come from search-index snippets of the Target pages,
deal trackers (Slickdeals, Thrifle, pricearchive, buyhatke), and apple.com. Each one is labeled with its source.

## 1. AirPods at Target

Note: the "Apple AirPods 4" parent page is A-93606140 (https://www.target.com/p/apple-airpods-4/-/A-93606140). It's a
variation page that groups the two AirPods 4 versions below.

| Item | Exact Target title | TCIN / DPCI | URL | Regular | Sale / recent | Confidence |
|---|---|---|---|---|---|---|
| **AirPods 4 (no ANC), RECOMMENDED** | Apple AirPods 4 Wireless Earbuds | 85978615 / 057-10-6413 | https://www.target.com/p/ap2022-true-wireless-bluetooth-headphones/-/A-85978615 | $129.99 at Target (search snippet + pricearchive "last price 129.99", ~Sep 9 2026). Apple MSRP $129 (apple.com) | $99.99 (pricearchive "<1 week" as of Oct 5; buyhatke "Target $99.99, 22% off $129"; Slickdeals Target thread 2026-09-13 "$99"). Not confirmed live on Oct 5 | Title/TCIN high. Regular price medium. Sale price medium-low |
| AirPods 4 with ANC | Apple AirPods 4 Wireless Earbuds with Active Noise Cancellation | 85978618 / 057-10-1345 | https://www.target.com/p/ap2022-true-wireless-bluetooth-headphones/-/A-85978618 | $179.99 at Target (search snippet). Apple MSRP $179 | $149.99 (Sep 2026 Target sale per search snippet; pricearchive "<1 week"). Slickdeals 2026-09-13 showed $179 at Target | Title/TCIN high. Prices medium-low |
| AirPods Pro 3 (current Pro) | Apple AirPods Pro 3 Wireless Earbuds with Active Noise Cancellation | 85978609 / 057-10-8384 (UPC 195950543698) | https://www.target.com/p/ap2022-true-wireless-bluetooth-headphones/-/A-85978609 | $249.99 at Target (Thrifle 2026-10-04 "$50 below $249.99"). Apple MSRP $249 | **SALE $199.99 starting Sun Oct 4, 2026** (Slickdeals 2026-10-02 "[Starts 10/04]"; Thrifle 2026-10-04). pricearchive shows $224.99, so it conflicts | Title/TCIN high. Sale medium |

Not used: Target Certified Refurbished AirPods 4 ANC (A-94200136) and Refurbished AirPods Pro 3 (A-95063377).

**Pickup / Drive Up:** all three product pages show the "Pickup" and "Delivery" fulfillment options, and the page data has
`eligibility_rules.hold.is_active=true` with a purchase limit of 2. The parent page's meta description says "Choose from Same Day Delivery, Drive Up or Order Pickup"
(that's Target's generic boilerplate). No page explicitly confirmed Drive Up for AirPods, but since the item is pickup-eligible, a Drive Up order
including AirPods is **plausible**. Unverified.

**Recommendation:** AirPods 4 (base, no ANC), TCIN 85978615. It's the cheapest current AirPods and the most natural
sister-to-sibling gift. Ordinary base price **$129.99** (Target regular). If the order should show a sale, $99.99 is the
recently seen Target sale price, but I couldn't confirm it live on 10/5. Displaying $129.99 is the safer "ordinary" choice.

## 2. Birthday candles (all Spritz, Target's owned party brand)

| Slot | Exact Target title | TCIN | URL | Price | Confidence |
|---|---|---|---|---|---|
| NORMAL (current) | 20ct Classic Colors Birthday Candles - Spritz™ | 50398491 | https://www.target.com/p/20ct-classic-colors-birthday-candles-spritz-8482/-/A-50398491 | $3.00 regular (search snippet, $0.15/ea). Red/yellow/orange/green/blue, 2 5/16" | High |
| PRETTIER (pick) | Gold/Silver Tall Spiral Birthday Candles 12ct - Spritz™ | 92290028 | https://www.target.com/p/gold-silver-tall-spiral-birthday-candles-12ct-spritz-8482/-/A-92290028 | $3.00 regular (search snippet, $0.25/ea). Gold, silver, and white-with-gold-speckle, 5¾" tall | Title/TCIN high. Price medium |
| PRETTIER (alt, pastel) | 10ct Pastel Rainbow Swirl Birthday Candles - Spritz™ | 92331479 | https://www.target.com/p/10ct-neon-rainbow-swirl-candle-spritz-8482/-/A-92331479 (the URL slug really says "neon") | $3.00 regular (search snippet, $0.30/ea). Pastel spirals, 2 7/8" | Title/TCIN high. Price medium |
| FUNNY / COMMENTABLE (pick) | Number 1 Birthday Candle Gold - Spritz™ | 92289968 (DPCI 053-03-7569) | https://www.target.com/p/number-1-gold-candle-spritz-8482/-/A-92289968 | $3.00 regular (search snippet. A review on the page says "especially for $3"). 4" gold glitter numeral on a pick | High |
| FUNNY (alt) | Gold Happy Birthday Candle - Spritz™ | 89280810 | https://www.target.com/p/gold-happy-birthday-candle-spritz-8482/-/A-89280810 | $3.00 regular (search snippet) | Title/TCIN high. Price medium |

Why the number candle is the funny pick: a single "1" (or any wrong digit) on a teen's cake invites "she thinks you're turning 1??"
comments. Other digits use the same parent listing, "Number Birthday Candle Gold - Spritz™" A-95232408: 0=92289964, 1=92289968,
2=92289972, 3=92289971, 4=92289967, 5=92289963, 6=92289966, 7=92289970, 8=92289965, 9=92289969 (Spritz digits list at $3 each per snippet).
Another commentable option: "Number 6 Sparkler Flame Candle by Unique Industries..." A-81254376, a 7" sparkler-style number. Its price is unverified (snippets say ~$3 for the 1/7 versions).

**Searched for and NOT found at Target:** self-relighting trick candles. Target searches for "relighting candles" and "trick candles"
only turn up sparkler, LED, or Halloween items, and no Spritz relighting SKU came up. Don't use "trick candles from Target" in the story.

## 3. Images (Target scene7 CDN, downloaded at 1200px)

| File | Source |
|---|---|
| airpods4_A-85978615_case.jpg (earbuds in open case, **best cart thumbnail**) | https://target.scene7.com/is/image/Target/GUEST_7c0b817f-9773-4ec4-b4d0-ce1563473cd7 |
| airpods4_A-85978615.jpg (primary listing image, earbuds only. The ANC listing 85978618 uses the same primary image) | https://target.scene7.com/is/image/Target/GUEST_abe46d5d-4336-4839-a5e9-62212c77be23 |
| airpods-pro3_A-85978609.jpg | https://target.scene7.com/is/image/Target/GUEST_d1b8c229-751b-430b-a0fb-521d7777a784 |
| candle-normal_spritz-20ct-classic_A-50398491.jpg | https://target.scene7.com/is/image/Target/GUEST_b5a07afd-f325-4902-9efc-e995bbf466b9 |
| candle-pretty_spritz-gold-silver-tall-spiral-12ct_A-92290028.jpg | https://target.scene7.com/is/image/Target/GUEST_95664aa8-2dfc-4be4-8cd9-36612b3a0eb7 |
| candle-pretty-alt_spritz-pastel-rainbow-swirl-10ct_A-92331479.jpg | https://target.scene7.com/is/image/Target/GUEST_07281290-9c0f-4852-878f-f9e8096c0d11 |
| candle-funny_spritz-number-1-gold_A-92289968.jpg | https://target.scene7.com/is/image/Target/GUEST_99dd8c66-e098-4a88-8769-9e78ca38eb66 |
| candle-funny-alt_spritz-gold-happy-birthday_A-89280810.jpg | https://target.scene7.com/is/image/Target/GUEST_0bb81738-285c-4a0a-9002-09b1d358867f |

## Suggested updated cart (using regular prices)
Spritz 20ct Classic $3.00 (or Gold/Silver Tall Spiral 12ct $3.00 / Number 1 Gold $3.00), Funfetti $1.99, Streamer 4pk $3.00,
Bounty Mega Roll $4.99, Apple AirPods 4 $129.99. Subtotal: **$142.97** before tax. Swapping candles doesn't change it because every option is $3.00.
With AirPods 4 at the $99.99 sale price instead: $112.97.
