# GOLDEN REGRESSION TESTS (machine version: GOLDEN_REGRESSION_TESTS.json)

## T01 s1_presentation
- INPUT: 3 short bubbles; peek template leaves >40% empty card
- EXPECTED: choose cropped thread / lock screen / preview card or thread+hook; not peek
- PASS: no large dead space; no padded fake dialogue
- FAIL: peek chosen with dead space; invented filler bubbles
- RULE: production-spec-qa hook-presentation router

## T02 propulsion
- INPUT: S1 'don't look at the order' then S2 order screen immediately
- EXPECTED: flag missing action trigger; add smallest causal beat (e.g. 'bc you're nosy' / 'ok now i'm looking')
- PASS: trigger+action present before proof
- FAIL: proof shown without motivated action
- RULE: story-development Pass 1

## T03a micro_detail_firewall
- INPUT: weak basket; propose AirPods to raise subtotal
- EXPECTED: reject AirPods
- PASS: no headroom-only item
- FAIL: expensive item added for discount
- RULE: story-development discount-headroom firewall

## T03b micro_detail_firewall
- INPUT: birthday gift story; AirPods are the hidden gift
- EXPECTED: approve AirPods
- PASS: item independently story-motivated
- FAIL: rejected despite motivation
- RULE: story-development

## T04 continuity
- INPUT: hook 'birthday tomorrow' then same-day lit cake, no time transition
- EXPECTED: fail; change hook to today or add transition
- PASS: state-transition consistent
- FAIL: impossible timeline passes
- RULE: story-development Pass 3

## T05 stale_reference_date
- INPUT: Target base shows 'Pick up by Wed, Oct 23'; ledger says Oct 7
- EXPECTED: render Oct 7
- PASS: visible date = ledger
- FAIL: reference date retained
- RULE: Pass 3 + production-spec-qa Reference Is Law carve-out

## T06 current_lock_precedence
- INPUT: old asset/memory says AirPods 4; approved lock says AirPods 5
- EXPECTED: use AirPods 5; mark old assets STALE
- PASS: AirPods 5 used; stale listed
- FAIL: AirPods 4 used; old files deleted/rewritten
- RULE: story-development current-lock precedence

## T07 ui_fit
- INPUT: 5 products don't fit native Target base
- EXPECTED: choose another real base or natural scroll state
- PASS: native row heights preserved
- FAIL: rows shrunk/squeezed
- RULE: production-spec-qa

## T08 reference_is_law
- INPUT: suitable Target base exists
- EXPECTED: localized edit of base
- PASS: base pixels retained
- FAIL: freehand full UI reconstruction
- RULE: production-spec-qa router

## T09 camera_roll_routing
- INPUT: real-life payoff slide needed
- EXPECTED: visual search first, then edit/reference-guided scene
- PASS: search performed and logged before generation
- FAIL: generated from text first
- RULE: production-spec-qa Type C

## T10 proof_boundary
- INPUT: order screen used as proof
- EXPECTED: claims limited to visible facts
- PASS: no invented intent/location/payment causality
- FAIL: slide implies facts the screen doesn't show
- RULE: story-development / production-spec-qa

## T11 comment_surface_overreach
- INPUT: micro-detail becomes hero product or ad
- EXPECTED: fail
- PASS: details secondary and native
- FAIL: detail dominates or reads like ad
- RULE: story-development Pass 2

## T12 overlay_redundancy
- INPUT: bubble 'don't look at the order'; overlay 'why did she tell me not to look'
- EXPECTED: rate weaker than overlay adding new context (e.g. 'my birthday is literally today 😭')
- PASS: overlay adds new fact
- FAIL: paraphrase overlay rated best
- RULE: production-spec-qa S1 hook gate

## T13 product_generation
- INPUT: lock wants AirPods 4 at $129.99 from cached snippet
- EXPECTED: verify live retailer; use current generation
- PASS: live check recorded
- FAIL: cached/stale product
- RULE: memory rule (2026-10-05)

## T14 aspect_ratio
- INPUT: final asset 1080x1920
- EXPECTED: fail; require 9:19.6
- PASS: ratio ≈ 0.4602 (e.g. 1206x2622)
- FAIL: 9:16 output
- RULE: production-spec-qa default output

## T15 dialogue_naturalness
- INPUT: bubble 'doing a quick Drive Up'
- EXPECTED: fail; rewrite to how a person texts
- PASS: no retailer-term exposition
- FAIL: commerce-first dialogue passes
- RULE: story-development / taste

## T16 math
- INPUT: subtotal 142.97, discount -125.00, tax 1.26
- EXPECTED: total 19.23
- PASS: arithmetic exact
- FAIL: mismatch
- RULE: deterministic

## T17 weekday
- INPUT: story date Mon Oct 5 2026; pickup 'Wed, Oct 7'
- EXPECTED: weekday matches calendar
- PASS: Oct 7 2026 is Wednesday
- FAIL: weekday mismatch
- RULE: Pass 3 deterministic

## T18 recursive_edit
- INPUT: need a second fix on an edited output
- EXPECTED: re-edit from original base
- PASS: edit source = original base
- FAIL: edit chained on degraded output
- RULE: production rule
