---
name: Production spec QA
description: >-
  Use after a storyboard is approved. Run the production router (base first,
  smallest edit) before every asset and the first-slide hook gate before any S1,
  run organic visual reference discovery, route each region to a production
  method, then QA. Does not require checkout, payment, or a chat opening.
---
# Production spec + QA

## When to use
Only after the storyboard is approved. Do not change the storyboard because a useful photo was found. Do not produce images until that approval.

## Production router — run before every asset

REFERENCE IS LAW.

Reference Is Law governs native visual structure and UI behavior. Story-specific clock, date, weekday, order-state and other continuity values come from the current approved STORY_LOCK.

Before creating any visual, ask: "What existing real or reference asset is the BASE, and what is the smallest edit required?"

Classify every asset first as exactly one of:

- A. SHORT MESSAGE / CHAT
- B. APP / COMMERCE / UI SCREEN
- C. REAL-LIFE / CAMERA-ROLL PHOTO
- D. TRUE NEW SCENE

Do not begin production until the type and base are chosen.

### A. Short message / chat
SHORT MESSAGE CONTENT MUST PASS A HOOK-PRESENTATION ROUTER. Do not automatically choose a peek. Choose the native message presentation that produces the strongest hook with the least useless space.

Native presentations include:

- A. Peek / context preview (template: `/workspace/creative-pipeline/shared/templates/ios-messages-peek/`)
- B. Tightly cropped full message thread
- C. Lock-screen notifications
- D. Message preview / banner card
- E. Message surface + native TikTok floating hook text
- F. Another approved phone-native message presentation

Choose based on message count, message length, hook density, importance of contact identity, importance of timestamps, need for surrounding thread history, available visual space, dead-space risk, and whether a floating hook improves stopping power.

Peek density test: a peek is valid only when the story-relevant messages fill enough of the preview card that the composition feels intentional. If the peek produces a large meaningless empty panel, FAIL THE ROUTE and choose another native presentation. Never add fake dialogue to fill a peek. Never stretch the peek card larger than the conversation naturally requires.

### B. App / commerce / UI screen
Retailer and app UI defaults to APPROVED BASE SCREEN → LOCALIZED CHATGPT IMAGE EDIT. Do not default to reconstruction.

1. Find the closest approved reference screen.
2. Declare that image the BASE.
3. Gather INGREDIENT images: products, thumbnails, photos, logos.
4. Pass BASE + INGREDIENTS to ChatGPT image editing.
5. Tell ChatGPT to preserve the base and modify only named fields.

Editable fields, when the approved storyboard requires them: item title, thumbnail, date, time, quantity, price, discount row, tax, total, status wording.

Preserve unless explicitly authorized: layout, icons, logos, spacing, card geometry, navigation, status chrome, background, native visual texture.

If the base does not physically support the desired content, find another approved base or another natural scroll state. NEVER compress, redesign, or create a fake "super screen" to fit everything.

### UI source priority
1. User-provided exact reference
2. Approved internal reference bank
3. Another real screenshot acquired through research
4. Close real screenshot + localized edit
5. Deterministic reconstruction
6. Full image generation

Never use a lower tier while a suitable higher-tier asset exists. Tier 5 reconstruction of retailer UI requires human approval. Tier 6 full generation of retailer UI is prohibited unless explicitly authorized.

### C. Real-life / camera-roll photo
Before generating anything: SEARCH FIRST. Use the Find slide images on Pinterest workflow, plus visual search where useful.

Search for the desired COMPOSITION, not merely the topic. Bad: `birthday party`. Good: `teen home birthday kitchen casual iphone cake streamers candid vertical`.

Inspect multiple results. Open the closest candidate. Inspect the Pinterest similar images underneath it. Run visual search on the strongest candidate where useful. Shortlist 3–5.

Assign each shortlisted photo one role: BASE or VISUAL REFERENCE. The owner has loosened rights for found real photos: a suitable found photo may be used as the BASE → ChatGPT localized edit.

People in a found base:
- Incidental people (a sibling, mom, friend, stranger at the frame edge) may stay as they are.
- If the person in the photo is meant to be the account's avatar or persona, swap that person for the avatar using the persona's approved anchors. Keep the base's room, light, camera, and composition.

Do not blindly generate a scene before this acquisition step.

### Camera-roll edit rule
If a suitable base exists, KEEP THE REAL BASE. Use ChatGPT only for the smallest continuity edits: replace a product, add or remove an object, change a bag, change food, adjust one decoration, remove a distracting item, change one color.

Do not regenerate room, lighting, camera angle, background, person, or composition when the base already provides them.

### D. True new scene
Full generation is allowed only when no usable base exists, the scene is genuinely unique, or the user explicitly requests full generation. Before doing so, state why tiers 1–4 could not satisfy the task. A newly generated real-life scene should normally still be informed by visual-search references.

### Asset role definitions
- BASE: the pixels and composition to preserve.
- INGREDIENT: an object, product, or image inserted into the base.
- REFERENCE: visual guidance only.
- EVIDENCE: a source proving factual or UI behavior.

A reference is not automatically a base. An evidence screenshot is not automatically the production image.

### Pre-asset routing record
Before producing each asset, resolve:

- TYPE: A / B / C / D
- BASE: exact file or source
- INGREDIENTS: exact files, if any
- REFERENCE: exact files or sources, if any
- MUST STAY IDENTICAL: list
- MAY CHANGE: list
- FINAL ASPECT
- PRODUCTION TOOL / METHOD

Do not start until this record is resolved.

### Locked text and numbers in an edit
First attempt: ChatGPT image edit from the same untouched approved base. The prompt says: "Keep image 1 as the untouched base. Do not recreate the screen. Do not expand or outpaint. Change only [locked fields]. Keep every other pixel and layout element unchanged."

QA every edited word, number, bubble side, date, time, price, quantity, discount, tax, total, and status.

If anything is wrong, second attempt: re-edit from the ORIGINAL approved base. Never edit the already-drifted output.

If ChatGPT fails the exact locked text or numbers twice, a TEXT FIDELITY PATCH is allowed: localized deterministic replacement of only the failing text fields (exact dialogue, price, total, date, time, quantity, label). It may not rebuild layout, cards, icons, logos, spacing, background, navigation, or surface geometry.

### Post-edit QA
After every ChatGPT edit, compare against the ORIGINAL base and the locked spec. Fail if:

- locked text is misspelled
- a number differs
- price or math differs
- a bubble side differs
- the product is wrong
- layout outside the authorized edit area drifts
- a logo or icon changes unnecessarily
- UI is rebuilt when a usable base existed

On failure, return to the ORIGINAL base. Never recursively patch a degraded edited output.

## First-slide hook gate — run before any S1 asset
Slide 1 is not just another evidence slide. Its one job is to EARN THE NEXT SWIPE. The hook determines the surface; the template does not determine the hook. This gate sits inside the production router and does not replace it.

Ask before producing S1:

1. What is the single question, contradiction, desire, or judgment that earns swipe 2?
2. What information must the viewer understand immediately?
3. What information should still be withheld?
4. Does the selected surface visually prioritize that hook?
5. Is any large part of the frame communicating nothing?
6. Would someone in the intended life-world actually phrase the dialogue this way?
7. Is retailer or app terminology being inserted only because a later commerce screen uses that retailer?
8. Does the slide remain interesting before the commercial mechanic appears?
9. Does S1 keep the story-development lock's trigger and action, and does it still create the intended expected next beat?

If an answer exposes a weak hook, revise S1 before production.

Blur / dead-space test: "If I blur the dialogue or content, is most of the frame just empty interface?" If yes, the composition fails unless the empty area has a real story function. Fix it by changing the crop, scroll position, message presentation, notification presentation, overlay treatment, or native surface. Authenticity alone is not sufficient: a technically accurate UI with weak visual density is still a failed first slide.

Dialogue naturalness gate: when S1 includes dialogue, ask: would someone actually text this? Is a phrase present only to explain the plot to the viewer? Is retailer, app, or fulfillment language being forced into human speech? Is the message too formal? Is it trying too hard to sound young? Does the dialogue create a question without answering it? If not, rewrite it before asset production. Youthfulness comes from situation, relationship, stakes, objects, and phone behavior, not slang stuffing.

Retailer reveal rule: do not force Target, DoorDash, or fulfillment terminology into S1 dialogue because S2 uses that app. If the retailer is not needed to understand the hook, withhold it so the later commerce surface is an information gain. Weak: "doing a quick Drive Up". Better: "grabbing stuff for the house rn".

Floating hook overlay: a native TikTok-style floating text hook MAY be added to S1 on any underlying phone surface when it materially improves stopping power. It must open the loop, add POV, emotion, or contradiction, stay short, feel like native creator text, and never summarize the story. It adds context, stakes, or POV the artifact does not already contain (per story-development). Good: "my birthday is literally tomorrow 😭". Bad (restates the bubble): "why did she tell me not to look 😭". Bad (summarizes): "my sister secretly bought birthday supplies at Target and I found out by checking the order". The artifact supplies evidence; the overlay supplies framing. Do not make overlay and dialogue say the same thing unnecessarily. It must not cover the key content or look like part of the app UI.

S1 information rule: S1 establishes enough to create the question while withholding the answer, the full backstory, the retailer when unnecessary, the commercial mechanic, the discount, and the final payoff. Every later slide must have new information to reveal.

## Story-development mirror — verify only
Read the concept's story-development lock record (`STORY_LOCK.md` or equivalent) before routing. Carry each slide's approved micro-details into the pre-asset routing record. This section verifies; it never invents micro-details, beats, or comment doors. A needed change goes back to story-development.

## Continuity mirror — verify only
Check every rendered asset against the current approved STORY_LOCK continuity ledger. This section does not invent continuity; a needed change goes back to story-development. FAIL production if:
- a clock, date, or weekday contradicts STORY_LOCK
- Today / Yesterday is wrong
- a stale reference date survives over a ledger value
- order progression is impossible
- the wrong locked product or model appears
- a wrong quantity, color, or variant creates a visible contradiction
- a physical payoff item does not match the ordered item
- an object appears before it is acquired
- an actor knows something before discovering it
- a payoff happens before its prerequisite event
- a meaningful unmarked time jump causes confusion
- an asset uses a value from an older, superseded lock

## Organic visual reference discovery
Required after storyboard approval and before any human-photo production. Skip it when that slide has no human photograph to make. Do not search merely because a person is mentioned.

Search colloquially for how an ordinary person would have photographed that beat. Pinterest, Reddit, TikTok stills, and Google Images are in bounds. The queries come from the storyboard. There is no fixed query list.

Classify each useful find as one of:

- COMPOSITION REFERENCE. Camera, crop, body placement, pose, distance, gaze, framing, obstruction.
- PHOTOGRAPHIC-LANGUAGE REFERENCE. Flash, noise, exposure, tilt, accidental crop, low light, phone processing.
- SURFACE REFERENCE. How a Snapchat caption, TikTok text, notification, or screen sits on a photo.

A found person is never an identity reference. Keep the weirdness that makes the reference believable: forehead in frame, half a face, flash blowout, grain, tilt, mostly ceiling, tiny subject, bad crop, thumb, glare, or a physical screen instead of a clean screenshot. Do not clean it up.

When a find is used as a REFERENCE rather than a router-C BASE, transfer the camera, crop, pose logic, gaze, distance, flash, obstruction, and imperfection, and recreate the scene with the approved identity anchors and the story's clothes, room, objects, and action. Do not transfer the reference person's identity, distinctive details, account, or post. When a found photo is the BASE, follow router C: incidental people may stay; a person who must be the account avatar is swapped for the avatar.

A back-camera photo does not need a face. Authorship can be what was photographed, how, and what was written on it.

## Persona
Use a persona only when the storyboard asked for that continuity. Sometimes authorship is only photographic behavior.

Identity comes only from that persona's approved anchors. If a generated frame disagrees with Anchor 0, Anchor 0 wins. Condition references and composition references are not anchors. Do not promote them. A replacement wide candid, including Image 10, is composition only. The rejected Image 10 is never used.

Do not chain generations. Each new scene starts from Anchor 0, the relevant approved anchors, and an optional condition or composition reference. A generated output does not become identity unless it is explicitly approved.

Clothing, hair arrangement, makeup, jewelry, expression, pose, room, lighting, and crop are not identity. Do not repeat a cami or lace-trim top unless the storyboard asks for it. Use ordinary clothes: hoodie, crew neck, T-shirt, sweatshirt, jacket, pajamas.

Do not face-swap an arbitrary photo. The only allowed swap is router C: replacing the person in a chosen camera-roll BASE with the account avatar from approved anchors. Do not edit the persona's identity specification during production. Do not progressively beautify the face. Keep ordinary skin, asymmetry, and phone-photo flaws.

The person is doing the action, not demonstrating it. Identity outranks attractiveness.

## Asset roles
For every region, separately name BASE, INGREDIENT, REFERENCE, and EVIDENCE. The library is a starting set, not the limit. Search when the right file is missing. Never letterbox the wrong image, stretch a tiny screenshot, substitute desktop UI for a phone screen, or rewrite the storyboard around a file that happens to exist.

## Route per region
Do not send a whole slide through one method. The production router above decides the default.

- Untouched real pixels, when the file is already the thing.
- Base-screen localized edit is the default for retailer/app UI. Deterministic construction is router tier 5 and requires human approval when an appropriate real/reference base exists. Exact text/number patching may use localized deterministic replacement only after two failed base-preserving image-edit attempts.
- Deterministic compositing, to place a real ingredient or a finished screen into a real frame. On a phone in a hand, keep the hand, phone, and room, and replace only the glass.
- Localized image edit, when a real base is close and one photographic region must change.
- New photographic generation, only under router D, from approved identity anchors plus the organic composition reference and the story's objects.

Reject an edit that changes the product, the logo, the retailer, the person's identity, or geometry that must stay exact. Return to the original base and re-edit; use the text fidelity patch only under the router fallback rule.

Retailer UI, prices, and totals are never freely generated. They change only through a base-preserving localized edit or the text fidelity patch. A social caption inside the artifact is added only when the storyboard said the artifact was a Snapchat, a TikTok, or a story. A native TikTok floating hook on S1 follows the first-slide hook gate instead.

There is no required checkout, payment screen, or chat opening. Do not add one because a carousel often has one.

## QA
Fail the frame if:

- a swipe adds nothing
- the organic reference is casual, candid, or flash-blown and the result is polished, staged, or influencer-like
- the face drifts from the anchors, or the persona is beautified across frames
- body proportions become implausible, or hands and anatomy fail
- anchor clothing is treated as identity, or a cami returns without a story reason
- a reference face, outfit, or personal detail leaked in when the find was only a reference
- the action, environment, or objects are wrong, or a candid became a pose
- a low-light scene became a professional portrait
- the product or retailer identity changed unintentionally
- UI was rebuilt or materially redrawn despite a suitable approved base, or pixels outside authorized edit fields drift. Localized exact-text replacement is allowed only under the router fallback rule.
- a short chat presentation leaves large meaningless empty space, whichever surface was chosen
- S1: most of the composition is meaningless empty UI
- S1: the message presentation was chosen only because of a template rule
- S1: dialogue contains retailer terminology solely to support downstream commerce
- S1: dialogue sounds like exposition rather than a real message
- S1: the floating hook summarizes the story instead of opening it
- S1: the first slide reveals information better saved for later
- S1: there is no clear reason to swipe
- propulsion broke: a dialogue, crop, or edit dropped the locked trigger or action decision, or a later slide no longer follows from an action someone took
- an approved micro-detail is missing or illegible without an approved change
- production added a detail that is not in the lock record
- a micro-detail visually overtakes the slide's primary story beat, or reads as an ad / hero product placement
- a camera-roll photo was generated without the search-first acquisition step
- the offer appears where the storyboard did not already need a surface
- the offer is stated as a real retailer discount or a completed transaction it is not
- a checkout, payment screen, or chat was added that the story did not need

Separate verified retailer facts, verified offer facts, staged story, inference, and unknown. Do not turn one into another.

Default final mobile creative output is 9:19.6 portrait (for example 1206×2622) unless the approved creative explicitly specifies another aspect ratio. Return finished files only when production was requested. A spec lock is not a render.
