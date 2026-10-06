# v0.3 context fidelity

## Problem

A context bundle could be reproduced, but it was not a provider-ready packet. It stored StoryLock version metadata without the document, rendered mostly policies and skills, mapped stages to the wrong skills, and treated every non-invariant as optional. Compiling context required a Creative. There was no frozen task. Approved Account DNA observations and Creative Genome facets could change in place.

## What stayed

StoryLock versioning, approval boundaries, selective staleness, source snapshots, policy scoping, post attribution, comment membership, Account DNA current-pointer semantics, Creative Genome lock binding, provenance, the regression framework, and the provider abstraction are unchanged. Tags `v0.1.0-preservation-baseline`, `v0.2.0-core-integrity`, and `v0.2.1-trust-context` stay where they are. Live provider execution still returns `NOT_IMPLEMENTED`.

## New behavior

`CreativeTask` is the frozen request: scope, stage, instruction, constraints, and input refs. Compiling a `ContextBundle` consumes the task. A later edit creates a new task. The bundle stores `creative_task_id` and the exact instruction inside the hashed payload.

`ContextScope` is program, optional account, campaign, creative, and ecosystem. Policy resolution uses that scope. A creative still builds a scope from its own ids. Order remains global, program, account, campaign, creative. Active approved global invariants stay non-overridable.

When a current approved StoryLock exists, the bundle stores the canonical document JSON and the canonical Markdown. The provider text prints that document. Creative truth does not depend on the section D policy note.

Token budget never drops the task instruction, global invariants, `LOCKED_VALUE` rules, the current StoryLock, required stage skills, or rules whose title is an approval, proof, or rights rule. Optional rules sort by scope specificity, kind, stage relevance, then code. A budget of zero drops optional heuristics and still keeps locks.

The stage registry names required, supporting, and optional specialist skills. Supporting versions are included when the registry asks for them. Legacy versions stay out. `PERFORMANCE_INTERPRETATION` records `MISSING_DEDICATED_SKILL` and does not borrow another skill. Required skill dependencies are audited as included or intentionally omitted.

Account DNA context includes profile identity plus each observation's evidence kind, confidence, sample size, dates, source, and notes. Genome facets include dimension, value, assignment, confidence, and source, plus the genome's lock binding. An approved profile or genome cannot gain, change, or lose children in place. A new version is required. If the current genome is not bound to the current lock, context reports `GENOME_PENDING_FOR_CURRENT_LOCK`.

Benchmarks include the stored lesson and known metrics, with a deterministic reason. Holdout rows stay out of generation context. The Target audit still receives its own StoryLock because that creative is the subject.

`ConceptCandidate` is a proposal. A model may create `PROPOSED` concepts. Selection is a human `ApprovalEvent`. `Creative.selected_concept_id` records the concept that led to the creative and is not replaced after a StoryLock exists.

`ProviderPacket` is provider-neutral Markdown and JSON. Output contracts exist for `CONCEPT_GENERATION` and `STORY_DEVELOPMENT_AUDIT`. Each packet reports characters and a character-based token estimate per section.

## Stage map

| Stage | Required | Supporting or specialist |
| --- | --- | --- |
| RESEARCH | story-conflict-scout, object-culture-scout, live-heat-scout | source-card, commerce-world-mapper |
| CONCEPT_GENERATION | synthetic-story-generator, commercial-aware-synthesis, adaptation-blitz-match | none |
| STORY_DEVELOPMENT | story-development | chat-story-slideshow only when the task names it |
| PRODUCTION_ROUTING | production-spec-qa, visual-surface-acquisition, find-purchase-screens-on-pinterest | none |
| PRODUCTION_QA | production-spec-qa, ios-26-production-normalization | none |
| PERFORMANCE_INTERPRETATION | none (`MISSING_DEDICATED_SKILL`) | none |

## Export

```bash
creative-os export-context-bundle <bundle_id> --format markdown
creative-os export-context-bundle <bundle_id> --format json
```

`GET /api/context-bundles/{bundle_id}/packet?format=markdown` returns the same text. The manual evaluation files live in `evaluation/model_transfer_v1/`. `REVIEWER_RUBRIC.md` is for the human reviewer and is not part of a packet.

## Migration

`f7b2d4e81a90` revises `e1f6a2c39d55`. It adds `creative_tasks`, `concept_candidates`, `context_bundles.creative_task_id`, nullable `context_bundles.creative_id`, and `creatives.selected_concept_id`.

## Remaining limitations

- No provider is called. Grok, ChatGPT, image generation, research, and posting stay disabled.
- `PERFORMANCE_INTERPRETATION` has no dedicated skill.
- Benchmark lessons are the stored metrics notes. Unknown metrics stay null.
- Token estimates are `characters // 4`.
- A zero budget still drops optional account and program preferences. Locks and invariants stay.
- The Target creative still has no account, so its audit packet has no Account DNA.
