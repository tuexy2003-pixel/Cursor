# v0.3.2 safe live smoke tests

These tasks are prepared and frozen. Nothing in this directory, and nothing in `prepare-smoke-tests`, calls a provider.

## First smoke test

- Account: Maria
- Ecosystem: DoorDash
- Stage: `CONCEPT_GENERATION`
- Ask: exactly 2 concepts
- Purpose: prove transport, frozen context, structured output, and local usage accounting
- This is not a quality benchmark
- Expected future result, after a human authorizes one attempt: 2 `PROPOSED` concept candidates
- Do not modify Maria Account DNA from the result
- Do not select a concept
- Do not research

Instruction frozen into the task:

> Propose exactly 2 concepts for Maria in the DoorDash food-and-couples lane. This is a transport smoke test, not a quality benchmark. Do not research. Do not select a winner. Leave unknown fields null.

## Optional second smoke test

Run this only after a human has reviewed the concept-generation result.

- Creative: current Target creative `chore-stuff-target`
- Stage: `STORY_DEVELOPMENT_AUDIT`
- One provider, one attempt, one frozen context bundle
- Diagnosis only. The story lock must not move

## Prepare, do not execute

```bash
creative-os prepare-smoke-tests
```

The command prints the local task and context-bundle ids. It creates no `RunAuthorization` and no `ModelRun`.

The first live call is one provider only. Provider comparison stays capped at 2 and is not this smoke test.

For that first real provider call, set `COS_TEXT_REASONING_DAILY_RUN_LIMIT=1` in the local environment. The application default stays 10. After the single run is reviewed, raise the limit by editing the environment. Do not change it from model output.

Provider values in `.env` are read through application settings. `COS_XAI_API_KEY` and `COS_XAI_MODEL`, or the OpenAI pair, may be process environment variables or entries in `.env`. A process variable overrides the file. `XAI_API_KEY` and `OPENAI_API_KEY` apply only when the matching `COS_*` key is absent. The model always comes from `COS_XAI_MODEL` or `COS_OPENAI_MODEL`.
