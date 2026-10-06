"""Working-policy and scope corrections that sit on top of the imported snapshot."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from creative_os.models import Account, ApprovalEvent, PolicyRule, Program, SkillArtifact, SkillVersion
from creative_os.util import sha256_text, utcnow

EXAMPLE_BEFORE = "my birthday is literally tomorrow 😭"
EXAMPLE_AFTER = "my birthday is literally today 😭"
WORKING_LABEL = "working-2026-10-06"
POLICY_REASON = (
    "Human-authorized migration cleanup. The GOOD floating-hook illustration now matches "
    "the approved story lock wording. This does not require hooks to say today."
)


def apply_preservation_baseline(session: Session) -> dict[str, str]:
    policy = apply_working_policy(session)
    scope = apply_scope_corrections(session)
    return {"policy": policy, "scope": scope}


def apply_working_policy(session: Session) -> str:
    skill = session.scalar(select(SkillArtifact).where(SkillArtifact.slug == "production-spec-qa"))
    if skill is None:
        raise RuntimeError("production-spec-qa was not imported")
    parent = session.scalar(
        select(SkillVersion).where(
            SkillVersion.skill_id == skill.id,
            SkillVersion.version_label == "handoff-2026-10-05",
        )
    )
    if parent is None:
        raise RuntimeError("imported production-spec-qa version is missing")
    if parent.content.count(EXAMPLE_BEFORE) != 1:
        raise RuntimeError("expected exactly one superseded floating-hook example in the imported skill")
    updated = parent.content.replace(EXAMPLE_BEFORE, EXAMPLE_AFTER, 1)
    if updated.count(EXAMPLE_AFTER) < 1 or EXAMPLE_BEFORE in updated:
        raise RuntimeError("working policy replacement did not apply cleanly")
    digest = sha256_text(updated)
    existing = session.scalar(
        select(SkillVersion).where(SkillVersion.skill_id == skill.id, SkillVersion.content_hash == digest)
    )
    if existing is None:
        existing = SkillVersion(
            skill_id=skill.id,
            version_label=WORKING_LABEL,
            status=parent.status,
            scope_level=parent.scope_level,
            rule_kind=parent.rule_kind,
            content=updated,
            content_hash=digest,
            source_path="skills/production-spec-qa/SKILL.md#working-example-correction",
            effective_from=utcnow(),
            supersedes_version_id=parent.id,
            approval_state="APPROVED",
            dependencies=list(parent.dependencies or []),
            created_at=utcnow(),
        )
        session.add(existing)
        session.flush()
    skill.current_version_id = existing.id
    approval = session.scalar(
        select(ApprovalEvent).where(
            ApprovalEvent.version_id == existing.id,
            ApprovalEvent.status == "APPROVED",
        )
    )
    if approval is None:
        session.add(
            ApprovalEvent(
                object_type="skill_version",
                object_id=skill.id,
                version_id=existing.id,
                status="APPROVED",
                actor="operator",
                notes=(
                    f"{POLICY_REASON} Exact diff: {EXAMPLE_BEFORE!r} -> {EXAMPLE_AFTER!r}. "
                    f"Parent imported version {parent.id}."
                ),
                previous_state=f"current={parent.id}",
                created_at=utcnow(),
            )
        )
    return existing.id


def apply_scope_corrections(session: Session) -> str:
    program = session.scalar(select(Program).where(Program.slug == "mydashperks"))
    if program is None:
        raise RuntimeError("program mydashperks is missing")
    notes: list[str] = []
    money = session.scalar(
        select(PolicyRule).where(PolicyRule.code == "principles-a-15", PolicyRule.scope_level == "GLOBAL")
    )
    if money is None:
        raise RuntimeError("money-path principle was not imported")
    if money.status == "active":
        money.status = "superseded"
        _approve_scope(
            session,
            money,
            "Superseded as a global invariant. Money-path presentation is a MyDashPerks program rule.",
        )
    _ensure_program_copy(session, money, program.id)
    notes.append("money-path")
    lanes = session.scalar(
        select(PolicyRule).where(PolicyRule.code == "principles-c-02", PolicyRule.scope_level == "PROGRAM")
    )
    if lanes is None or "Maria" not in lanes.text:
        raise RuntimeError("account-lane principle was not imported")
    if lanes.status == "active":
        lanes.status = "superseded"
        _approve_scope(
            session,
            lanes,
            "Superseded as one program blob. Each account lane is now an account preference.",
        )
    accounts = {row.slug: row for row in session.scalars(select(Account)).all()}
    for slug, text in (
        ("maria", "Maria covers food and couples (e.g. Dre)."),
        ("sarah", "Sarah covers electronics."),
        ("brooke", "Brooke covers electronics."),
    ):
        _ensure_account_rule(session, accounts[slug], f"account-lane-{slug}", text)
    notes.append("account-lanes")
    return ",".join(notes)


def _ensure_program_copy(session: Session, source: PolicyRule, program_id: str) -> None:
    existing = session.scalar(
        select(PolicyRule).where(
            PolicyRule.code == source.code,
            PolicyRule.content_hash == source.content_hash,
            PolicyRule.scope_level == "PROGRAM",
            PolicyRule.scope_id == program_id,
        )
    )
    if existing:
        return
    session.add(
        PolicyRule(
            code=source.code,
            scope_level="PROGRAM",
            scope_id=program_id,
            rule_kind="INVARIANT",
            title=source.title,
            text=source.text,
            status="active",
            source_path=source.source_path,
            content_hash=source.content_hash,
            supersedes_rule_id=source.id,
            source_artifact_id=source.source_artifact_id,
            approval_state="APPROVED",
            effective_from=utcnow(),
            created_at=utcnow(),
        )
    )


def _ensure_account_rule(session: Session, account: Account, code: str, text: str) -> None:
    digest = sha256_text(text)
    existing = session.scalar(
        select(PolicyRule).where(
            PolicyRule.code == code,
            PolicyRule.content_hash == digest,
            PolicyRule.scope_level == "ACCOUNT",
            PolicyRule.scope_id == account.id,
        )
    )
    if existing:
        return
    session.add(
        PolicyRule(
            code=code,
            scope_level="ACCOUNT",
            scope_id=account.id,
            rule_kind="PREFERENCE",
            title=text,
            text=text,
            status="active",
            source_path="PRINCIPLES_VS_HEURISTICS.md#scope-audit",
            content_hash=digest,
            effective_from=utcnow(),
            created_at=utcnow(),
        )
    )


def _approve_scope(session: Session, rule: PolicyRule, notes: str) -> None:
    session.add(
        ApprovalEvent(
            object_type="policy_rule",
            object_id=rule.id,
            version_id=None,
            status="SUPERSEDED",
            actor="operator",
            notes=f"Human-authorized migration cleanup. {notes}",
            previous_state="active",
            created_at=utcnow(),
        )
    )
