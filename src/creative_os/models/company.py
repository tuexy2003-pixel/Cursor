"""Company control-plane records. These reference Creative OS objects; they do not copy them."""

from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    event,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.attributes import get_history

from creative_os.models.base import Base
from creative_os.models.entities import ImmutableVersionError, new_id


class WorkOrder(Base):
    __tablename__ = "work_orders"
    __table_args__ = (Index("ix_work_orders_status", "status", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    goal: Mapped[str] = mapped_column(Text)
    program_id: Mapped[str] = mapped_column(ForeignKey("programs.id"))
    account_id: Mapped[str | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    campaign_id: Mapped[str | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True)
    creative_id: Mapped[str | None] = mapped_column(ForeignKey("creatives.id"), nullable=True)
    priority: Mapped[str] = mapped_column(String(40), default="NORMAL")
    requested_by: Mapped[str] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(40), default="DRAFT")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_ids: Mapped[list[Any]] = mapped_column(JSON, default=list)
    reference_requirements: Mapped[list[Any]] = mapped_column(JSON, default=list)


class WorkflowDefinition(Base):
    __tablename__ = "workflow_definitions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    key: Mapped[str] = mapped_column(String(80), unique=True)
    name: Mapped[str] = mapped_column(String(240))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class WorkflowDefinitionVersion(Base):
    __tablename__ = "workflow_definition_versions"
    __table_args__ = (UniqueConstraint("definition_id", "version_number"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    definition_id: Mapped[str] = mapped_column(ForeignKey("workflow_definitions.id"))
    version_number: Mapped[int] = mapped_column(Integer)
    graph: Mapped[list[Any]] = mapped_column(JSON)
    graph_hash: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    work_order_id: Mapped[str] = mapped_column(ForeignKey("work_orders.id"))
    definition_version_id: Mapped[str] = mapped_column(ForeignKey("workflow_definition_versions.id"))
    status: Mapped[str] = mapped_column(String(40), default="RUNNING")
    memory: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class StepRun(Base):
    __tablename__ = "step_runs"
    __table_args__ = (UniqueConstraint("workflow_run_id", "node_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    workflow_run_id: Mapped[str] = mapped_column(ForeignKey("workflow_runs.id"))
    position: Mapped[int] = mapped_column(Integer)
    node_id: Mapped[str] = mapped_column(String(80))
    node_kind: Mapped[str] = mapped_column(String(80))
    input_refs: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    output_refs: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(40), default="PENDING")
    specialist_role: Mapped[str | None] = mapped_column(String(80), nullable=True)
    capability: Mapped[str | None] = mapped_column(String(80), nullable=True)
    attempt: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    error_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_ids: Mapped[list[Any]] = mapped_column(JSON, default=list)


class WorkflowEvent(Base):
    __tablename__ = "workflow_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    workflow_run_id: Mapped[str] = mapped_column(ForeignKey("workflow_runs.id"))
    step_run_id: Mapped[str | None] = mapped_column(ForeignKey("step_runs.id"), nullable=True)
    from_status: Mapped[str | None] = mapped_column(String(40), nullable=True)
    to_status: Mapped[str] = mapped_column(String(40))
    actor: Mapped[str] = mapped_column(String(160))
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Specialist(Base):
    __tablename__ = "specialists"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    role: Mapped[str] = mapped_column(String(80), unique=True)
    capabilities: Mapped[list[Any]] = mapped_column(JSON)
    transports: Mapped[list[Any]] = mapped_column(JSON)
    authoritative: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class SpecialistAssignment(Base):
    __tablename__ = "specialist_assignments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    step_run_id: Mapped[str] = mapped_column(ForeignKey("step_runs.id"))
    specialist_role: Mapped[str] = mapped_column(String(80))
    transport: Mapped[str] = mapped_column(String(40))
    creative_task_id: Mapped[str | None] = mapped_column(ForeignKey("creative_tasks.id"), nullable=True)
    context_bundle_id: Mapped[str | None] = mapped_column(ForeignKey("context_bundles.id"), nullable=True)
    context_bundle_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    provider_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    api_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(40), default="PENDING")
    contract_name: Mapped[str] = mapped_column(String(80))
    raw_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_response: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    validation_status: Mapped[str] = mapped_column(String(40), default="PENDING")
    imported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    result_refs: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    error_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class EvidenceRecord(Base):
    __tablename__ = "evidence_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    evidence_type: Mapped[str] = mapped_column(String(80))
    source: Mapped[str] = mapped_column(String(160))
    subject_type: Mapped[str] = mapped_column(String(80))
    subject_id: Mapped[str] = mapped_column(String(36))
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    claims_supported: Mapped[list[Any]] = mapped_column(JSON, default=list)
    verification_state: Mapped[str] = mapped_column(String(40), default="RECORDED")
    workflow_run_id: Mapped[str | None] = mapped_column(ForeignKey("workflow_runs.id"), nullable=True)
    step_run_id: Mapped[str | None] = mapped_column(ForeignKey("step_runs.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    approval_type: Mapped[str] = mapped_column(String(80))
    subject_type: Mapped[str] = mapped_column(String(80))
    subject_id: Mapped[str] = mapped_column(String(36))
    subject_hash: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(40), default="PENDING")
    requested_by: Mapped[str] = mapped_column(String(160))
    decided_by: Mapped[str | None] = mapped_column(String(160), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    workflow_run_id: Mapped[str | None] = mapped_column(ForeignKey("workflow_runs.id"), nullable=True)
    step_run_id: Mapped[str | None] = mapped_column(ForeignKey("step_runs.id"), nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ActionAuthorization(Base):
    __tablename__ = "action_authorizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    action_type: Mapped[str] = mapped_column(String(80))
    subject_type: Mapped[str] = mapped_column(String(80))
    subject_id: Mapped[str] = mapped_column(String(64))
    payload_hash: Mapped[str] = mapped_column(String(64))
    target: Mapped[str | None] = mapped_column(String(240), nullable=True)
    limits: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    requested_by: Mapped[str] = mapped_column(String(160))
    authorizer: Mapped[str | None] = mapped_column(String(160), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(40), default="PENDING")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ExternalExecution(Base):
    __tablename__ = "external_executions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    action_authorization_id: Mapped[str | None] = mapped_column(
        ForeignKey("action_authorizations.id"), nullable=True
    )
    action_type: Mapped[str] = mapped_column(String(80))
    adapter: Mapped[str] = mapped_column(String(80), default="NONE")
    status: Mapped[str] = mapped_column(String(40), default="REQUESTED")
    detail: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    reported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class VerificationResult(Base):
    __tablename__ = "verification_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    external_execution_id: Mapped[str] = mapped_column(ForeignKey("external_executions.id"))
    status: Mapped[str] = mapped_column(String(40))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class McpAuditLog(Base):
    __tablename__ = "mcp_audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    caller: Mapped[str] = mapped_column(String(160))
    interface: Mapped[str] = mapped_column(String(40), default="MCP")
    operation: Mapped[str] = mapped_column(String(120))
    input_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    affected_records: Mapped[list[Any]] = mapped_column(JSON, default=list)
    result_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


@event.listens_for(WorkflowDefinitionVersion, "before_update")
def _freeze_workflow_graph(_mapper: object, _connection: object, target: WorkflowDefinitionVersion) -> None:
    if get_history(target, "graph").has_changes() or get_history(target, "graph_hash").has_changes():
        raise ImmutableVersionError("workflow definition versions are immutable")
