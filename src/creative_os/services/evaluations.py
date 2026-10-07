"""Import the external manual model-transfer scores. These rows are not ModelRuns."""

import json
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from creative_os.config import repo_root
from creative_os.models import ManualEvaluation

ORIGIN = "EXTERNAL_MANUAL_EVALUATION"
RECORDED_AT = datetime(2026, 10, 6, 20, 50, tzinfo=UTC)

TARGET_ITEMS = {
    "preserves_good_decisions": 2,
    "story_before_commerce": 2,
    "human_causality": 2,
    "specific_stakes": 2,
    "comment_doors": 2,
    "viral_texture": 2,
    "secondary_inspection": 2,
    "commerce_integration": 2,
    "proof_boundary": 2,
    "continuity": 2,
    "retailer_language": 2,
    "basket_padding": 2,
    "production_ready_judgment": 2,
}
MARIA_GROK = {
    "account_fit": 2,
    "age_world": 2,
    "novelty": 1,
    "story_native_commerce": 2,
    "comment_doors": 2,
    "viral_texture": 2,
    "research_flags": 2,
    "economics": 2,
    "proof_surface": 2,
}
MARIA_GPT = {
    "account_fit": 1,
    "age_world": 2,
    "novelty": 2,
    "story_native_commerce": 2,
    "comment_doors": 2,
    "viral_texture": 2,
    "research_flags": 2,
    "economics": 2,
    "proof_surface": 2,
}


def import_manual_evaluations(session: Session, root: Path | None = None) -> int:
    directory = (root or repo_root()) / "evaluation/model_transfer_v1"
    runs = directory / "runs"
    specs = (
        (
            "grok",
            "Grok 4.7",
            "target_story_development_packet.json",
            "grok_target_audit.json",
            "STORY_DEVELOPMENT",
            "26/26",
            TARGET_ITEMS,
            "READY. One stale AirPods 4 TCIN cleared as a recommended patch, not applied by the model.",
        ),
        (
            "gpt",
            "GPT-5.6 Terra",
            "target_story_development_packet.json",
            "gpt_target_audit.json",
            "STORY_DEVELOPMENT",
            "26/26",
            TARGET_ITEMS,
            "READY. No story rewrite. Did not mention the stale TCIN.",
        ),
        (
            "grok",
            "Grok 4.7",
            "maria_concept_generation_packet.json",
            "grok_maria_concepts.json",
            "CONCEPT_GENERATION",
            "17/18",
            MARIA_GROK,
            "Account-specific, including Dre. Three concepts share claim-versus-order-surface.",
        ),
        (
            "gpt",
            "GPT-5.6 Terra",
            "maria_concept_generation_packet.json",
            "gpt_maria_concepts.json",
            "CONCEPT_GENERATION",
            "17/18",
            MARIA_GPT,
            "Wider premise shapes. Boyfriend stays unnamed, so Dre is not bound.",
        ),
    )
    inserted = 0
    for provider, model, packet_name, output_name, stage, score, items, notes in specs:
        packet = json.loads((directory / packet_name).read_text(encoding="utf-8"))
        output = json.loads((runs / output_name).read_text(encoding="utf-8"))
        existing = session.scalar(
            select(ManualEvaluation).where(
                ManualEvaluation.provider_name == provider,
                ManualEvaluation.model_name == model,
                ManualEvaluation.packet_hash == packet["bundle_hash"],
                ManualEvaluation.stage == stage,
            )
        )
        if existing is not None:
            continue
        task = (packet.get("packet") or {}).get("task") or {}
        session.add(
            ManualEvaluation(
                origin=ORIGIN,
                provider_name=provider,
                model_name=model,
                packet_hash=packet["bundle_hash"],
                recorded_context_bundle_id=packet.get("bundle_id"),
                recorded_task_id=packet.get("creative_task_id"),
                stage=stage,
                task_instruction=str(task.get("instruction") or ""),
                output_json=output,
                rubric_score=score,
                rubric_item_scores=items,
                notes=notes,
                run_timestamp=RECORDED_AT,
                source_path=f"evaluation/model_transfer_v1/runs/{output_name}",
            )
        )
        inserted += 1
    session.flush()
    return inserted
