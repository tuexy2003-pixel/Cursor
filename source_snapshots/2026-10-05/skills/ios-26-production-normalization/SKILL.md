---
name: iOS 26 Production Normalization
description: >-
  Use when a researched phone screenshot is turned into a final creative asset.
  Normalizes device chrome to a modern iPhone on iOS 26 at 9:19.6, while keeping
  retailer facts limited to the reference family. Does not apply during
  research.
---
# iOS 26 production normalization

This rule applies only when a digital screenshot or screen moves from research or reference into final creative production.

Visual Surface Acquisition may use Android, older iOS, mobile web, editorial, organic-user, or other legitimate references to learn a commerce surface. The reference device does not determine the final production device.

Unless a concept explicitly requires another platform, final phone screenshots use:

- DEVICE FAMILY: modern iPhone
- OS PRESENTATION: iOS 26
- FINAL ASPECT RATIO: 9:19.6
- ORIENTATION: portrait

## Two layers

Treat every researched screenshot as two independent layers.

COMMERCE LAYER: retailer or app or site content. Headers, product and order information, totals, cards, buttons, retailer navigation, retailer typography, retailer icons, and transaction state.

DEVICE LAYER: status bar, time, signal, Wi-Fi, battery, safe areas, browser or device chrome when it applies, the bottom home indicator, and the overall screenshot canvas.

Preserve supported information from the commerce layer. Do not preserve incompatible Android or old-iOS device chrome just because it appears in the reference.

When a story continuity ledger exists, visible status-bar time and other story-relevant iOS temporal values must follow the current approved STORY_LOCK rather than stale values in the visual reference.

## Canonical template

Maintain one reusable iOS 26 screenshot template. Do not recreate device chrome independently for every asset, and do not redraw the status icons from memory on every generation.

Template ID: ios26-phone-9x19.6.

Master file: `/workspace/creative-pipeline/shared/templates/ios26-phone-9x19.6/ios26-phone-9x19.6_device_chrome.png`

Spec: `/workspace/creative-pipeline/shared/templates/ios26-phone-9x19.6/spec.json`

The master is a transparent 1206×2622 canvas. Locked pixels are the status glyphs lifted from the supplied Messages screenshot at `outputs/cand01_final_916/_w26/ref.png`. Everything else is the empty commerce slot. Do not stretch this file to force 9:19.6. The supplied screenshot is 1206×2622, which is close to 9:19.6 but not exact. Do not invent the home indicator, the bottom safe area, or side content margins. Those are unverified because that screenshot does not show them.

Use the same template across produced screenshots unless the source or context requires a legitimate variation. Time digits and status levels may change only inside the measured boxes in the spec.

## Reference translation

If the best reference is Android, use it to understand the retailer or app surface, not Android device chrome.

If the best reference is older iOS, use supported retailer structure, not obsolete iOS chrome.

If the reference is cropped, do not invent missing retailer UI just to fill the taller iOS canvas. Use other members of the reference family for missing structure. Otherwise mark that area unresolved.

If several references cover different portions of the same surface, they may inform reconstruction only where the state and version relationship is compatible. Do not merge states from different years into a fictional current UI.

## Truth boundary

Device normalization does not authorize changing transaction facts.

Never invent discounts, totals, purchases, rewards, promo codes, order states, products, balances, or retailer features to make the normalized screenshot more useful.

Device chrome can be normalized. Commercial facts cannot.

## Production brief

Every digital-screen production brief must contain:

- SOURCE REFERENCE FAMILY
- COMMERCE ELEMENTS OBSERVED
- COMMERCE ELEMENTS INFERRED
- COMMERCE ELEMENTS UNKNOWN
- SOURCE DEVICE
- PRODUCTION DEVICE: iPhone / iOS 26
- FINAL CANVAS: 9:19.6
- IOS 26 TEMPLATE: ios26-phone-9x19.6, or a named legitimate variation
- DEVICE-CHROME CHANGES
- COMMERCE-UI CHANGES
- CLAIM BOUNDARY

Track device-chrome changes and commerce-UI changes separately. A commerce-UI change that adds a fact not supported by the reference family is not allowed.
