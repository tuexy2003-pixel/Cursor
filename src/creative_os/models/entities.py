from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
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
    current_approved_dna_profile_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "account_dna_profiles.id",
            use_alter=True,
            name="fk_account_current_dna",
        ),
        nullable=True,
    )
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
    current_genome_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "creative_genomes.id",
            use_alter=True,
            name="fk_creative_current_genome",
        ),
        nullable=True,
    )
    selected_concept_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "concept_candidates.id",
            use_alter=True,
            name="fk_creative_selected_concept",
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
    supersedes_version_id: Mapped[str | None] = mapped_column(
        ForeignKey("story_lock_versions.id"), nullable=True
    )
    content_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    content_markdown: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64))
    document_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    approval_state: Mapped[str] = mapped_column(String(40), default="APPROVED")
    change_reason: Mapped[str] = mapped_column(Text)
    approved_by: Mapped[str | None] = mapped_column(String(160), nullable=True)
    source_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    story_lock: Mapped[StoryLock] = relationship(back_populates="versions")


_STORY_LOCK_CONTENT = (
    "content_json",
    "content_markdown",
    "content_hash",
    "document_hash",
    "change_reason",
    "supersedes_version_id",
    "source_path",
    "source_hash",
    "version_number",
    "story_lock_id",
)
_STORY_LOCK_TRANSITIONS = {
    ("PENDING", "APPROVED"),
    ("PENDING", "REJECTED"),
    ("PENDING", "NEEDS_CHANGES"),
}


@event.listens_for(StoryLockVersion, "before_update")
def _reject_story_lock_mutation(_mapper, _connection, target: StoryLockVersion) -> None:
    from sqlalchemy.orm.attributes import get_history

    from creative_os.services.lifecycle import consume_lifecycle

    for attr in _STORY_LOCK_CONTENT:
        if get_history(target, attr).has_changes():
            raise ImmutableVersionError(
                f"story lock version {target.id} is immutable; field {attr} cannot change"
            )
    state_history = get_history(target, "approval_state")
    actor_history = get_history(target, "approved_by")
    if not state_history.has_changes() and not actor_history.has_changes():
        return
    if not consume_lifecycle(target):
        raise ImmutableVersionError(
            f"story lock version {target.id} lifecycle can change only through the decision service"
        )
    if state_history.has_changes():
        old = state_history.deleted[0] if state_history.deleted else None
        new = state_history.added[0] if state_history.added else None
        if (old, new) not in _STORY_LOCK_TRANSITIONS:
            raise ImmutableVersionError(f"story lock version {target.id} cannot move from {old} to {new}")


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
    current_version_id: Mapped[str | None] = mapped_column(
        ForeignKey("skill_versions.id", use_alter=True, name="fk_skill_current_version"),
        nullable=True,
    )


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
    supersedes_version_id: Mapped[str | None] = mapped_column(ForeignKey("skill_versions.id"), nullable=True)
    approval_state: Mapped[str] = mapped_column(String(40))
    dependencies: Mapped[list[Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


_SKILL_CONTENT = (
    "content",
    "content_hash",
    "source_path",
    "scope_level",
    "rule_kind",
    "skill_id",
    "version_label",
    "supersedes_version_id",
    "dependencies",
)


@event.listens_for(SkillVersion, "before_update")
def _reject_skill_content_mutation(_mapper, _connection, target: SkillVersion) -> None:
    from sqlalchemy.orm.attributes import get_history

    from creative_os.services.lifecycle import consume_lifecycle

    for attr in _SKILL_CONTENT:
        if get_history(target, attr).has_changes():
            raise ImmutableVersionError(f"skill version {target.id} content field {attr} cannot change")
    status_history = get_history(target, "status")
    approval_history = get_history(target, "approval_state")
    if not status_history.has_changes() and not approval_history.has_changes():
        return
    if not consume_lifecycle(target):
        raise ImmutableVersionError(
            f"skill version {target.id} lifecycle can change only through an explicit transition"
        )


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
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    supersedes_rule_id: Mapped[str | None] = mapped_column(ForeignKey("policy_rules.id"), nullable=True)
    source_skill_version_id: Mapped[str | None] = mapped_column(ForeignKey("skill_versions.id"), nullable=True)
    source_artifact_id: Mapped[str | None] = mapped_column(ForeignKey("source_artifacts.id"), nullable=True)
    approval_state: Mapped[str] = mapped_column(String(40), default="APPROVED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


_POLICY_CONTENT = (
    "code",
    "scope_level",
    "scope_id",
    "rule_kind",
    "title",
    "text",
    "content_hash",
    "source_path",
    "source_skill_version_id",
    "source_artifact_id",
    "supersedes_rule_id",
)
_POLICY_STATUS_TRANSITIONS = {("active", "superseded")}


@event.listens_for(PolicyRule, "before_update")
def _reject_policy_content_mutation(_mapper, _connection, target: PolicyRule) -> None:
    from sqlalchemy.orm.attributes import get_history

    from creative_os.services.lifecycle import consume_lifecycle

    for attr in _POLICY_CONTENT:
        if get_history(target, attr).has_changes():
            raise ImmutableVersionError(f"policy rule {target.id} content field {attr} cannot change")
    lifecycle_fields = ("status", "approval_state", "effective_from", "effective_to")
    if not any(get_history(target, attr).has_changes() for attr in lifecycle_fields):
        return
    if not consume_lifecycle(target):
        raise ImmutableVersionError(
            f"policy rule {target.id} lifecycle can change only through an explicit transition"
        )
    status_history = get_history(target, "status")
    if status_history.has_changes():
        old = status_history.deleted[0] if status_history.deleted else None
        new = status_history.added[0] if status_history.added else None
        if (old, new) not in _POLICY_STATUS_TRANSITIONS:
            raise ImmutableVersionError(f"policy rule {target.id} cannot move from {old} to {new}")


class SourceSnapshot(Base):
    __tablename__ = "source_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    label: Mapped[str] = mapped_column(String(160), unique=True)
    captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    root_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    immutable: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class SourceArtifact(Base):
    __tablename__ = "source_artifacts"
    __table_args__ = (UniqueConstraint("snapshot_id", "relative_path"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    snapshot_id: Mapped[str] = mapped_column(ForeignKey("source_snapshots.id"))
    relative_path: Mapped[str] = mapped_column(Text)
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
    __table_args__ = (
        Index("ix_assets_creative_id", "creative_id"),
        Index("ix_assets_bound_story_lock_version_id", "bound_story_lock_version_id"),
    )

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
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    present_in_snapshot: Mapped[bool] = mapped_column(Boolean, default=False)
    source_exists_claim: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    approved: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    stale: Mapped[bool] = mapped_column(Boolean, default=False)
    staleness_state: Mapped[str] = mapped_column(String(40), default="CURRENT")
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


class ExampleLink(Base):
    __tablename__ = "example_links"
    __table_args__ = (UniqueConstraint("benchmark_id", "regression_test_id", "asset_id", "example_role"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    benchmark_id: Mapped[str | None] = mapped_column(ForeignKey("benchmark_creatives.id"), nullable=True)
    regression_test_id: Mapped[str | None] = mapped_column(ForeignKey("regression_tests.id"), nullable=True)
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.id"))
    example_role: Mapped[str] = mapped_column(String(40))
    reason: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AssetLockDependency(Base):
    __tablename__ = "asset_lock_dependencies"
    __table_args__ = (UniqueConstraint("asset_id", "field_path"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.id"))
    creative_id: Mapped[str | None] = mapped_column(ForeignKey("creatives.id"), nullable=True)
    field_path: Mapped[str] = mapped_column(String(240))
    slide_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    dependency_kind: Mapped[str] = mapped_column(String(40))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    explicit: Mapped[bool] = mapped_column(Boolean, default=True)


class StaleArtifactRecord(Base):
    __tablename__ = "stale_artifact_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.id"))
    story_lock_version_id: Mapped[str | None] = mapped_column(
        ForeignKey("story_lock_versions.id"), nullable=True
    )
    superseded_by_version_id: Mapped[str | None] = mapped_column(
        ForeignKey("story_lock_versions.id"), nullable=True
    )
    staleness_state: Mapped[str] = mapped_column(String(40), default="STALE")
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
    context_bundle_id: Mapped[str | None] = mapped_column(ForeignKey("context_bundles.id"), nullable=True)


class CreativeTask(Base):
    __tablename__ = "creative_tasks"
    __table_args__ = (Index("ix_creative_tasks_program", "program_id", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    program_id: Mapped[str] = mapped_column(ForeignKey("programs.id"))
    account_id: Mapped[str | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    campaign_id: Mapped[str | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True)
    creative_id: Mapped[str | None] = mapped_column(ForeignKey("creatives.id"), nullable=True)
    ecosystem_id: Mapped[str | None] = mapped_column(ForeignKey("ecosystems.id"), nullable=True)
    stage: Mapped[str] = mapped_column(String(80))
    instruction: Mapped[str] = mapped_column(Text)
    constraints: Mapped[dict[str, Any]] = mapped_column(JSON)
    input_refs: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_by: Mapped[str] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(40), default="OPEN")
    expected_output_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


_TASK_CONTENT = (
    "instruction",
    "constraints",
    "input_refs",
    "stage",
    "program_id",
    "account_id",
    "campaign_id",
    "creative_id",
    "ecosystem_id",
    "expected_output_type",
    "notes",
    "created_by",
)


@event.listens_for(CreativeTask, "before_update")
def _reject_consumed_task_mutation(_mapper, _connection, target: CreativeTask) -> None:
    from sqlalchemy.orm.attributes import get_history

    from creative_os.services.lifecycle import consume_lifecycle

    status = get_history(target, "status")
    old = status.deleted[0] if status.deleted else target.status
    if old == "CONSUMED":
        raise ImmutableVersionError(
            f"creative task {target.id} is immutable after it compiled a context bundle"
        )
    content_changed = any(get_history(target, attr).has_changes() for attr in _TASK_CONTENT)
    if not status.has_changes():
        return
    new = status.added[0] if status.added else None
    if (old, new) != ("OPEN", "CONSUMED") or not consume_lifecycle(target) or content_changed:
        raise ImmutableVersionError("creative task status can only move from OPEN to CONSUMED")


class ConceptCandidate(Base):
    __tablename__ = "concept_candidates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    task_id: Mapped[str | None] = mapped_column(ForeignKey("creative_tasks.id"), nullable=True)
    program_id: Mapped[str] = mapped_column(ForeignKey("programs.id"))
    account_id: Mapped[str | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    campaign_id: Mapped[str | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True)
    ecosystem_id: Mapped[str | None] = mapped_column(ForeignKey("ecosystems.id"), nullable=True)
    source_model_run_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    title: Mapped[str] = mapped_column(String(240))
    premise: Mapped[str | None] = mapped_column(Text, nullable=True)
    family: Mapped[str | None] = mapped_column(String(120), nullable=True)
    hook_direction: Mapped[str | None] = mapped_column(Text, nullable=True)
    commerce_relation: Mapped[str | None] = mapped_column(String(80), nullable=True)
    structured_payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(40), default="PROPOSED")
    created_by: Mapped[str] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


_CONCEPT_CONTENT = (
    "title",
    "premise",
    "family",
    "hook_direction",
    "commerce_relation",
    "structured_payload",
    "task_id",
    "program_id",
    "account_id",
    "campaign_id",
    "ecosystem_id",
    "created_by",
)
_CONCEPT_TRANSITIONS = {("PROPOSED", "SELECTED"), ("PROPOSED", "REJECTED"), ("SELECTED", "SUPERSEDED")}


@event.listens_for(ConceptCandidate, "before_update")
def _reject_concept_mutation(_mapper, _connection, target: ConceptCandidate) -> None:
    from sqlalchemy.orm.attributes import get_history

    from creative_os.services.lifecycle import consume_lifecycle

    status = get_history(target, "status")
    old = status.deleted[0] if status.deleted else target.status
    content_changed = any(get_history(target, attr).has_changes() for attr in _CONCEPT_CONTENT)
    if old in {"SELECTED", "REJECTED", "SUPERSEDED"} and content_changed:
        raise ImmutableVersionError(f"concept {target.id} content is immutable after {old}")
    if not status.has_changes():
        return
    new = status.added[0] if status.added else None
    if (old, new) not in _CONCEPT_TRANSITIONS or not consume_lifecycle(target) or content_changed:
        raise ImmutableVersionError(f"concept {target.id} cannot move from {old} to {new}")


class ContextBundle(Base):
    __tablename__ = "context_bundles"
    __table_args__ = (Index("ix_context_bundles_creative", "creative_id", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    creative_id: Mapped[str | None] = mapped_column(ForeignKey("creatives.id"), nullable=True)
    creative_task_id: Mapped[str | None] = mapped_column(ForeignKey("creative_tasks.id"), nullable=True)
    requested_stage: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    story_lock_version_id: Mapped[str | None] = mapped_column(
        ForeignKey("story_lock_versions.id"), nullable=True
    )
    account_id: Mapped[str | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    campaign_id: Mapped[str | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True)
    account_dna_profile_id: Mapped[str | None] = mapped_column(
        ForeignKey("account_dna_profiles.id"), nullable=True
    )
    creative_genome_id: Mapped[str | None] = mapped_column(ForeignKey("creative_genomes.id"), nullable=True)
    policy_rule_ids: Mapped[list[Any]] = mapped_column(JSON)
    skill_version_ids: Mapped[list[Any]] = mapped_column(JSON)
    benchmark_ids: Mapped[list[Any]] = mapped_column(JSON)
    reference_ids: Mapped[list[Any]] = mapped_column(JSON)
    mechanic_as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    compiled_payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    compiled_text: Mapped[str] = mapped_column(Text)
    payload_hash: Mapped[str] = mapped_column(String(64))
    compiler_version: Mapped[str] = mapped_column(String(40))
    size_estimate: Mapped[int] = mapped_column(Integer)
    token_estimate: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(40))


@event.listens_for(ContextBundle, "before_update")
def _reject_context_bundle_mutation(_mapper, _connection, target: ContextBundle) -> None:
    raise ImmutableVersionError(f"context bundle {target.id} is immutable")


class CreativeGenome(Base):
    __tablename__ = "creative_genomes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    creative_id: Mapped[str] = mapped_column(ForeignKey("creatives.id"))
    source_story_lock_version_id: Mapped[str | None] = mapped_column(
        ForeignKey("story_lock_versions.id"), nullable=True
    )
    version_label: Mapped[str] = mapped_column(String(80))
    origin: Mapped[str] = mapped_column(String(40), default="HUMAN_SET")
    approval_state: Mapped[str] = mapped_column(String(40), default="APPROVED")
    confidence: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    source_run_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class GenomeFacet(Base):
    __tablename__ = "genome_facets"
    __table_args__ = (Index("ix_genome_facets_genome_dimension", "genome_id", "dimension"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    genome_id: Mapped[str] = mapped_column(ForeignKey("creative_genomes.id"))
    dimension: Mapped[str] = mapped_column(String(80))
    value: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(Text)
    assignment: Mapped[str] = mapped_column(String(40))
    confidence: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


def _approved_parent(connection, table: str, parent_id: str) -> bool:
    from sqlalchemy import text

    row = connection.execute(
        text(f"SELECT approval_state FROM {table} WHERE id = :id"),
        {"id": parent_id},
    ).first()
    return row is not None and row[0] == "APPROVED"


def _reject_if_approved(connection, table: str, parent_id: str, message: str) -> None:
    if _approved_parent(connection, table, parent_id):
        raise ImmutableVersionError(message)


@event.listens_for(GenomeFacet, "before_insert")
@event.listens_for(GenomeFacet, "before_update")
@event.listens_for(GenomeFacet, "before_delete")
def _reject_approved_facet_mutation(_mapper, connection, target: GenomeFacet) -> None:
    _reject_if_approved(
        connection,
        "creative_genomes",
        target.genome_id,
        "approved creative genome facets cannot change in place",
    )


class AccountDnaProfile(Base):
    __tablename__ = "account_dna_profiles"
    __table_args__ = (UniqueConstraint("account_id", "version_number"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"))
    version_number: Mapped[int] = mapped_column(Integer)
    supersedes_profile_id: Mapped[str | None] = mapped_column(
        ForeignKey("account_dna_profiles.id"), nullable=True
    )
    approval_state: Mapped[str] = mapped_column(String(40), default="APPROVED")
    origin: Mapped[str] = mapped_column(String(40), default="HUMAN_SET")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AccountDnaObservation(Base):
    __tablename__ = "account_dna_observations"
    __table_args__ = (Index("ix_account_dna_observations_profile", "profile_id"),)

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


_PROFILE_TRANSITIONS = {("PENDING", "APPROVED")}
_GENOME_TRANSITIONS = {("PENDING", "APPROVED")}


@event.listens_for(AccountDnaProfile, "before_update")
def _reject_dna_profile_mutation(_mapper, _connection, target: AccountDnaProfile) -> None:
    from sqlalchemy.orm.attributes import get_history

    from creative_os.services.lifecycle import consume_lifecycle

    status = get_history(target, "approval_state")
    if status.has_changes():
        old = status.deleted[0] if status.deleted else None
        new = status.added[0] if status.added else None
        if (old, new) not in _PROFILE_TRANSITIONS or not consume_lifecycle(target):
            raise ImmutableVersionError(f"account DNA profile {target.id} cannot move from {old} to {new}")
        return
    if target.approval_state == "APPROVED":
        for attr in ("account_id", "version_number", "origin", "supersedes_profile_id"):
            if get_history(target, attr).has_changes():
                raise ImmutableVersionError(f"approved account DNA profile {target.id} cannot change {attr}")


@event.listens_for(AccountDnaObservation, "before_insert")
@event.listens_for(AccountDnaObservation, "before_update")
@event.listens_for(AccountDnaObservation, "before_delete")
def _reject_approved_observation_mutation(_mapper, connection, target: AccountDnaObservation) -> None:
    _reject_if_approved(
        connection,
        "account_dna_profiles",
        target.profile_id,
        "approved account DNA observations cannot change in place",
    )


@event.listens_for(CreativeGenome, "before_update")
def _reject_genome_mutation(_mapper, _connection, target: CreativeGenome) -> None:
    from sqlalchemy.orm.attributes import get_history

    from creative_os.services.lifecycle import consume_lifecycle

    status = get_history(target, "approval_state")
    if status.has_changes():
        old = status.deleted[0] if status.deleted else None
        new = status.added[0] if status.added else None
        if (old, new) not in _GENOME_TRANSITIONS or not consume_lifecycle(target):
            raise ImmutableVersionError(f"creative genome {target.id} cannot move from {old} to {new}")
        return
    if target.approval_state == "APPROVED":
        for attr in ("creative_id", "source_story_lock_version_id", "version_label", "origin"):
            if get_history(target, attr).has_changes():
                raise ImmutableVersionError(f"approved creative genome {target.id} cannot change {attr}")


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(240))
    hypothesis: Mapped[str] = mapped_column(Text)
    account_id: Mapped[str | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    campaign_id: Mapped[str | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True)
    creative_id: Mapped[str | None] = mapped_column(ForeignKey("creatives.id"), nullable=True)
    variable_dimension: Mapped[str] = mapped_column(String(80))
    mode: Mapped[str] = mapped_column(String(40), default="SINGLE_VARIABLE")
    changed_dimensions: Mapped[list[Any]] = mapped_column(JSON, default=list)
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


class ExperimentVariantPost(Base):
    __tablename__ = "experiment_variant_posts"
    __table_args__ = (UniqueConstraint("variant_id", "post_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    variant_id: Mapped[str] = mapped_column(ForeignKey("experiment_variants.id"))
    post_id: Mapped[str] = mapped_column(ForeignKey("posts.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Post(Base):
    __tablename__ = "posts"
    __table_args__ = (
        Index("ix_posts_account_published", "account_id", "published_at"),
        Index("ix_posts_creative_id", "creative_id"),
        Index("ix_posts_campaign_id", "campaign_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    creative_id: Mapped[str | None] = mapped_column(ForeignKey("creatives.id"), nullable=True)
    account_id: Mapped[str | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    campaign_id: Mapped[str | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True)
    external_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    platform: Mapped[str] = mapped_column(String(40))
    story_lock_version_id: Mapped[str | None] = mapped_column(
        ForeignKey("story_lock_versions.id"), nullable=True
    )
    creative_genome_id: Mapped[str | None] = mapped_column(ForeignKey("creative_genomes.id"), nullable=True)
    experiment_variant_id: Mapped[str | None] = mapped_column(
        ForeignKey("experiment_variants.id", use_alter=True, name="fk_post_experiment_variant"),
        nullable=True,
    )
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PostAsset(Base):
    __tablename__ = "post_assets"
    __table_args__ = (UniqueConstraint("post_id", "asset_id", "slide_index"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    post_id: Mapped[str] = mapped_column(ForeignKey("posts.id"))
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.id"))
    slide_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sort_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    role: Mapped[str | None] = mapped_column(String(40), nullable=True)


class PerformanceSnapshot(Base):
    __tablename__ = "performance_snapshots"
    __table_args__ = (Index("ix_performance_post_captured", "post_id", "captured_at"),)

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
    revenue_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    revenue_currency: Mapped[str | None] = mapped_column(String(8), nullable=True)
    watch_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    slide_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)


class CommentDoor(Base):
    __tablename__ = "comment_doors"
    __table_args__ = (Index("ix_comment_doors_creative_lock", "creative_id", "story_lock_version_id"),)

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
    __table_args__ = (Index("ix_comments_post_id", "post_id"),)

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


class CommentClusterMember(Base):
    __tablename__ = "comment_cluster_members"
    __table_args__ = (UniqueConstraint("cluster_id", "comment_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    cluster_id: Mapped[str] = mapped_column(ForeignKey("comment_clusters.id"))
    comment_id: Mapped[str] = mapped_column(ForeignKey("comments.id"))
    confidence: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    assigned_by: Mapped[str | None] = mapped_column(String(160), nullable=True)
    human_override: Mapped[bool] = mapped_column(Boolean, default=False)
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
    __table_args__ = (
        UniqueConstraint("story_lock_version_id", "position"),
        Index("ix_story_line_items_version", "story_lock_version_id"),
    )

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
    __table_args__ = (
        UniqueConstraint("story_lock_version_id", "slide_index"),
        Index("ix_slide_projections_version", "story_lock_version_id"),
    )

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
    __table_args__ = (Index("ix_mechanics_account_dimension_time", "account_id", "dimension", "observed_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    creative_id: Mapped[str] = mapped_column(ForeignKey("creatives.id"))
    account_id: Mapped[str | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    post_id: Mapped[str | None] = mapped_column(ForeignKey("posts.id"), nullable=True)
    story_lock_version_id: Mapped[str | None] = mapped_column(
        ForeignKey("story_lock_versions.id"), nullable=True
    )
    genome_id: Mapped[str | None] = mapped_column(ForeignKey("creative_genomes.id"), nullable=True)
    dimension: Mapped[str] = mapped_column(String(80))
    value: Mapped[str] = mapped_column(Text)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    source: Mapped[str] = mapped_column(Text)
