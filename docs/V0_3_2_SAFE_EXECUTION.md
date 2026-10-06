# v0.3.2 safe execution gate

v0.3.1 creative selection stays in place. This pass adds the operational gate around paid text reasoning. It does not enable research, image generation, image editing, posting, or purchasing.

## A key is not permission

`available()` is true when a provider API key is present. That state is `CONFIGURED`. Live calls stay off unless `COS_LIVE_TEXT_REASONING_ENABLED=true`. The default is false.

Readiness values:

- `NOT_IMPLEMENTED`: the adapter or capability does not exist
- `NOT_CONFIGURED`: the key or the explicit model is missing
- `EXECUTION_DISABLED`: the adapter exists, but the operator has turned live calls off
- `AUTHORIZATION_REQUIRED`: live execution is enabled and no valid human authorization matches
- `READY`: configured and enabled, waiting for a valid authorization
- `CONTEXT_TOO_LARGE`: the frozen bundle exceeds the input ceiling
- `DAILY_LIMIT_REACHED`: today's network-attempt count has reached the local limit

Deleting an API key is not required to pause spending.

## Human authorization

`RunAuthorization` is created only by the local operator identity (`COS_OPERATOR_IDENTITY`, default `operator`). A provider response cannot create or approve one. The record binds the context bundle id, the context bundle hash, the provider, the explicit model, and the stage. A newly compiled bundle needs a new authorization.

Default limits for this phase: `max_attempts=1`, at most 2 named providers, and the configured output-token ceiling. Optional `max_cost` is stored only as a ceiling note. The app does not invent a price.

## One network attempt

Before the HTTP call, the app claims a `ProviderInvocation` with an idempotency key and commits that claim. The same key returns the existing run and does not call the provider again.

Same-response fenced JSON parsing is response salvage. It is not a second network call. A timeout after the request is sent becomes `UNKNOWN_PROVIDER_OUTCOME` and is not retried. A second network attempt needs a new human authorization, and the daily limit still applies.

`COS_TEXT_REASONING_DAILY_RUN_LIMIT` defaults to 10. It counts provider network attempts. Model code cannot change it.

## Explicit model

Paid execution reads `COS_XAI_MODEL` or `COS_OPENAI_MODEL`. There is no fallback model name. The chosen model is frozen onto the authorization and the model run. If the provider returns a different model, the run is `PROVIDER_ERROR` and no concept or audit record is stored.

If the provider returns a request id, it is stored. If it returns a numeric cost, that cost is stored. Otherwise cost is `UNKNOWN`. Token counts are not converted into money.

## Diversity and identity

The phrase detector labels its assignment `DETERMINISTIC_INFERRED`. Diversity levels are a `DETERMINISTIC_HEURISTIC` with coverage `known_count / total_count`. A high label is not a proof of creative diversity, and it is withheld when unknown skeletons are at least as common as known ones. The account-identity check stays advisory.

Historical manual evaluation files are not rewritten. Current structured fingerprint rows are relabeled by migration `c5a1e8d42f06` when the source is `deterministic skeleton phrases`.

## First smoke test

`creative-os prepare-smoke-tests` freezes two tasks and does not execute them:

1. Maria, DoorDash, concept generation, exactly 2 concepts
2. Optional later: story-development audit of the current Target creative, diagnosis only

The operator confirms provider, model, stage, task, bundle id, hash, size, max attempts, max output tokens, daily count, and unknown cost status, then chooses `AUTHORIZE & RUN ONCE`.

The compiler packet field `provider_execution` remains `NOT_IMPLEMENTED`. The compiler still does not call a provider.
