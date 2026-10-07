---
name: Source card
description: >-
  Use when turning a short-form post, link, or screenshot into a labeled
  discovery source card before any adaptation. Every frame records narrative
  role, surface type, and information-state change.
---
# Source card

## When to use
Any time a source enters the pipeline. Produce one source card before adaptation.

## Rules
- Record published_at, first_seen_at, and captured_at. Label source_type: user_provided_fyp, public_search, browser, or other.
- Do not bypass platform access controls. Do not invent metrics or dates.
- Teaching examples are not templates. Do not copy another creator's face, handle, wording, or screenshots.
- Every frame has three separate fields. Do not collapse them.
  - narrative_role: setup, misunderstanding, contradiction, escalation, evidence, confession, payoff, or another role the story actually uses.
  - surface_type: tiktok_text, snapchat_bar, imessage, app_screenshot, lockscreen_notification, notes, search_screen, meme_reaction, raw_camera, selfie, physical_payoff, selfie_status_widget, overlay_on_proof, or other_native_surface.
  - information_state_change: what the viewer knows, suspects, or wants answered after this frame that they did not before.
- A repeated surface is valid. A new surface with no information-state change is not.
- Golden Lane A / FYP examples must store surface_sequence and narrative_pattern so both are searchable.

## Output
frames_slides[] entries include index, asset_ref, narrative_role, surface_type, text_placement (native_overlay, inside_screenshot, both, none), information_state_change, visible_text, and new_information.
Also store surface_sequence as an arrow string and narrative_pattern as the ordered roles.

## Steps
1. Save the media and the URL or post id when they exist.
2. Fill the three fields on every frame, in reveal order.
3. Write surface_sequence and narrative_pattern from those frames.
4. Hand the card on. Do not propose an offer or generate a creative here.
