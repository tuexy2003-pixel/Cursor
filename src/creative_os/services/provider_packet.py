"""Provider-neutral packet text. This does not call a model."""

import json
from typing import Any

from creative_os.models import ContextBundle
from creative_os.util import ensure_utc

SECTION_ORDER = (
    "task",
    "invariants",
    "policies",
    "skills",
    "story_lock",
    "dna",
    "genome",
    "benchmarks",
    "mechanics",
    "references",
    "other",
)


def render_sections(payload: dict[str, Any]) -> dict[str, str]:
    sections = {
        "task": _task_section(payload),
        "invariants": _policy_section("GLOBAL INVARIANTS", payload.get("global_invariants") or []),
        "policies": "\n\n".join(
            part
            for part in (
                _policy_section("PROGRAM POLICIES", payload.get("program_policies") or []),
                _policy_section("ACCOUNT POLICIES", payload.get("account_policies") or []),
                _policy_section("CAMPAIGN POLICIES", payload.get("campaign_policies") or []),
                _policy_section("CREATIVE LOCKS", payload.get("creative_locks") or []),
            )
            if part
        ),
        "skills": _skills_section(
            payload.get("skill_versions") or [], payload.get("skill_dependency_audit") or []
        ),
        "story_lock": _story_lock_section(payload),
        "dna": _dna_section(payload.get("account_dna")),
        "genome": _genome_section(payload.get("creative_genome"), payload.get("genome_state")),
        "benchmarks": _benchmarks_section(payload.get("benchmarks") or []),
        "mechanics": _json_block("MECHANIC HISTORY", payload.get("mechanic_context")),
        "references": _references_section(payload.get("references") or [], payload.get("assets") or []),
        "other": _other_section(payload),
    }
    return sections


def render_context_text(payload: dict[str, Any]) -> str:
    sections = render_sections(payload)
    chunks = [
        "# Creative OS provider packet",
        "PROVIDER_EXECUTION: NOT_IMPLEMENTED",
        "Use only this packet. Do not search the web. Do not mutate stored creative truth.",
        f"COMPILER: {payload.get('compiler_version')}",
        f"AS_OF: {payload.get('as_of')}",
        f"STAGE: {payload.get('requested_stage')}",
        "",
    ]
    for name in SECTION_ORDER:
        body = sections.get(name) or ""
        if not body.strip():
            continue
        chunks.append(body.strip())
        chunks.append("")
    sizes = payload.get("section_sizes") or {}
    if sizes:
        chunks.append("## SECTION SIZES")
        for name in SECTION_ORDER:
            row = sizes.get(name) or {}
            chunks.append(
                f"- {name}: {row.get('characters', 0)} characters, "
                f"token estimate {row.get('token_estimate', 0)}"
            )
    return "\n".join(chunks).strip() + "\n"


def section_sizes(sections: dict[str, str]) -> dict[str, dict[str, int]]:
    sizes: dict[str, dict[str, int]] = {}
    for name in SECTION_ORDER:
        text = sections.get(name) or ""
        sizes[name] = {
            "characters": len(text),
            "token_estimate": len(text) // 4,
        }
    return sizes


def packet_document(bundle: ContextBundle) -> dict[str, Any]:
    return {
        "bundle_id": bundle.id,
        "bundle_hash": bundle.payload_hash,
        "provider_execution": "NOT_IMPLEMENTED",
        "compiler_version": bundle.compiler_version,
        "as_of": ensure_utc(bundle.as_of).isoformat(),
        "requested_stage": bundle.requested_stage,
        "creative_task_id": bundle.creative_task_id,
        "packet": bundle.compiled_payload,
        "compiled_text": bundle.compiled_text,
    }


def _task_section(payload: dict[str, Any]) -> str:
    task = payload.get("task") or {}
    contract = payload.get("output_contract") or {}
    lines = ["## TASK", task.get("instruction") or "No task instruction was frozen."]
    if task:
        lines.append(f"Task id: {task.get('id')}")
        lines.append(f"Stage: {task.get('stage')}")
        lines.append(f"Status: {task.get('status')}")
        lines.append(f"Expected output: {task.get('expected_output_type')}")
        lines.append("Constraints:")
        lines.append(_pretty(task.get("constraints") or {}))
        lines.append("Input refs:")
        lines.append(_pretty(task.get("input_refs") or {}))
    if contract:
        lines.append("")
        lines.append(f"## OUTPUT CONTRACT {contract.get('name')}")
        lines.append(contract.get("instructions") or "")
        lines.append(_pretty(contract.get("json_schema") or {}))
    return "\n".join(lines)


def _policy_section(title: str, items: list[dict[str, Any]]) -> str:
    if not items:
        return ""
    lines = [f"## {title}"]
    for item in items:
        lines.append(f"### {item.get('code')} ({item.get('scope')} {item.get('rule_kind')})")
        lines.append(
            f"version {item.get('version')} priority {item.get('priority')} authority {item.get('authority')}"
        )
        lines.append(f"Included because: {item.get('reason_included')}")
        lines.append(item.get("text") or "")
        lines.append("")
    return "\n".join(lines).strip()


def _skills_section(skills: list[dict[str, Any]], audit: list[dict[str, Any]]) -> str:
    lines = ["## SKILLS"]
    if not skills:
        lines.append("No skill text was selected for this stage.")
    for skill in skills:
        lines.append(f"### {skill.get('slug')} role {skill.get('skill_role')}")
        lines.append(
            f"version {skill.get('version')} id {skill.get('version_id')} hash {skill.get('content_hash')}"
        )
        lines.append(f"Included because: {skill.get('reason_included')}")
        lines.append(skill.get("content") or "")
        lines.append("")
    if audit:
        lines.append("### SKILL DEPENDENCY AUDIT")
        lines.append(_pretty(audit))
    return "\n".join(lines).strip()


def _story_lock_section(payload: dict[str, Any]) -> str:
    lock = payload.get("current_story_lock_version")
    lines = ["## CURRENT STORY LOCK"]
    if not lock:
        lines.append("No current approved StoryLock is in scope.")
        return "\n".join(lines)
    lines.append(
        f"version {lock.get('version_number')} id {lock.get('id')} document_hash {lock.get('document_hash')}"
    )
    lines.append(lock.get("markdown") or "")
    lines.append("")
    lines.append("### STORY LOCK DOCUMENT")
    lines.append(_pretty(lock.get("document") or {}))
    return "\n".join(lines)


def _dna_section(dna: dict[str, Any] | None) -> str:
    lines = ["## ACCOUNT DNA"]
    if not dna:
        lines.append("No approved Account DNA profile is in scope.")
        return "\n".join(lines)
    lines.append(
        f"profile {dna.get('profile_id')} version {dna.get('version')} "
        f"origin {dna.get('origin')} approval {dna.get('approval_state')}"
    )
    lines.append(f"Included because: {dna.get('reason_included')}")
    for row in dna.get("observations") or []:
        lines.append(
            f"- {row.get('field_name')} = {row.get('value')} "
            f"[{row.get('evidence_kind')}] confidence {row.get('confidence')} "
            f"sample {row.get('sample_size')} dates {row.get('date_start')}..{row.get('date_end')} "
            f"source {row.get('source_path')}"
        )
        if row.get("notes"):
            lines.append(f"  notes: {row.get('notes')}")
    return "\n".join(lines)


def _genome_section(genome: dict[str, Any] | None, state: str | None) -> str:
    lines = ["## CREATIVE GENOME", f"state: {state or 'NONE'}"]
    if not genome:
        return "\n".join(lines)
    lines.append(
        f"id {genome.get('id')} version {genome.get('version')} origin {genome.get('origin')} "
        f"approval {genome.get('approval_state')} story_lock {genome.get('source_story_lock_version_id')}"
    )
    for facet in genome.get("facets") or []:
        lines.append(
            f"- {facet.get('dimension')} = {facet.get('value')} "
            f"assignment {facet.get('assignment')} confidence {facet.get('confidence')} "
            f"source {facet.get('source')}"
        )
    return "\n".join(lines)


def _benchmarks_section(rows: list[dict[str, Any]]) -> str:
    lines = ["## BENCHMARKS"]
    if not rows:
        lines.append("No non-holdout benchmarks were selected.")
        return "\n".join(lines)
    for row in rows:
        lines.append(f"### {row.get('name')}")
        lines.append(
            f"account {row.get('account')} category {row.get('category')} "
            f"ecosystem {row.get('ecosystem')} holdout {row.get('holdout')}"
        )
        lines.append(
            f"metrics views {row.get('views')} likes {row.get('likes')} "
            f"comments {row.get('comments')} shares {row.get('shares')} saves {row.get('saves')}"
        )
        lines.append(f"lesson: {row.get('lesson')}")
        lines.append(f"metrics note: {row.get('metrics_note')}")
        lines.append(f"Included because: {row.get('reason_included')}")
        lines.append(f"source: {row.get('source')}")
        lines.append("")
    return "\n".join(lines).strip()


def _references_section(references: list[dict[str, Any]], assets: list[dict[str, Any]]) -> str:
    lines = ["## REFERENCES AND ASSET METADATA"]
    if not references and not assets:
        lines.append("No visual reference metadata was selected for this stage.")
        return "\n".join(lines)
    for row in references:
        lines.append(
            f"- reference {row.get('name')} source {row.get('source')} because {row.get('reason_included')}"
        )
    for row in assets:
        lines.append(
            f"- asset {row.get('name')} role {row.get('role')} rights {row.get('rights_status')} "
            f"stale {row.get('staleness_state')} product {row.get('product_model')} "
            f"{row.get('width')}x{row.get('height')} path {row.get('original_path')} "
            f"story {row.get('story_key')} because {row.get('reason_included')}"
        )
    return "\n".join(lines)


def _other_section(payload: dict[str, Any]) -> str:
    lines = ["## SCOPE", _pretty(payload.get("scope") or {})]
    concept = payload.get("selected_concept")
    lines.append("")
    lines.append("## SELECTED CONCEPT")
    lines.append(_pretty(concept) if concept else "No selected concept is linked.")
    lines.append("")
    lines.append("## COMMENT DOORS")
    lines.append(_pretty(payload.get("comment_doors") or []))
    lines.append("")
    lines.append("## CONTINUITY")
    lines.append(_pretty(payload.get("continuity") or []))
    lines.append("")
    lines.append("## EXCLUSIONS")
    lines.append(_pretty(payload.get("excluded_for_token_budget") or []))
    coverage = payload.get("skill_coverage")
    if coverage:
        lines.append("")
        lines.append(f"SKILL COVERAGE: {coverage}")
    return "\n".join(lines)


def _json_block(title: str, value: Any) -> str:
    return f"## {title}\n{_pretty(value)}"


def _pretty(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2)
