"""Build the v0.3 manual model-transfer packets. This does not call a provider."""

from datetime import datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from creative_os.models import Account, ContextBundle, Creative, Ecosystem, Program
from creative_os.services.context_bundles import create_context_bundle
from creative_os.services.provider_packet import packet_document
from creative_os.services.tasks import create_creative_task
from creative_os.util import ensure_utc

TARGET_INSTRUCTION = """
Audit the current story as a creative director.
Determine whether the narrative is production-ready.
Preserve strong existing decisions.
Identify only meaningful remaining story-level weaknesses.
Do not redesign it simply to be different.
Do not inspect image pixels. This test is narrative and system transfer only.
""".strip()

MARIA_INSTRUCTION = """
Generate 5 NEW staged short-form carousel concepts appropriate for this account
using the current creative operating system.

Requirements:
- new concepts, not copies of benchmarks
- story-native commerce
- roughly 15–20 life-world where current account or program policy says so
- believable human causality
- multiple potential comment doors
- do not pad baskets for economics
- commerce and economic discovery should follow current policy
- do not search the web in this manual evaluation
- flag research needed instead

Do not create a Creative or a StoryLock. These concepts are proposals for human review.
""".strip()


def build_transfer_bundles(session: Session, as_of: datetime) -> tuple[ContextBundle, ContextBundle]:
    moment = ensure_utc(as_of)
    program = session.scalar(select(Program).where(Program.slug == "mydashperks"))
    target = session.scalar(select(Creative).where(Creative.slug == "chore-stuff-target"))
    maria = session.scalar(select(Account).where(Account.slug == "maria"))
    doordash = session.scalar(select(Ecosystem).where(Ecosystem.code == "DOORDASH"))
    if program is None or target is None or maria is None or doordash is None:
        raise RuntimeError("model-transfer packets require the imported handoff")
    story_task = create_creative_task(
        session,
        program_id=target.program_id,
        account_id=target.account_id,
        campaign_id=target.campaign_id,
        creative_id=target.id,
        ecosystem_id=target.ecosystem_id,
        stage="STORY_DEVELOPMENT",
        instruction=TARGET_INSTRUCTION,
        created_by="operator",
        expected_output_type="STORY_DEVELOPMENT_AUDIT",
        notes="Manual model-transfer evaluation. Does not mutate the Target creative.",
    )
    concept_task = create_creative_task(
        session,
        program_id=program.id,
        account_id=maria.id,
        ecosystem_id=doordash.id,
        stage="CONCEPT_GENERATION",
        instruction=MARIA_INSTRUCTION,
        created_by="operator",
        expected_output_type="CONCEPT_GENERATION",
        notes="Evaluation task only. No creative is created.",
    )
    story = create_context_bundle(session, target, task=story_task, as_of=moment, heuristic_budget=24)
    concepts = create_context_bundle(session, None, task=concept_task, as_of=moment, heuristic_budget=24)
    return story, concepts


def write_transfer_packets(directory: Path, story: ContextBundle, concepts: ContextBundle) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    _write(directory / "target_story_development_packet.md", story.compiled_text)
    _write(directory / "target_story_development_packet.json", _json(story))
    _write(directory / "maria_concept_generation_packet.md", concepts.compiled_text)
    _write(directory / "maria_concept_generation_packet.json", _json(concepts))


def _json(bundle: ContextBundle) -> str:
    import json

    return json.dumps(packet_document(bundle), indent=2, ensure_ascii=False) + "\n"


def _write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
