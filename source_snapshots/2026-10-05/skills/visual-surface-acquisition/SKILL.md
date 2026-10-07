---
name: Visual Surface Acquisition
description: >-
  Use when a specific digital or physical commerce surface must be seen, not
  merely described. Hunts current pixels through text, behavioral, and
  visual-similarity search, preferring organic screenshots over marketing
  composites, or decides a real capture is required. Does not write concepts or
  prove a transaction.
---
# Visual Surface Acquisition

Acquisition and research only. Given one required digital or physical surface, find what it currently looks like and return the strongest usable references, or determine that a reliable reference cannot be found.

Do not generate carousel concepts. Do not run Object & Culture Scout, Story & Conflict Scout, Adaptation Blitz, or Commerce World Mapper. Do not modify those skills. Do not invent pixels to turn a failed search into a success.

Commerce World Mapper establishes that a surface exists and what it can prove. This skill establishes appearance.

An image may be useful for discovery without being trustworthy enough for reconstruction. Keep those uses separate.

## Input

- COMMERCE WORLD
- NEEDED SURFACE
- INFORMATION IT MUST SHOW
- WHY IT IS NEEDED
- CLAIM BOUNDARY

Optional: DEVICE / PLATFORM, DATE/FRESHNESS REQUIREMENT, KNOWN REFERENCE.

## Search behavior

Text search is only the first discovery mechanism. Do not stop after ordinary web results. Search the surface, not merely the company.

Use whatever is accessible and appropriate: official pages and help, web search, image search, Reddit, TikTok and other social results, Pinterest, YouTube and tutorials, App Store and Play Store media, press, blogs and tutorials that contain genuine screenshots, forums, and current user photos.

Text documentation alone does not satisfy a request for pixels. A help article that names a button does not establish layout.

### Broad-first queries

Do not assume the most precise textual query is the best discovery query. Begin with several granularities, then let visual chaining find neighboring surfaces.

- BROAD, such as "Target order receipt app."
- SURFACE, such as "Target order summary screenshot."
- STATE, such as "Target pickup checkout screenshot."
- BEHAVIORAL, such as "Target discount not showing reddit," "Target order total wrong," or "Target pickup order problem."

A broad query is often a better seed-finder than an exact UI-state query.

### Indirect and behavioral search

Do not search only for the formal name of the required surface. Direct queries mostly return SEO tutorials, corporate help graphics, and marketing.

Also search for situations where an ordinary person would expose that surface while talking about something else. Apply this to every commerce world. Build query families around:

PROBLEM, CONFUSION, GLITCH, COMPLAINT, QUESTION, WAIT, WRONG ITEM, ORDER STATUS, PRICE, PROMO, REFUND, RETURN, DELIVERY, PICKUP, HAUL, RECEIPT, SUPPORT.

Example for a Target Drive Up arrival screen: do not stop at "Target Drive Up barcode screenshot." Also search combinations like "Target Drive Up app problem," "Target Drive Up I'm here reddit," "Target pickup app screenshot reddit," "Target Drive Up wait screenshot," "Target app pickup glitch," "my Target Drive Up order," and "Target order ready screenshot," plus site-specific variants.

The goal is naturally occurring UI, not another explanation of the feature.

### Visual chaining

When a search returns a visually relevant image, even if it is old, partial, editorial, promotional, or insufficient as final evidence, treat it as a potential visual seed. A seed does not need to meet the freshness or authenticity bar. Its second job is to find visually similar artifacts. Do not mistake seed quality for evidence quality.

1. Text discovery. Search broad natural-language and behavioral queries until at least one visually relevant specimen exists.
2. Select visual seeds. Choose images that look like the requested commerce surface. A seed may be an organic screenshot, an old screenshot, a blog screenshot, an editorial reproduction, a first-party image, or a partial surface.
3. Reverse or similar-image discovery. When the tools allow, run reverse-image search, visual similarity, Google Lens, or an equivalent on promising seeds. Look for exact matches, similar screenshots, alternate crops, newer instances, posts with the same UI family, social posts with related screens, and adjacent transaction states.
4. Follow the neighborhood. Open promising results one by one. A seed Order Summary screenshot may lead to another cart, a Reddit checkout, a Facebook checkout, a different discount state, a newer mobile-web version, a purchase-history screen, or a checkout state with an element the seed lacked. Shared UI family does not make them duplicates.
5. Re-seed. If a new image is closer to the required surface, or newer or more organic, use it as the next seed.

Stop when an adequate reference family exists, further branches are mostly duplicates or irrelevant, or a real capture is demonstrably necessary. Do not loop forever.

If reverse-image or similarity search cannot be run, report VISUAL CHAINING UNAVAILABLE. Do not imply the visual neighborhood was exhausted. Do not claim Google Lens, reverse-image search, Pinterest visual search, or any other visual-search system was used unless it actually was.

Score each seed separately:

- DISCOVERY VALUE: how useful it is for finding better images.
- EVIDENCE VALUE: how far it goes toward establishing the requested current UI.

An old screenshot can have high discovery value and low evidence value for the current UI. Never throw away a useful seed only because it cannot establish current UI.

### Adjacent surfaces

Record useful neighboring surfaces found during the hunt even when they are not the requested surface. Do not expand this run into researching all of them. Put them in DISCOVERED SURFACE INDEX, for example: "Target Order Summary, reference family discovered, available for a later acquisition." The point is reusable visual knowledge, not a wider task.

### Duplicate lineages

Do not count reposts of the same underlying screenshot as independent evidence. Group obvious duplicates into one reference lineage. A Pinterest pin of a 2020 blog screenshot is still a 2020 reference, not fresh Pinterest evidence. Date the lineage from the earliest known capture, not from the repost. Neighborhood finds that are different states or crops are not duplicates just because they share a UI family.

## Reference family

Do not treat acquisition as the hunt for one perfect screenshot. Build a reference family when several independent images together establish a commerce surface. For each family record:

- COMMON STRUCTURE
- VARIABLE STRUCTURE
- OBSERVED STATES
- OBSERVED DATE RANGE
- DEVICE / PLATFORM VARIANTS
- ORGANIC EXAMPLES
- FIRST-PARTY EXAMPLES
- UNKNOWN CURRENT ELEMENTS
- SOURCE LINEAGES

Recurring layout can be stated as common structure. Amounts, products, promotions, and some controls are state-specific and must not be generalized. Example of structure only: several independent Order Summary screens may show header, order summary, subtotal, discounts, fulfillment, estimated taxes, total, savings, and checkout. Those labels are not assumed for a surface that was not actually seen.

## Reference classification

Classify every useful result by age and source:

- CURRENT_FIRST_PARTY
- CURRENT_REAL_USER
- RECENT_REAL_USER
- OLDER_REAL_REFERENCE
- OFFICIAL_BUT_NONCURRENT
- ILLUSTRATIVE_ONLY
- UNVERIFIED

Record the date when known. Do not treat an old screenshot as current UI.

### Artifact type

Finding genuine UI somewhere inside an image is not sufficient. Also classify how the image itself was created or published:

- ORGANIC_USER_SCREENSHOT: an ordinary person's direct screenshot of their app or site.
- ORGANIC_USER_PHOTO: an ordinary photograph that contains the relevant physical or digital surface.
- FIRST_PARTY_RAW_UI: a direct official screenshot or current product document that shows UI without a marketing reconstruction.
- FIRST_PARTY_MARKETING: App Store imagery, ads, launch graphics, promotional renders.
- INSTRUCTIONAL_COMPOSITE: a tutorial, press, or help graphic that arranges screenshots with arrows, captions, illustrations, numbered steps, or backgrounds.
- EDITORIAL_REPRODUCTION: a news, blog, or article reproduction of a screen.
- MOCKUP_OR_RENDER: reconstructed or simulated UI.
- UNKNOWN.

Never describe FIRST_PARTY_MARKETING or INSTRUCTIONAL_COMPOSITE as equivalent to an organic app screenshot just because real interface pieces appear inside it.

### Separate dimensions

Record these separately. Do not collapse them into one confidence score.

- SOURCE AUTHORITY: how trustworthy the publisher is about what the surface is.
- PIXEL AUTHENTICITY: whether the pixels are a real capture rather than a redraw.
- ORGANIC CAPTURE VALUE: how useful it is for knowing what an ordinary phone would show.
- CURRENTNESS: how recent the underlying capture is, using the lineage date, not the repost date.
- DISCOVERY VALUE and EVIDENCE VALUE, as defined under visual chaining.

A polished corporate graphic can have high source authority and low organic capture value.

### Organic-pixel priority

When the downstream use needs what an ordinary person's phone would naturally show, prefer, in order:

1. recent organic user screenshot
2. recent organic user photo
3. current first-party raw UI
4. recent editorial reproduction of genuine UI
5. older organic or raw reference
6. instructional composite
7. first-party marketing
8. mockup or render

## Surface match

- EXACT: the required surface and state are visible.
- PARTIAL: the correct surface, but the required state or detail is missing.
- STRUCTURAL: teaches layout or components but cannot establish current pixels.
- WRONG: superficially related, not the requested surface.

## Pixel knowledge

For the strongest references, extract only what is visible: screen hierarchy, navigation and header, card shapes, typography hierarchy, spacing, button placement, labels, icons, imagery, state-specific elements, the bottom action area, and device framing when relevant.

Separate observed pixels from inference. Do not invent unreadable or missing UI.

### Reconstruction

Several references may be combined to understand structure. Never silently combine states from different years into a fictional current UI. Keep four buckets:

- OBSERVED CURRENT
- OBSERVED OLDER
- INFERRED STABLE: only a pattern that is actually repeated across dated references, labeled as inference.
- UNKNOWN

If current organic pixels cannot be established, the decision is REAL CAPTURE REQUIRED, but only after the stop condition below.

## Physical surfaces

For bags, packages, receipts, signs, labels, and products, use actual photographs. Record object, material, form, branding, common variation, what is actually visible, environment, and reference date. One photo is not a universal design. Apply the same artifact type, lineage, visual chaining, and dimensions. A photo of a bag can be a seed for similar photos.

## Creative-surface fitness

NATURAL CAMERA-ROLL FITNESS: HIGH, MEDIUM, or LOW.

Would this reference teach how the surface would plausibly appear in the casual phone-evidence style the creative system uses? A corporate promotional composite is normally LOW even when the UI inside it is authentic. This score does not change whether the source is factually trustworthy.

## Acquisition decision

End with exactly one:

- REFERENCE SUFFICIENT
- REFERENCE SUFFICIENT FOR STRUCTURE ONLY
- REAL CAPTURE REQUIRED
- SURFACE UNAVAILABLE

REFERENCE SUFFICIENT requires current pixels that meet the organic-pixel priority, not a composite or an older screen treated as current. Structure-only describes what a reference family can teach. It does not upgrade an older or composite family into current UI.

REAL CAPTURE REQUIRED may be returned only after all of these:

1. direct textual search
2. behavioral and indirect search
3. image search
4. at least one visual-seed or similarity branch, when a viable seed exists
5. inspection of promising neighboring results

If similarity search cannot be run, say VISUAL CHAINING UNAVAILABLE in the same report. That flag means the neighborhood was not exhausted. It is not a substitute for the decision, and it is not a claim that a visual-search product was used.

If real capture is required, say why research cannot substitute and give the minimum capture procedure. Do not manufacture pixels to avoid that decision.

## Evidence rule

A reference teaches appearance only to the extent actually visible. Someone else's screenshot does not prove our transaction. A staged screen does not prove an event. An old screenshot does not silently establish current UI. A help article does not establish pixel layout. Do not add rewards, discounts, transactions, balances, orders, conversations, or statuses that are not in the source.

## Output

- SURFACE REQUEST
- SEARCH INTENTS USED, including broad, surface, state, and behavioral queries
- SOURCES SEARCHED
- VISUAL SEEDS, each with discovery value and evidence value
- VISUAL CHAINING status: used, or VISUAL CHAINING UNAVAILABLE, naming only systems that were actually used
- REFERENCE FAMILY
- REFERENCE CANDIDATES, each with artifact type, lineage, and the separate dimensions
- BEST REFERENCE
- REFERENCE CLASS
- ARTIFACT TYPE
- SURFACE MATCH
- OBSERVED PIXELS, split into OBSERVED CURRENT, OBSERVED OLDER, INFERRED STABLE, and UNKNOWN
- UNKNOWN PIXELS
- FRESHNESS, by lineage date
- SOURCE AUTHORITY
- PIXEL AUTHENTICITY
- ORGANIC CAPTURE VALUE
- CURRENTNESS
- NATURAL CAMERA-ROLL FITNESS
- DISCOVERED SURFACE INDEX
- CLAIM BOUNDARY
- ACQUISITION DECISION
- CAPTURE INSTRUCTIONS if required
