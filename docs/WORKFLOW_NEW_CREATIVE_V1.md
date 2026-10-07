# NEW_CREATIVE_V1

`NEW_CREATIVE_V1` is the only workflow definition published in v0.4. The node list is stored on `WorkflowDefinitionVersion` and hashed. Runtime code executes that list. It does not invent nodes.

## Nodes

1. `CREATE_CREATIVE_TASK` creates a `CreativeTask` at `CONCEPT_GENERATION`.
2. `COMPILE_CONTEXT` freezes a `ContextBundle`.
3. `SPECIALIST_REASONING` assigns `CREATIVE_DIRECTOR` on `MANUAL_SUBSCRIPTION` and waits.
4. `IMPORT_SPECIALIST_RESULT` accepts only a valid `ConceptGenerationResult`.
5. `DIVERSITY_CHECK` records the existing concept-batch diversity audit.
6. `HUMAN_CONCEPT_SELECTION` waits for the operator to select one proposed concept.
7. `STORY_DEVELOPMENT` creates the story task from that selected concept.
8. `COMPILE_CONTEXT` freezes the story bundle.
9. `SPECIALIST_REASONING` assigns `CREATIVE_DIRECTOR` again and waits.
10. `IMPORT_SPECIALIST_RESULT` stores a `StoryDevelopmentAuditResult` as `MODEL_DIAGNOSIS`.
11. `STORY_QA` records the diagnosis and does not approve it.
12. `HUMAN_STORY_APPROVAL` binds the current pending story-lock version and calls `decide_story_lock_version` only after the operator approves.
13. `PRODUCTION_ROUTING` records the next check. It does not generate or post.
14. `REFERENCE_READINESS` compares the human-declared requirements on the work order with existing assets.

## Stop

The run ends as `READY_FOR_PRODUCTION` when every declared requirement has a matching asset, or `BLOCKED_MISSING_REFERENCE` with the exact missing ecosystem, surface, state, mode, product, role, and reason. Empty requirements are ready. The service does not add requirements the human did not declare.

Production, production QA, post approval, external execution, and verification exist in the node catalog so later definitions can name them. This workflow does not use them, and their executors stay disabled.

## Waiting states

A manual specialist step uses `WAITING_EXTERNAL_RESPONSE`. The work order shows `WAITING_SPECIALIST`. An approval step uses `WAITING_HUMAN`. Later steps stay `PENDING` until every earlier step is `SUCCEEDED`. `resume_step` rejects a skip.
