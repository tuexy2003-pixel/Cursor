from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    event,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from creative_os.models.base import Base


def new_id() -> str:
    return str(uuid4())


class ImmutableVersionError(RuntimeError):
    pass


class Program(Base):
    __tablename__ = "programs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    slug: Mapped[str] = mapped_column(String(120), unique=True)
    name: Mapped[str] = mapped_column(String(240))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Ecosystem(Base):
    __tablename__ = "ecosystems"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    code: Mapped[str] = mapped_column(String(80), unique=True)
    name: Mapped[str] = mapped_column(String(160))


class ProgramEcosystem(Base):
    __tablename__ = "program_ecosystems"
    __table_args__ = (UniqueConstraint("program_id", "ecosystem_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    program_id: Mapped[str] = mapped_column(ForeignKey("programs.id"))
    ecosystem_id: Mapped[str] = mapped_column(ForeignKey("ecosystems.id"))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (UniqueConstraint("program_id", "slug"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    program_id: Mapped[str] = mapped_column(ForeignKey("programs.id"))
    slug: Mapped[str] = mapped_column(String(120))
    name: Mapped[str] = mapped_column(String(240))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Campaign(Base):
    __tablename__ = "campaigns"
    __table_args__ = (UniqueConstraint("program_id", "slug"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    program_id: Mapped[str] = mapped_column(ForeignKey("programs.id"))
    account_id: Mapped[str | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    slug: Mapped[str] = mapped_column(String(120))
    name: Mapped[str] = mapped_column(String(240))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Creative(Base):
    __tablename__ = "creatives"
    __table_args__ = (UniqueConstraint("program_id", "slug"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    program_id: Mapped[str] = mapped_column(ForeignKey("programs.id"))
    account_id: Mapped[str | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    campaign_id: Mapped[str | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True)
    ecosystem_id: Mapped[str | None] = mapped_column(ForeignKey("ecosystems.id"), nullable=True)
    slug: Mapped[str] = mapped_column(String(160))
    name: Mapped[str] = mapped_column(String(240))
    status: Mapped[str] = mapped_column(String(40))
    holdout: Mapped[bool] = mapped_column(Boolean, default=False)
    current_approved_story_lock_version_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "story_lock_versions.id",
            use_alter=True,
            name="fk_creative_current_lock",
        ),
        nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    story_lock: Mapped["StoryLock | None"] = relationship(back_populates="creative", uselist=False)


class StoryLock(Base):
    __tablename__ = "story_locks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    creative_id: Mapped[str] = mapped_column(ForeignKey("creatives.id"), unique=True)
    name: Mapped[str] = mapped_column(String(240))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    creative: Mapped[Creative] = relationship(back_populates="story_lock")
    versions: Mapped[list["StoryLockVersion"]] = relationship(back_populates="story_lock")


class StoryLockVersion(Base):
    __tablename__ = "story_lock_versions"
    __table_args__ = (UniqueConstraint("story_lock_id", "version_number"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    story_lock_id: Mapped[str] = mapped_column(ForeignKey("story_locks.id"))
    version_number: Mapped[int] = mapped_column(Integer)
    supersedes_version_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    content_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    content_markdown: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64))
    change_reason: Mapped[str] = mapped_column(Text)
    approved_by: Mapped[str | None] = mapped_column(String(160), nullable=True)
    source_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    story_lock: Mapped[StoryLock] = relationship(back_populates="versions")


@event.listens_for(StoryLockVersion, "before_update")
def _reject_story_lock_mutation(_mapper, _connection, target: StoryLockVersion) -> None:
    from sqlalchemy.orm.attributes import get_history

    for attr in ("content_json", "content_markdown", "content_hash"):
        if get_history(target, attr).has_changes():
            raise ImmutableVersionError(
                f"story lock version {target.id} is immutable; field {attr} cannot change"
            )


class ApprovalEvent(Base):
    __tablename__ = "approval_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    object_type: Mapped[str] = mapped_column(String(80))
    object_id: Mapped[str] = mapped_column(String(36))
    version_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(String(40))
    actor: Mapped[str] = mapped_column(String(160))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    previous_state: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class SkillArtifact(Base):
    __tablename__ = "skill_artifacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    slug: Mapped[str] = mapped_column(String(160), unique=True)
    name: Mapped[str] = mapped_column(String(240))


class SkillVersion(Base):
    __tablename__ = "skill_versions"
    __table_args__ = (UniqueConstraint("skill_id", "content_hash"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    skill_id: Mapped[str] = mapped_column(ForeignKey("skill_artifacts.id"))
    version_label: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(80))
    scope_level: Mapped[str] = mapped_column(String(40))
    rule_kind: Mapped[str | None] = mapped_column(String(40), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64))
    source_path: Mapped[str] = mapped_column(Text)
    effective_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    supersedes_version_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    approval_state: Mapped[str] = mapped_column(String(40))
    dependencies: Mapped[list[Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PolicyRule(Base):
    __tablename__ = "policy_rules"
    __table_args__ = (UniqueConstraint("code", "content_hash", "scope_level", "scope_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    code: Mapped[str] = mapped_column(String(120))
    scope_level: Mapped[str] = mapped_column(String(40))
    scope_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    rule_kind: Mapped[str] = mapped_column(String(40))
    title: Mapped[str] = mapped_column(String(240))
    text: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40))
    source_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64))
    effective_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class SourceArtifact(Base):
    __tablename__ = "source_artifacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    relative_path: Mapped[str] = mapped_column(Text, unique=True)
    sha256: Mapped[str] = mapped_column(String(64))
    size_bytes: Mapped[int] = mapped_column(Integer)
    kind: Mapped[str] = mapped_column(String(40))
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ReferenceBank(Base):
    __tablename__ = "reference_banks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(240))
    ecosystem_id: Mapped[str | None] = mapped_column(ForeignKey("ecosystems.id"), nullable=True)
    original_path: Mapped[str] = mapped_column(Text, unique=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    creative_id: Mapped[str | None] = mapped_column(ForeignKey("creatives.id"), nullable=True)
    reference_bank_id: Mapped[str | None] = mapped_column(ForeignKey("reference_banks.id"), nullable=True)
    bound_story_lock_version_id: Mapped[str | None] = mapped_column(
        ForeignKey("story_lock_versions.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(240))
    role: Mapped[str] = mapped_column(String(40))
    rights_status: Mapped[str] = mapped_column(String(40))
    original_path: Mapped[str] = mapped_column(Text, unique=True)
    storage_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    present_in_snapshot: Mapped[bool] = mapped_column(Boolean, default=False)
    source_exists_claim: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    approved: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    stale: Mapped[bool] = mapped_column(Boolean, default=False)
    ecosystem_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    story_key: Mapped[str | None] = mapped_column(String(160), nullable=True)
    editing_method: Mapped[str | None] = mapped_column(String(120), nullable=True)
    provider_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(120), nullable=True)
    product_model: Mapped[str | None] = mapped_column(String(160), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AssetRelation(Base):
    __tablename__ = "asset_relations"
    __table_args__ = (UniqueConstraint("asset_id", "related_asset_id", "relation"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.id"))
    related_asset_id: Mapped[str] = mapped_column(ForeignKey("assets.id"))
    relation: Mapped[str] = mapped_column(String(40))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class StaleArtifactRecord(Base):
    __tablename__ = "stale_artifact_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.id"))
    story_lock_version_id: Mapped[str | None] = mapped_column(
        ForeignKey("story_lock_versions.id"), nullable=True
    )
    superseded_by_version_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    reason: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class RegressionTest(Base):
    __tablename__ = "regression_tests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    code: Mapped[str] = mapped_column(String(16), unique=True)
    category: Mapped[str] = mapped_column(String(80))
    input_text: Mapped[str] = mapped_column(Text)
    expected_decision: Mapped[str] = mapped_column(Text)
    pass_conditions: Mapped[list[Any]] = mapped_column(JSON)
    fail_conditions: Mapped[list[Any]] = mapped_column(JSON)
    source_rule: Mapped[str] = mapped_column(Text)
    evaluation_mode: Mapped[str] = mapped_column(String(40))
    content_hash: Mapped[str] = mapped_column(String(64))


class BenchmarkCreative(Base):
    __tablename__ = "benchmark_creatives"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(240), unique=True)
    account_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    category: Mapped[str | None] = mapped_column(String(40), nullable=True)
    ecosystem_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    views: Mapped[int | None] = mapped_column(Integer, nullable=True)
    likes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comments: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shares: Mapped[int | None] = mapped_column(Integer, nullable=True)
    saves: Mapped[int | None] = mapped_column(Integer, nullable=True)
    lesson: Mapped[str | None] = mapped_column(Text, nullable=True)
    holdout: Mapped[bool] = mapped_column(Boolean, default=False)
    source_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    metrics_note: Mapped[str | None] = mapped_column(Text, nullable=True)


class ValidationRun(Base):
    __tablename__ = "validation_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    subject_type: Mapped[str] = mapped_column(String(80))
    subject_id: Mapped[str] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    results: Mapped[list["ValidationResult"]] = relationship(back_populates="run")


class ValidationResult(Base):
    __tablename__ = "validation_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    run_id: Mapped[str] = mapped_column(ForeignKey("validation_runs.id"))
    check_code: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(40))
    message: Mapped[str] = mapped_column(Text)
    details: Mapped[dict[str, Any]] = mapped_column(JSON)

    run: Mapped[ValidationRun] = relationship(back_populates="results")


class ModelProvider(Base):
    __tablename__ = "model_providers"
    __table_args__ = (UniqueConstraint("name", "capability"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(120))
    capability: Mapped[str] = mapped_column(String(80))
    model_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(160), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class ModelRun(Base):
    __tablename__ = "model_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    provider_id: Mapped[str | None] = mapped_column(ForeignKey("model_providers.id"), nullable=True)
    capability: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(40))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    input_refs: Mapped[dict[str, Any]] = mapped_column(JSON)
    output_refs: Mapped[dict[str, Any]] = mapped_column(JSON)
    cost: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)


class CreativeGenome(Base):
    __tablename__ = "creative_genomes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    creative_id: Mapped[str] = mapped_column(ForeignKey("creatives.id"))
    version_label: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class GenomeFacet(Base):
    __tablename__ = "genome_facets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    genome_id: Mapped[str] = mapped_column(ForeignKey("creative_genomes.id"))
    dimension: Mapped[str] = mapped_column(String(80))
    value: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(Text)
    assignment: Mapped[str] = mapped_column(String(40))
    confidence: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AccountDnaProfile(Base):
    __tablename__ = "account_dna_profiles"
    __table_args__ = (UniqueConstraint("account_id", "version_number"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"))
    version_number: Mapped[int] = mapped_column(Integer)
    supersedes_profile_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AccountDnaObservation(Base):
    __tablename__ = "account_dna_observations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    profile_id: Mapped[str] = mapped_column(ForeignKey("account_dna_profiles.id"))
    field_name: Mapped[str] = mapped_column(String(120))
    value: Mapped[str] = mapped_column(Text)
    evidence_kind: Mapped[str] = mapped_column(String(40))
    confidence: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    sample_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    date_start: Mapped[str | None] = mapped_column(String(40), nullable=True)
    date_end: Mapped[str | None] = mapped_column(String(40), nullable=True)
    source_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(240))
    hypothesis: Mapped[str] = mapped_column(Text)
    account_id: Mapped[str | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    campaign_id: Mapped[str | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True)
    creative_id: Mapped[str | None] = mapped_column(ForeignKey("creatives.id"), nullable=True)
    variable_dimension: Mapped[str] = mapped_column(String(80))
    fixed_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    primary_metric: Mapped[str | None] = mapped_column(String(80), nullable=True)
    secondary_metrics: Mapped[list[Any]] = mapped_column(JSON)
    measurement_window: Mapped[str | None] = mapped_column(String(120), nullable=True)
    result: Mapped[str | None] = mapped_column(Text, nullable=True)
    interpretation: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[str | None] = mapped_column(String(40), nullable=True)
    follow_up: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ExperimentVariant(Base):
    __tablename__ = "experiment_variants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    experiment_id: Mapped[str] = mapped_column(ForeignKey("experiments.id"))
    name: Mapped[str] = mapped_column(String(160))
    is_control: Mapped[bool] = mapped_column(Boolean, default=False)
    changes: Mapped[dict[str, Any]] = mapped_column(JSON)
    fixed: Mapped[dict[str, Any]] = mapped_column(JSON)
    post_id: Mapped[str | None] = mapped_column(String(36), nullable=True)


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    creative_id: Mapped[str | None] = mapped_column(ForeignKey("creatives.id"), nullable=True)
    account_id: Mapped[str | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    external_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    platform: Mapped[str] = mapped_column(String(40))
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PerformanceSnapshot(Base):
    __tablename__ = "performance_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    post_id: Mapped[str] = mapped_column(ForeignKey("posts.id"))
    source: Mapped[str] = mapped_column(String(80))
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    post_age_hours: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    measurement_window: Mapped[str | None] = mapped_column(String(120), nullable=True)
    views: Mapped[int | None] = mapped_column(Integer, nullable=True)
    likes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comments: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shares: Mapped[int | None] = mapped_column(Integer, nullable=True)
    saves: Mapped[int | None] = mapped_column(Integer, nullable=True)
    profile_visits: Mapped[int | None] = mapped_column(Integer, nullable=True)
    link_clicks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    conversions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    revenue: Mapped[str | None] = mapped_column(String(40), nullable=True)
    watch_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    slide_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)


class CommentDoor(Base):
    __tablename__ = "comment_doors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    creative_id: Mapped[str] = mapped_column(ForeignKey("creatives.id"))
    story_lock_version_id: Mapped[str | None] = mapped_column(
        ForeignKey("story_lock_versions.id"), nullable=True
    )
    kind: Mapped[str] = mapped_column(String(40))
    text: Mapped[str] = mapped_column(Text)
    prediction_notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    post_id: Mapped[str] = mapped_column(ForeignKey("posts.id"))
    body: Mapped[str] = mapped_column(Text)
    stance: Mapped[str | None] = mapped_column(String(80), nullable=True)
    source: Mapped[str | None] = mapped_column(String(80), nullable=True)
    observed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class CommentCluster(Base):
    __tablename__ = "comment_clusters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    post_id: Mapped[str] = mapped_column(ForeignKey("posts.id"))
    label: Mapped[str] = mapped_column(String(240))
    size: Mapped[int] = mapped_column(Integer)
    example_comments: Mapped[list[Any]] = mapped_column(JSON)
    sentiment: Mapped[str | None] = mapped_column(String(80), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    unexpected: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class CommentDoorMapping(Base):
    __tablename__ = "comment_door_mappings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    door_id: Mapped[str | None] = mapped_column(ForeignKey("comment_doors.id"), nullable=True)
    cluster_id: Mapped[str | None] = mapped_column(ForeignKey("comment_clusters.id"), nullable=True)
    relationship: Mapped[str] = mapped_column(String(40))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class StoryLineItem(Base):
    __tablename__ = "story_line_items"
    __table_args__ = (UniqueConstraint("story_lock_version_id", "position"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    story_lock_version_id: Mapped[str] = mapped_column(ForeignKey("story_lock_versions.id"))
    position: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(Text)
    quantity: Mapped[str | None] = mapped_column(String(40), nullable=True)
    unit_price: Mapped[str | None] = mapped_column(String(40), nullable=True)
    model: Mapped[str | None] = mapped_column(String(160), nullable=True)
    generation: Mapped[str | None] = mapped_column(String(40), nullable=True)
    variant: Mapped[str | None] = mapped_column(String(120), nullable=True)
    color: Mapped[str | None] = mapped_column(String(80), nullable=True)
    pack_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    external_id: Mapped[str | None] = mapped_column(String(80), nullable=True)


class SlideProjection(Base):
    __tablename__ = "slide_projections"
    __table_args__ = (UniqueConstraint("story_lock_version_id", "slide_index"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    story_lock_version_id: Mapped[str] = mapped_column(ForeignKey("story_lock_versions.id"))
    slide_index: Mapped[int] = mapped_column(Integer)
    beat: Mapped[str | None] = mapped_column(Text, nullable=True)
    relative_time: Mapped[str | None] = mapped_column(Text, nullable=True)
    visible_clock: Mapped[str | None] = mapped_column(Text, nullable=True)
    visible_date: Mapped[str | None] = mapped_column(Text, nullable=True)
    overlay: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_state: Mapped[str | None] = mapped_column(Text, nullable=True)
    actor_knowledge: Mapped[str | None] = mapped_column(Text, nullable=True)
    actor_location: Mapped[str | None] = mapped_column(Text, nullable=True)


class ContinuityEntry(Base):
    __tablename__ = "continuity_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    story_lock_version_id: Mapped[str] = mapped_column(ForeignKey("story_lock_versions.id"))
    slide_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    field: Mapped[str] = mapped_column(String(80))
    value: Mapped[str] = mapped_column(Text)


class ViralTextureDetail(Base):
    __tablename__ = "viral_texture_details"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    story_lock_version_id: Mapped[str] = mapped_column(ForeignKey("story_lock_versions.id"))
    slide_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    text: Mapped[str] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)


class MechanicObservation(Base):
    __tablename__ = "mechanic_observations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    creative_id: Mapped[str] = mapped_column(ForeignKey("creatives.id"))
    dimension: Mapped[str] = mapped_column(String(80))
    value: Mapped[str] = mapped_column(Text)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    source: Mapped[str] = mapped_column(Text)
