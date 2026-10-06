import json
import re
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from creative_os.importers.story_lock_parser import parse_story_lock_markdown
from creative_os.models import (
    Account,
    AccountDnaObservation,
    AccountDnaProfile,
    ApprovalEvent,
    Asset,
    BenchmarkCreative,
    Campaign,
    Creative,
    CreativeGenome,
    Ecosystem,
    GenomeFacet,
    MechanicObservation,
    ModelProvider,
    PolicyRule,
    Program,
    ProgramEcosystem,
    ReferenceBank,
    RegressionTest,
    SkillArtifact,
    SkillVersion,
    SourceArtifact,
    StoryLock,
    StoryLockVersion,
)
from creative_os.services.projections import replace_version_projections
from creative_os.util import sha256_bytes, sha256_text, utcnow
from creative_os.validation.regression import evaluation_mode_for

SNAPSHOT_EFFECTIVE = "2026-10-05T21:50:00-04:00"


class ImportReport:
    def __init__(self) -> None:
        self.inserted = 0
        self.skipped = 0
        self.notes: list[str] = []

    def add(self, skipped: bool) -> None:
        if skipped:
            self.skipped += 1
        else:
            self.inserted += 1

    def as_dict(self) -> dict[str, object]:
        return {"inserted": self.inserted, "skipped": self.skipped, "notes": self.notes}


def import_handoff(session: Session, snapshot_root: Path) -> ImportReport:
    report = ImportReport()
    if not snapshot_root.is_dir():
        raise FileNotFoundError(f"snapshot root does not exist: {snapshot_root}")
    _import_files(session, snapshot_root, report)
    manifest = json.loads((snapshot_root / "SYSTEM_MANIFEST.json").read_text(encoding="utf-8"))
    program = _program(session, report)
    ecosystems = _ecosystems(session, program, report)
    accounts = _accounts(session, program, report)
    campaign = _campaign(session, program, report)
    _skills(session, snapshot_root, manifest, report)
    _policies(session, snapshot_root, program, report)
    target = _target_creative(session, snapshot_root, program, campaign, ecosystems["TARGET"], report)
    _onions_creative(session, program, campaign, ecosystems["DOORDASH"], report)
    _assets(session, snapshot_root, target, ecosystems, report)
    _benchmarks(session, report)
    _regressions(session, snapshot_root, report)
    _providers(session, report)
    _dna(session, accounts, report)
    report.notes.append(
        "production-spec-qa still contains the superseded floating-hook example "
        "'my birthday is literally tomorrow'; the story lock's 'today' remains authoritative"
    )
    report.notes.append(
        "TARGET_CHORE_STUFF_TRANSACTION_MATH_SPEC.md totals ($5.33) are historical; "
        "the current story lock totals ($19.23) are the creative pointer"
    )
    return report


def _import_files(session: Session, root: Path, report: ImportReport) -> None:
    now = utcnow()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        data = path.read_bytes()
        digest = sha256_bytes(data)
        existing = session.scalar(select(SourceArtifact).where(SourceArtifact.relative_path == relative))
        if existing and existing.sha256 == digest:
            report.add(True)
            continue
        if existing:
            existing.sha256 = digest
            existing.size_bytes = len(data)
            report.add(False)
            continue
        session.add(
            SourceArtifact(
                relative_path=relative,
                sha256=digest,
                size_bytes=len(data),
                kind=_kind(relative),
                imported_at=now,
            )
        )
        report.add(False)


def _kind(relative: str) -> str:
    if relative.startswith("skills/") and relative.endswith("SKILL.md"):
        return "skill"
    if relative.startswith("story_locks/"):
        return "story_lock"
    if relative.endswith(".json"):
        return "json"
    if relative.endswith(".md"):
        return "markdown"
    return "file"


def _program(session: Session, report: ImportReport) -> Program:
    existing = session.scalar(select(Program).where(Program.slug == "mydashperks"))
    if existing:
        report.add(True)
        return existing
    program = Program(
        slug="mydashperks",
        name="MyDashPerks",
        description=(
            "Staged short-form carousel program. Current commercial ecosystems are "
            "configuration, not a limit of the engine."
        ),
        created_at=utcnow(),
    )
    session.add(program)
    session.flush()
    report.add(False)
    return program


def _ecosystems(session: Session, program: Program, report: ImportReport) -> dict[str, Ecosystem]:
    found: dict[str, Ecosystem] = {}
    for code, name in (("TARGET", "Target"), ("DOORDASH", "DoorDash")):
        row = session.scalar(select(Ecosystem).where(Ecosystem.code == code))
        if row is None:
            row = Ecosystem(code=code, name=name)
            session.add(row)
            session.flush()
            report.add(False)
        else:
            report.add(True)
        link = session.scalar(
            select(ProgramEcosystem).where(
                ProgramEcosystem.program_id == program.id,
                ProgramEcosystem.ecosystem_id == row.id,
            )
        )
        if link is None:
            session.add(
                ProgramEcosystem(
                    program_id=program.id,
                    ecosystem_id=row.id,
                    notes="Current program configuration from the 2026-10-05 handoff. Not a global invariant.",
                )
            )
            report.add(False)
        found[code] = row
    return found


def _accounts(session: Session, program: Program, report: ImportReport) -> dict[str, Account]:
    specs = {
        "maria": "Maria",
        "sarah": "Sarah",
        "brooke": "Brooke",
    }
    found: dict[str, Account] = {}
    for slug, name in specs.items():
        row = session.scalar(select(Account).where(Account.program_id == program.id, Account.slug == slug))
        if row is None:
            row = Account(
                program_id=program.id,
                slug=slug,
                name=name,
                notes="Named in ACCOUNT_STATE_TODAY.md. No account config file existed.",
                created_at=utcnow(),
            )
            session.add(row)
            session.flush()
            report.add(False)
        else:
            report.add(True)
        found[slug] = row
    return found


def _campaign(session: Session, program: Program, report: ImportReport) -> Campaign:
    row = session.scalar(
        select(Campaign).where(Campaign.program_id == program.id, Campaign.slug == "october-2026-benchmarks")
    )
    if row:
        report.add(True)
        return row
    row = Campaign(
        program_id=program.id,
        slug="october-2026-benchmarks",
        name="October 2026 benchmarks",
        notes="Holds the current Target and DoorDash benchmark creatives. Not a birthday-specific table.",
        created_at=utcnow(),
    )
    session.add(row)
    session.flush()
    report.add(False)
    return row


def _skills(session: Session, root: Path, manifest: dict, report: ImportReport) -> None:
    by_name = {item["name"]: item for item in manifest["skills"]}
    now = utcnow()
    for path in sorted((root / "skills").glob("*/SKILL.md")):
        slug = path.parent.name
        meta = by_name.get(slug, {})
        text = path.read_text(encoding="utf-8")
        digest = sha256_text(text)
        artifact = session.scalar(select(SkillArtifact).where(SkillArtifact.slug == slug))
        if artifact is None:
            artifact = SkillArtifact(slug=slug, name=_skill_name(text, slug))
            session.add(artifact)
            session.flush()
            report.add(False)
        else:
            report.add(True)
        existing = session.scalar(
            select(SkillVersion).where(
                SkillVersion.skill_id == artifact.id,
                SkillVersion.content_hash == digest,
            )
        )
        if existing:
            if artifact.current_version_id is None:
                artifact.current_version_id = existing.id
            report.add(True)
            continue
        version = SkillVersion(
            skill_id=artifact.id,
            version_label="handoff-2026-10-05",
            status=str(meta.get("status", "UNKNOWN")),
            scope_level="GLOBAL",
            rule_kind="HEURISTIC",
            content=text,
            content_hash=digest,
            source_path=str(meta.get("path") or path.relative_to(root).as_posix()),
            effective_from=now,
            supersedes_version_id=None,
            approval_state="IMPORTED",
            dependencies=list(meta.get("calls_or_depends_on") or []),
            created_at=now,
        )
        session.add(version)
        session.flush()
        if artifact.current_version_id is None:
            artifact.current_version_id = version.id
        report.add(False)
    playbook = root / "skills/live-heat-scout/QUERY_HYGIENE_PLAYBOOK.md"
    if playbook.exists():
        text = playbook.read_text(encoding="utf-8")
        digest = sha256_text(text)
        artifact = session.scalar(select(SkillArtifact).where(SkillArtifact.slug == "live-heat-scout"))
        if artifact is not None:
            existing = session.scalar(
                select(SkillVersion).where(
                    SkillVersion.skill_id == artifact.id,
                    SkillVersion.content_hash == digest,
                )
            )
            if existing is None:
                session.add(
                    SkillVersion(
                        skill_id=artifact.id,
                        version_label="query-hygiene-playbook-2026-10-05",
                        status="SUPPORTING_DOCUMENT",
                        scope_level="GLOBAL",
                        rule_kind="HEURISTIC",
                        content=text,
                        content_hash=digest,
                        source_path="skills/live-heat-scout/QUERY_HYGIENE_PLAYBOOK.md",
                        effective_from=now,
                        supersedes_version_id=None,
                        approval_state="IMPORTED",
                        dependencies=["live-heat-scout"],
                        created_at=now,
                    )
                )
                report.add(False)


def _skill_name(text: str, slug: str) -> str:
    for line in text.splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip()
    return slug


def _policies(session: Session, root: Path, program: Program, report: ImportReport) -> None:
    text = (root / "PRINCIPLES_VS_HEURISTICS.md").read_text(encoding="utf-8")
    section = ""
    index = 0
    now = utcnow()
    for line in text.splitlines():
        if line.startswith("## A."):
            section = "A"
            index = 0
            continue
        if line.startswith("## B."):
            section = "B"
            index = 0
            continue
        if line.startswith("## C."):
            section = "C"
            index = 0
            continue
        if line.startswith("## D."):
            section = "D"
            index = 0
            continue
        numbered = re.match(r"^(\d+)\.\s+(.*)", line)
        if section == "A" and numbered:
            index = int(numbered.group(1))
            body = numbered.group(2).strip()
            scope, scope_id, kind = "GLOBAL", None, "INVARIANT"
        elif line.startswith("- ") and section in {"B", "C"}:
            index += 1
            body = line[2:].strip()
            if section == "B":
                scope, scope_id, kind = "GLOBAL", None, "HEURISTIC"
            else:
                scope, scope_id, kind = "PROGRAM", program.id, "PREFERENCE"
        else:
            continue
        code = f"principles-{section.lower()}-{index:02d}"
        digest = sha256_text(body)
        existing = session.scalar(
            select(PolicyRule).where(PolicyRule.code == code, PolicyRule.content_hash == digest)
        )
        if existing:
            report.add(True)
            continue
        session.add(
            PolicyRule(
                code=code,
                scope_level=scope,
                scope_id=scope_id,
                rule_kind=kind,
                title=body[:180],
                text=body,
                status="active",
                source_path="PRINCIPLES_VS_HEURISTICS.md",
                content_hash=digest,
                effective_from=now,
                created_at=now,
            )
        )
        report.add(False)


def _target_creative(
    session: Session,
    root: Path,
    program: Program,
    campaign: Campaign,
    ecosystem: Ecosystem,
    report: ImportReport,
) -> Creative:
    creative = session.scalar(
        select(Creative).where(Creative.program_id == program.id, Creative.slug == "chore-stuff-target")
    )
    if creative is None:
        creative = Creative(
            program_id=program.id,
            campaign_id=campaign.id,
            ecosystem_id=ecosystem.id,
            slug="chore-stuff-target",
            name="SHE SAID IT WAS CHORE STUFF",
            status="produced",
            holdout=True,
            notes="Current Target benchmark. Produced v6, not posted. Hold out of generation context.",
            created_at=utcnow(),
        )
        session.add(creative)
        session.flush()
        report.add(False)
    lock = session.scalar(select(StoryLock).where(StoryLock.creative_id == creative.id))
    path = root / "story_locks/TARGET_chore_stuff_STORY_LOCK_current.md"
    raw = path.read_text(encoding="utf-8")
    document = parse_story_lock_markdown(raw)
    payload = document.model_dump(mode="json")
    digest = sha256_text(raw)
    if lock is None:
        lock = StoryLock(creative_id=creative.id, name=document.title, created_at=utcnow())
        session.add(lock)
        session.flush()
    existing = session.scalar(
        select(StoryLockVersion).where(
            StoryLockVersion.story_lock_id == lock.id,
            StoryLockVersion.source_hash == digest,
        )
    )
    if existing is None:
        version = StoryLockVersion(
            story_lock_id=lock.id,
            version_number=1,
            supersedes_version_id=None,
            content_json=payload,
            content_markdown=raw,
            content_hash=digest,
            change_reason="Imported current approved story lock from the 2026-10-05 handoff.",
            approved_by="Tyrel",
            source_path="story_locks/TARGET_chore_stuff_STORY_LOCK_current.md",
            source_hash=digest,
            created_at=utcnow(),
        )
        session.add(version)
        session.flush()
        creative.current_approved_story_lock_version_id = version.id
        session.add(
            ApprovalEvent(
                object_type="story_lock_version",
                object_id=lock.id,
                version_id=version.id,
                status="APPROVED",
                actor="Tyrel",
                notes="Handoff states the continuity update was Tyrel-approved on 2026-10-05.",
                previous_state=None,
                created_at=utcnow(),
            )
        )
        replace_version_projections(session, version, document, creative.id)
        _genome(session, creative, document, report)
        _mechanics(session, creative, document)
        _creative_policy(session, creative, root, report)
        report.add(False)
    else:
        if creative.current_approved_story_lock_version_id is None:
            creative.current_approved_story_lock_version_id = existing.id
        report.add(True)
    return creative


def _genome(session: Session, creative: Creative, document, report: ImportReport) -> None:
    existing = session.scalar(
        select(CreativeGenome).where(
            CreativeGenome.creative_id == creative.id,
            CreativeGenome.version_label == "import-2026-10-05",
        )
    )
    if existing:
        report.add(True)
        return
    genome = CreativeGenome(
        creative_id=creative.id,
        version_label="import-2026-10-05",
        created_at=utcnow(),
    )
    session.add(genome)
    session.flush()
    facets = [
        (
            "commerce_integration",
            document.commerce_relation or "UNKNOWN",
            "story lock COMMERCE RELATION",
        ),
        ("ecosystem", "TARGET", "story lock title names Target"),
        (
            "story_works_without_economics",
            "yes" if document.story_works_without_economics else "UNKNOWN",
            "story lock DOES STORY WORK WITHOUT ECONOMICS",
        ),
        ("hook_text", document.hook or "UNKNOWN", "story lock HOOK"),
        ("floating_hook", document.floating_hook or "UNKNOWN", "story lock floating hook"),
        ("label", document.label or "UNKNOWN", "story lock LABEL"),
        ("slide_count", str(len(document.slides) or 3), "continuity ledger headings"),
    ]
    for dimension, value, source in facets:
        if value == "UNKNOWN":
            continue
        session.add(
            GenomeFacet(
                genome_id=genome.id,
                dimension=dimension,
                value=value,
                source=source,
                assignment="human_set",
                confidence=None,
                created_at=utcnow(),
            )
        )
    report.add(False)


def _mechanics(session: Session, creative: Creative, document) -> None:
    observed = utcnow()
    rows = [
        ("hook_pattern", document.floating_hook or ""),
        ("commerce_integration", document.commerce_relation or ""),
        ("ecosystem", "TARGET"),
        ("proof_surface", "order_details"),
    ]
    for dimension, value in rows:
        if not value:
            continue
        session.add(
            MechanicObservation(
                creative_id=creative.id,
                dimension=dimension,
                value=value,
                observed_at=observed,
                source="story lock import",
            )
        )


def _creative_policy(session: Session, creative: Creative, root: Path, report: ImportReport) -> None:
    text = (root / "PRINCIPLES_VS_HEURISTICS.md").read_text(encoding="utf-8")
    section = text.split("## D.", 1)[-1].strip()
    digest = sha256_text(section)
    code = "principles-d-creative-lock-note"
    existing = session.scalar(
        select(PolicyRule).where(PolicyRule.code == code, PolicyRule.content_hash == digest)
    )
    if existing:
        report.add(True)
        return
    session.add(
        PolicyRule(
            code=code,
            scope_level="CREATIVE",
            scope_id=creative.id,
            rule_kind="LOCKED_VALUE",
            title="Creative-specific locks from principles section D",
            text=section,
            status="active",
            source_path="PRINCIPLES_VS_HEURISTICS.md",
            content_hash=digest,
            effective_from=utcnow(),
            created_at=utcnow(),
        )
    )
    report.add(False)


def _onions_creative(
    session: Session,
    program: Program,
    campaign: Campaign,
    ecosystem: Ecosystem,
    report: ImportReport,
) -> None:
    existing = session.scalar(
        select(Creative).where(Creative.program_id == program.id, Creative.slug == "onions-note-blank")
    )
    if existing:
        report.add(True)
        return
    creative = Creative(
        program_id=program.id,
        campaign_id=campaign.id,
        ecosystem_id=ecosystem.id,
        slug="onions-note-blank",
        name="THE ONIONS NOTE WAS BLANK",
        status="not_produced",
        holdout=True,
        notes=(
            "Locked structure only. Overlay: he said he copied my order exactly. "
            "Product: McDonald's Double Cheeseburger. Proof: structured No Diced Onions modifier is absent. "
            "No final amounts were stated, so none are stored."
        ),
        created_at=utcnow(),
    )
    session.add(creative)
    session.flush()
    report.add(False)


def _assets(
    session: Session,
    root: Path,
    creative: Creative,
    ecosystems: dict[str, Ecosystem],
    report: ImportReport,
) -> None:
    payload = json.loads((root / "ASSET_INDEX.json").read_text(encoding="utf-8"))
    version_id = creative.current_approved_story_lock_version_id
    for row in payload:
        original = row["path"]
        existing = session.scalar(select(Asset).where(Asset.original_path == original))
        if existing:
            report.add(True)
            continue
        role = row.get("role") or "REFERENCE"
        if row.get("type") == "dir" and role == "REFERENCE" and original.endswith("/"):
            bank = session.scalar(select(ReferenceBank).where(ReferenceBank.original_path == original))
            if bank is None:
                code = row.get("ecosystem")
                ecosystem = ecosystems.get(code) if isinstance(code, str) else None
                ecosystem_id = ecosystem.id if ecosystem is not None else None
                session.add(
                    ReferenceBank(
                        name=row.get("name") or original,
                        ecosystem_id=ecosystem_id,
                        original_path=original,
                        notes=row.get("notes") or None,
                    )
                )
        approved = row.get("approved")
        if approved == "unknown":
            approved_value = None
        else:
            approved_value = bool(approved) if approved is not None else None
        story_key = row.get("story_id")
        bind = None
        if (
            version_id
            and story_key == "chore_stuff_target"
            and row.get("stale") is False
            and role in {"EXAMPLE", "BASE", "INGREDIENT"}
        ):
            bind = version_id
        product_model = None
        lowered = original.lower()
        if "airpods5" in lowered or "airpods 5" in (row.get("name") or "").lower():
            product_model = "AirPods 5"
        session.add(
            Asset(
                creative_id=creative.id if story_key == "chore_stuff_target" else None,
                bound_story_lock_version_id=bind,
                name=row.get("name") or original.rsplit("/", 1)[-1],
                role=role,
                rights_status=_rights(original, row.get("name") or ""),
                original_path=original,
                storage_uri=None,
                content_hash=None,
                present_in_snapshot=False,
                source_exists_claim=bool(row.get("exists")) if "exists" in row else None,
                approved=approved_value,
                stale=bool(row.get("stale")),
                ecosystem_code=None
                if row.get("ecosystem") in {None, "BOTH", "GLOBAL"}
                else row.get("ecosystem"),
                story_key=story_key,
                product_model=product_model,
                notes=(row.get("notes") or "") + " Binary is not in the core snapshot."
                if row.get("type") in {"image", "dir"}
                else row.get("notes"),
                created_at=utcnow(),
            )
        )
        report.add(False)


def _rights(path: str, name: str) -> str:
    blob = f"{path} {name}".lower()
    if "ios-messages-keyboard" in blob or "user's own" in blob or "user's own" in name.lower():
        return "USER_OWNED"
    return "UNKNOWN"


def _benchmarks(session: Session, report: ImportReport) -> None:
    rows = [
        ("Brooke pink iPad / overslept", "Brooke", "WINNER", 2_300_000, "source text: 2.3M", False),
        ("Maria Chick-fil-A", "Maria", None, 338_200, "source text: 338.2K", False),
        ("Sarah MacBook", "Sarah", None, 150_500, "source text: 150.5K", False),
        ("Maria McChicken", "Maria", None, None, "UNKNOWN / NEEDS FOLLOW-UP", False),
        ("Brooke boyfriend pink-iPad sequel", "Brooke", "WEAK", None, "UNKNOWN", False),
        ("Sarah Dasher got nosy", "Sarah", "WEAK", None, "UNKNOWN", False),
        ("Cent post", None, "FAILURE", None, "did not travel", False),
        ("Lindy metadata joke", None, "FAILURE", None, "did not travel", False),
        ("Jenny screen recording", None, "FAILURE", None, "did not travel", False),
        ("SHE SAID IT WAS CHORE STUFF", None, "HOLDOUT", None, "not posted", True),
        ("THE ONIONS NOTE WAS BLANK", None, "HOLDOUT", None, "not produced", True),
    ]
    for name, account, category, views, note, holdout in rows:
        existing = session.scalar(select(BenchmarkCreative).where(BenchmarkCreative.name == name))
        if existing:
            report.add(True)
            continue
        session.add(
            BenchmarkCreative(
                name=name,
                account_name=account,
                category=category,
                ecosystem_code=None,
                views=views,
                lesson=note,
                holdout=holdout,
                source_path="BENCHMARKS.md",
                metrics_note=note,
            )
        )
        report.add(False)


def _regressions(session: Session, root: Path, report: ImportReport) -> None:
    payload = json.loads((root / "GOLDEN_REGRESSION_TESTS.json").read_text(encoding="utf-8"))
    for row in payload:
        digest = sha256_text(json.dumps(row, sort_keys=True))
        existing = session.scalar(select(RegressionTest).where(RegressionTest.code == row["id"]))
        if existing:
            report.add(True)
            continue
        session.add(
            RegressionTest(
                code=row["id"],
                category=row["category"],
                input_text=row["input"],
                expected_decision=row["expected_decision"],
                pass_conditions=row.get("pass_conditions") or [],
                fail_conditions=row.get("fail_conditions") or [],
                source_rule=row["source_rule"],
                evaluation_mode=evaluation_mode_for(row["id"]),
                content_hash=digest,
            )
        )
        report.add(False)


def _providers(session: Session, report: ImportReport) -> None:
    rows = [
        (
            "grok",
            "creative_reasoning",
            "UNKNOWN",
            "Historical creative-intelligence provider. Not coupled to the core.",
        ),
        (
            "chatgpt-web",
            "image_editing",
            "UNKNOWN",
            "Historical image editor. Model version was not recorded.",
        ),
        (
            "scrapecreators",
            "research",
            "UNKNOWN",
            "Optional TikTok research API. No secret stored.",
        ),
        ("apify", "research", "UNKNOWN", "Optional TikTok research test. No secret stored."),
        (
            "pinterest",
            "visual_search",
            "UNKNOWN",
            "Pins are reference-only unless rights are cleared.",
        ),
    ]
    for name, capability, version, notes in rows:
        existing = session.scalar(
            select(ModelProvider).where(
                ModelProvider.name == name,
                ModelProvider.capability == capability,
            )
        )
        if existing:
            report.add(True)
            continue
        session.add(
            ModelProvider(
                name=name,
                capability=capability,
                model_name=None,
                model_version=version,
                notes=notes,
            )
        )
        report.add(False)


def _dna(session: Session, accounts: dict[str, Account], report: ImportReport) -> None:
    specs = {
        "maria": [
            ("content_lane", "food and couples", "HUMAN_SET_CONSTRAINT", None, None),
            ("recurring_relationship", "Dre as boyfriend", "HUMAN_SET_CONSTRAINT", None, None),
            (
                "post_views",
                "338200",
                "HISTORICAL_OBSERVATION",
                1,
                "Chick-fil-A post stated as 338.2K",
            ),
        ],
        "sarah": [
            ("content_lane", "electronics", "HUMAN_SET_CONSTRAINT", None, None),
            ("post_views", "150500", "HISTORICAL_OBSERVATION", 1, "MacBook post stated as 150.5K"),
        ],
        "brooke": [
            ("content_lane", "electronics", "HUMAN_SET_CONSTRAINT", None, None),
            ("post_views", "2300000", "HISTORICAL_OBSERVATION", 1, "Pink iPad post stated as 2.3M"),
        ],
    }
    for slug, observations in specs.items():
        account = accounts[slug]
        profile = session.scalar(
            select(AccountDnaProfile).where(
                AccountDnaProfile.account_id == account.id,
                AccountDnaProfile.version_number == 1,
            )
        )
        if profile:
            report.add(True)
            continue
        profile = AccountDnaProfile(
            account_id=account.id,
            version_number=1,
            supersedes_profile_id=None,
            created_at=utcnow(),
        )
        session.add(profile)
        session.flush()
        for field_name, value, kind, sample, notes in observations:
            session.add(
                AccountDnaObservation(
                    profile_id=profile.id,
                    field_name=field_name,
                    value=value,
                    evidence_kind=kind,
                    confidence=None,
                    sample_size=sample,
                    date_start=None,
                    date_end=None,
                    source_path="ACCOUNT_STATE_TODAY.md",
                    notes=notes,
                    created_at=utcnow(),
                )
            )
        report.add(False)
