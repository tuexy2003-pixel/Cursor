# QA — SHE SAID IT WAS CHORE STUFF carousel

## SLIDE 1 — iMessage
- Path: slide1_imessage.png (1206×2622) + slide1_imessage_9x16.png (1080×1920)
- Text exact: PASS (Drive Up / chore stuff don’t look / why would I look)
- Gray left / blue right: PASS
- Today 4:12 PM + status 4:14: PASS
- No extra messages: PASS
- Method: deterministic build_imessage_ios26.py
- **QA: PASS**

## SLIDE 2 — Target Order Details
- Path: slide2_target_order_details.png (1206×2622)
- Ready for pickup + Drive Up: PASS
- Four items exact titles/prices/qty/order: PASS
- Subtotal 12.98 / mydashperks.com Discount -8.00 / Tax 0.35 / Total 5.33: PASS
- No Circle/coupon/gift chrome: PASS
- Discount not boxed/arrowed: PASS
- **QA: PASS** (staged reconstruction; STAGED/FICTIONAL)

## SLIDE 3 — Birthday camera-roll
- Path: slide3_birthday_camera_roll.png (1080×1920)
- Cake + candles + streamers: PASS
- Paper towels ambient: PASS
- No Target UI / prices: PASS
- Casual not ad: PASS
- Note: source gen returned landscape; portrait is padded vertical compose — acceptable camera-roll candidate; optional polish later
- **QA: PASS**

## CONTINUITY: PASS
## ANY FIX REQUIRED: NONE blocking (optional: regenerate S3 as native portrait without letterbox padding)

PROVENANCE: STAGED/FICTIONAL TRANSACTION; NOT VERIFIED TARGET PROMOTION; NOT Target–MyDashPerks integration claim.
