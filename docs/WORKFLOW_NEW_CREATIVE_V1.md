# NEW_CREATIVE_V1

`NEW_CREATIVE_V1` is the only workflow definition published in v0.4.1. The node list is stored on `WorkflowDefinitionVersion` and hashed. When the published hash differs from the code, Creative OS inserts a new immutable version. It does not rewrite the previous one. Runtime code executes the stored list. It does not invent nodes.

## Nodes

1. `CREATE_CREATIVE_TASK` creates a `CreativeTask` at `CONCEPT_GENERATION`.
2. `COMPILE_CONTEXT` freezes a concept `ContextBundle`.
3. `SPECIALIST_REASONING` assigns `CREATIVE_DIRECTOR` on `MANUAL_SUBSCRIPTION` and waits.
4. `IMPORT_SPECIALIST_RESULT` accepts only a valid `ConceptGenerationResult`.
5. `DIVERSITY_CHECK` records the existing concept-batch diversity audit.
6. `HUMAN_CONCEPT_SELECTION` waits for the operator to select one proposed concept.
7. `STORY_DEVELOPMENT` creates a `STORY_DEVELOPMENT_DRAFT` task from that selected concept. A work order with no creative gets a new Creative here. The first StoryLock can be version 1.
8. `COMPILE_CONTEXT` freezes the draft bundle. The output contract is `StoryLockDraftResult`.
9. `SPECIALIST_REASONING` assigns `CREATIVE_DIRECTOR` again and waits.
10. `IMPORT_SPECIALIST_RESULT` validates `StoryLockDraftResult` and creates a `PENDING` `StoryLockVersion`. It does not move `current_approved_story_lock_version_id`.
11. `CREATE_CREATIVE_TASK` creates a `STORY_DEVELOPMENT_AUDIT` task whose input is that pending candidate.
12. `COMPILE_CONTEXT` freezes the audit bundle.
13. `SPECIALIST_REASONING` assigns `CREATIVE_QA` and waits.
14. `IMPORT_SPECIALIST_RESULT` stores a `StoryDevelopmentAuditResult` as `MODEL_DIAGNOSIS`. QA cannot approve the lock.
15. `STORY_QA` records the diagnosis.
16. `HUMAN_STORY_APPROVAL` shows the pending version, diff, QA result, uncertainties, research-needed flags, and provenance. `APPROVE` calls `decide_story_lock_version`. `NEEDS_CHANGES` marks that version and inserts a new draft cycle. The prior draft is not edited.
17. `PRODUCTION_ROUTING` runs only after the human approval set `story_lock_approved`. It does not generate or post.
18. `REFERENCE_READINESS` compares human-declared requirements with existing assets.

`READY_FOR_PRODUCTION` requires the concept selection, the StoryLock draft, QA, human StoryLock approval, production routing, and reference readiness.

## Stop

The run ends as `READY_FOR_PRODUCTION` when every declared requirement has a matching asset, or `BLOCKED_MISSING_REFERENCE` with the exact missing ecosystem, surface, state, mode, product, role, and reason.

An empty requirement list is `REFERENCE_REQUIREMENTS_NOT_GENERATED`, not `READY`. Production routing does not yet generate those requirements. That is a v0.5 production-routing gap. The service does not invent requirements, and it does not treat "none declared" as ready.

Production, production QA, post approval, external execution, and verification exist in the node catalog so later definitions can name them. This workflow does not use them, and their executors stay disabled.

## Waiting states

A manual specialist step uses `WAITING_EXTERNAL_RESPONSE`. The work order shows `WAITING_SPECIALIST`. An approval step uses `WAITING_HUMAN`. Later steps stay `PENDING` until every earlier step is `SUCCEEDED`. `resume_step` rejects a skip.

## Changes requested

`NEEDS_CHANGES` does not mutate the pending draft. The workflow appends a new story-development assignment that receives the current pending draft, the QA feedback, and the human notes. The next valid specialist response creates a new pending StoryLock version. There is no automatic retry.
