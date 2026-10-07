import re

from creative_os.schemas.story_lock import StoryLockDocument
from creative_os.services.canonical import canonical_json


def render_story_lock_markdown(document: StoryLockDocument) -> str:
    lines = [f"# STORY LOCK — {document.title}", ""]
    if document.label:
        lines.append(f"LABEL: {document.label}")
    if document.core_story:
        lines.append(f"CORE STORY: {document.core_story}")
    if document.hook:
        lines.append(f"HOOK: {document.hook}")
    if document.floating_hook:
        lines.append(f"FLOATING HOOK: {document.floating_hook}")
    if document.stakes:
        lines.append(f"STAKES: {document.stakes}")
    if document.trigger:
        lines.append(f"TRIGGER: {document.trigger}")
    if document.action:
        lines.append(f"ACTION: {document.action}")
    if document.expected_next_beat:
        lines.append(f"EXPECTED NEXT BEAT: {document.expected_next_beat}")
    if document.reveal:
        lines.append(f"REVEAL: {document.reveal}")
    if document.story_date or document.story_weekday:
        weekday = document.story_weekday or ""
        date = document.story_date or ""
        lines.append(f"STORY DATE: {weekday} {date}".strip())
    if document.dialogue:
        lines.append("")
        lines.append("DIALOGUE:")
        for turn in document.dialogue:
            direction = f" ({turn.direction})" if turn.direction else ""
            lines.append(f"- {turn.speaker}{direction}: {turn.text}")
    if document.line_items:
        lines.append("")
        lines.append("LINE ITEMS:")
        for item in document.line_items:
            price = f" — ${item.unit_price}" if item.unit_price else ""
            lines.append(f"{item.position}. {item.title}{price}")
    if document.economics:
        eco = document.economics
        lines.append("")
        lines.append("ECONOMICS:")
        if eco.discount_label:
            lines.append(f"- discount label: {eco.discount_label}")
        lines.append(f"- subtotal: {eco.subtotal}")
        lines.append(f"- discount: {eco.discount}")
        lines.append(f"- tax: {eco.tax}")
        lines.append(f"- total: {eco.total}")
        if eco.staged is not None:
            lines.append(f"- staged: {eco.staged}")
    if document.comment_doors:
        lines.append("")
        lines.append("COMMENT DOORS:")
        for door in document.comment_doors:
            lines.append(f"- ({door.kind}) {door.text}")
    if document.slides:
        lines.append("")
        lines.append("SLIDES:")
        for slide in document.slides:
            lines.append(
                f"- S{slide.index}: beat={slide.beat or ''}; clock={slide.visible_clock or ''}; "
                f"date={slide.visible_date or ''}; overlay={slide.overlay or ''}"
            )
    if document.stale_notes:
        lines.append("")
        lines.append("STALE NOTES:")
        for note in document.stale_notes:
            lines.append(f"- {note}")
    if document.extra:
        lines.append("")
        lines.append("UNPARSED SOURCE EXCERPTS:")
        for key, value in document.extra.items():
            lines.append(f"## {key}")
            lines.append(value)
    lines.append("")
    return "\n".join(lines)


def _cell(value: object) -> str:
    if value is None:
        return ""
    return str(value).replace("\n", "\\n").replace("|", "/")


def render_canonical_markdown(document: StoryLockDocument) -> str:
    """Human-readable export plus a canonical JSON block that round-trips."""
    lines = [f"# STORY LOCK — {document.title}", "FORMAT: canonical-v2", ""]
    lines.append(f"LABEL: {document.label or ''}")
    lines.append(f"CORE STORY: {document.core_story or ''}")
    lines.append(f"HOOK: {document.hook or ''}")
    lines.append(f"FLOATING HOOK: {document.floating_hook or ''}")
    lines.append(f"STAKES: {document.stakes or ''}")
    lines.append(f"TRIGGER: {document.trigger or ''}")
    lines.append(f"ACTION: {document.action or ''}")
    lines.append(f"EXPECTED NEXT BEAT: {document.expected_next_beat or ''}")
    lines.append(f"REVEAL: {document.reveal or ''}")
    lines.append(f"COMMERCE RELATION: {document.commerce_relation or ''}")
    works = (
        ""
        if document.story_works_without_economics is None
        else str(document.story_works_without_economics).lower()
    )
    lines.append(f"STORY WORKS WITHOUT ECONOMICS: {works}")
    lines.append(f"STORY DATE: {document.story_date or ''}")
    lines.append(f"STORY WEEKDAY: {document.story_weekday or ''}")
    lines.append("")
    lines.append("DIALOGUE:")
    for turn in document.dialogue:
        lines.append(f"- {_cell(turn.speaker)} | {_cell(turn.direction)} | {_cell(turn.text)}")
    lines.append("")
    lines.append("LINE ITEMS:")
    for item in document.line_items:
        lines.append(
            "- "
            + " | ".join(
                _cell(part)
                for part in (
                    item.position,
                    item.title,
                    item.quantity,
                    item.unit_price,
                    item.model,
                    item.generation,
                    item.variant,
                    item.color,
                    item.pack_count,
                    item.external_id,
                )
            )
        )
    lines.append("")
    lines.append("ECONOMICS:")
    eco = document.economics
    lines.append(f"- subtotal: {'' if eco is None else eco.subtotal or ''}")
    lines.append(f"- discount: {'' if eco is None else eco.discount or ''}")
    lines.append(f"- discount_label: {'' if eco is None else eco.discount_label or ''}")
    lines.append(f"- tax: {'' if eco is None else eco.tax or ''}")
    lines.append(f"- total: {'' if eco is None else eco.total or ''}")
    staged = "" if eco is None or eco.staged is None else str(eco.staged).lower()
    lines.append(f"- staged: {staged}")
    lines.append(f"- notes: {'' if eco is None else eco.notes or ''}")
    lines.append("")
    lines.append("SLIDES:")
    for slide in document.slides:
        lines.append(
            "- "
            + " | ".join(
                _cell(part)
                for part in (
                    slide.index,
                    slide.beat,
                    slide.relative_time,
                    slide.visible_clock,
                    slide.visible_date,
                    slide.overlay,
                    slide.order_state,
                    slide.actor_knowledge,
                    slide.actor_location,
                )
            )
        )
    lines.append("")
    lines.append("CONTINUITY:")
    for fact in document.continuity:
        lines.append(f"- {_cell(fact.slide_index)} | {_cell(fact.field)} | {_cell(fact.value)}")
    lines.append("")
    lines.append("COMMENT DOORS:")
    for door in document.comment_doors:
        lines.append(f"- {_cell(door.kind)} | {_cell(door.text)}")
    lines.append("")
    lines.append("VIRAL TEXTURE:")
    for detail in document.viral_texture:
        lines.append(f"- {_cell(detail.slide_index)} | {_cell(detail.text)} | {_cell(detail.category)}")
    lines.append("")
    lines.append("STALE NOTES:")
    for note in document.stale_notes:
        lines.append(f"- {note}")
    lines.append("")
    lines.append("```json canonical")
    lines.append(canonical_json(document))
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def parse_canonical_markdown(text: str) -> StoryLockDocument:
    match = re.search(r"```json canonical\n(.*?)\n```", text, re.DOTALL)
    if match is None:
        raise ValueError("canonical story lock markdown is missing its structured block")
    return StoryLockDocument.model_validate_json(match.group(1))
