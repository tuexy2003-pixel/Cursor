# v0.3.1 creative selection

This pass keeps the v0.3 context compiler. It adds batch diversity, account identity anchors, a human-approved product-identifier correction, and a read-only text reasoning path.

Tags `v0.1.0-preservation-baseline`, `v0.2.0-core-integrity`, `v0.2.1-trust-context`, and `v0.3.0-context-fidelity` stay where they are.

## What changed

- Manual model-transfer outputs live in `manual_evaluations` with origin `EXTERNAL_MANUAL_EVALUATION`. They are not `ModelRun` rows.
- A concept-generation run can create a `ConceptBatch`. Diversity is measured after the concepts exist.
- Each candidate can carry a partial mechanism fingerprint. Missing dimensions stay absent.
- Account DNA observations shaped like `Dre as boyfriend` compile into identity anchors. Generic relationship wording is not scored as a contradiction.
- The Target AirPods 5 row no longer keeps TCIN `85978615` after `creative-os apply-baseline` or `creative-os seed`. The replacement id is left unknown.
- `GrokReasoningProvider` and `OpenAIReasoningProvider` can read a frozen bundle for `CONCEPT_GENERATION` and `STORY_DEVELOPMENT_AUDIT` when an environment key is present. Without a key the run is `NOT_IMPLEMENTED`.
- Successful concept output is `PROPOSED`. A story audit is `MODEL_DIAGNOSIS` and does not move the approved StoryLock.
- The operator page at `/runs` compares providers against one bundle. `evaluation/model_transfer_v1/REVIEWER_RUBRIC.md` stays out of provider packets.
- Markdown and JSON packet export remain.

## Still disabled

Web research, Pinterest, visual search, image editing, image generation, and posting.

## Known gaps

Live calls need `COS_XAI_API_KEY` or `COS_OPENAI_API_KEY`. This environment has neither, so text provider execution is partial. Cost stays unknown unless a provider returns it. The diversity repair plan does not rank concept quality and does not generate replacements.
