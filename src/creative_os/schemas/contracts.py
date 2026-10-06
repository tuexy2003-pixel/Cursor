"""Output contracts for manual model-transfer. These do not call a provider."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class StoryDevelopmentAuditResult(BaseModel):
    """Diagnosis only. The model must not mutate the StoryLock."""

    overall_status: Literal["READY", "THIN", "NEEDS_CHANGES"]
    diagnosis: str
    hook_assessment: str
    propulsion_assessment: str
    viral_texture_assessment: str
    continuity_assessment: str
    comment_door_assessment: str
    commerce_integration_assessment: str
    proof_boundary_assessment: str
    recommended_changes: list[str] = Field(default_factory=list)
    recommended_patches: list[dict[str, Any]] = Field(default_factory=list)
    things_to_preserve: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)


class ConceptDraft(BaseModel):
    title: str
    family: str | None = None
    premise: str | None = None
    human_event: str | None = None
    hook_direction: str | None = None
    stakes: str | None = None
    action_trigger: str | None = None
    expected_consequence: str | None = None
    reveal: str | None = None
    payoff: str | None = None
    commerce_relation: str | None = None
    proof_surface_direction: str | None = None
    primary_comment_door: str | None = None
    secondary_comment_doors: list[str] = Field(default_factory=list)
    viral_texture_opportunities: list[str] = Field(default_factory=list)
    why_it_fits_account: str | None = None
    risks: list[str] = Field(default_factory=list)
    research_needed: list[str] = Field(default_factory=list)


class ConceptGenerationResult(BaseModel):
    concepts: list[ConceptDraft]
