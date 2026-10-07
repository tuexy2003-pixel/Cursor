# Company control plane

Creative OS remains the system of record. The control plane is a thin, inspectable orchestration layer in front of it.

## Boundaries

| Role | Responsibility |
| --- | --- |
| Creative OS | Owns tasks, context bundles, concepts, story locks, assets, approvals, and model-run records. |
| Workflow graph | Chooses the next allowed step from a published definition. |
| Specialists | Return proposals and evidence. They do not own state and cannot approve. |
| Human operator | Makes irreversible approvals and action authorizations. |
| OpenClaw | Future executive client. It is not installed or imported. |
| GeeLark | Future operations adapter. No credentials, phone control, or workflow execution exist here. |

## Records

- `WorkOrder` is a human business goal. It references `CreativeTask` rows; it does not copy them.
- `WorkflowDefinition` plus `WorkflowDefinitionVersion` store an explicit node list. A published version is immutable. A model cannot submit a new graph at runtime.
- `WorkflowRun` and `StepRun` record each node, its inputs, outputs, attempts, errors, and evidence references.
- `Specialist` is a provider-neutral registry. `authoritative` is false.
- `SpecialistAssignment` binds one step to a role and a transport.
- `EvidenceRecord` points at an existing object and hash. It does not duplicate the object.
- `ApprovalRequest` binds an approval type to a subject id and hash.
- `ActionAuthorization` freezes an action type, payload hash, limits, authorizer, and expiry.
- `ExternalExecution` and `VerificationResult` stay separate. Reported completion does not create a verification.

## Manual subscription

The operator exports a frozen context bundle, runs it in Grok or ChatGPT, and pastes the raw JSON back. Creative OS validates it with the existing Pydantic contracts and stores it through the same concept-batch and story-audit path used by text reasoning.

The assignment records `transport = MANUAL_SUBSCRIPTION`, the declared provider and model, `api_verified = false`, the bundle id and hash, the raw and parsed response, and the validation status. No socket is opened. Concept rows stay `PROPOSED`. Story audits stay `MODEL_DIAGNOSIS`. No approval pointer moves.

## What stays disabled

Posting, research execution, image generation, cloud-phone control, GeeLark, purchasing, and direct StoryLock or Account DNA mutation are not exposed by this layer. `MODEL_RUN` remains delegated to the existing text-reasoning gate. `POST_CONTENT`, `RUN_GEELARK_WORKFLOW`, and `START_DEVICE` can be named on an authorization and still cannot execute.
