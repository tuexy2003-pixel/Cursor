import re
from datetime import date

from creative_os.schemas.story_lock import (
    CommentDoorDocument,
    ContinuityFact,
    DialogueTurn,
    Economics,
    LineItem,
    SlideDocument,
    StoryLockDocument,
    TextureDetail,
)

_MONTHS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


def parse_story_lock_markdown(text: str) -> StoryLockDocument:
    """Parse the current story-lock dialect. Unrecognized prose stays in extra, not invented fields."""
    lines = text.splitlines()
    title = "UNKNOWN"
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        title = re.sub(r"^STORY LOCK —\s*", "", title)

    def field(label: str) -> str | None:
        pattern = re.compile(rf"^{re.escape(label)}:\s*(.+)$", re.IGNORECASE)
        for line in lines:
            match = pattern.match(line.strip())
            if match:
                return match.group(1).strip()
        return None

    floating = None
    for line in lines:
        if "FLOATING HOOK" in line and "LOCKED" in line:
            quoted = re.search(r'"([^"]+)"', line)
            if quoted:
                floating = quoted.group(1)
            break

    dialogue: list[DialogueTurn] = []
    in_dialogue = False
    for line in lines:
        if line.startswith("S1 DIALOGUE"):
            in_dialogue = True
            continue
        if in_dialogue:
            if not line.startswith("  "):
                in_dialogue = False
                continue
            match = re.match(r"\s+([^:]+?)\s+\((incoming|outgoing)\):\s+(.+)$", line)
            if match:
                dialogue.append(
                    DialogueTurn(
                        speaker=match.group(1).strip(),
                        direction=match.group(2),
                        text=match.group(3).strip(),
                    )
                )

    items: list[LineItem] = []
    in_items = False
    for line in lines:
        if line.startswith("S2 LOCKED ITEMS"):
            in_items = True
            continue
        if in_items:
            if line.startswith("S2 LOCKED MATH") or (line and not line.startswith(" ")):
                if not line.startswith(" "):
                    in_items = False
                if line.startswith("S2 LOCKED MATH"):
                    in_items = False
                continue
            match = re.match(r"\s+(\d+)\.\s+(.+?)\s+—\s+\$([0-9.]+)", line)
            if not match:
                continue
            raw_title = match.group(2).strip()
            title_main = re.sub(r"\s+\(.*\)$", "", raw_title).strip()
            generation = None
            model = None
            airpods = re.search(r"(AirPods)\s+(\d+)", title_main, re.IGNORECASE)
            if airpods:
                model = f"AirPods {airpods.group(2)}"
                generation = airpods.group(2)
            pack = re.search(r"(\d+)\s*ct", title_main, re.IGNORECASE)
            external = re.search(r"TCIN\s+(\d+)", line)
            items.append(
                LineItem(
                    position=int(match.group(1)),
                    title=title_main,
                    unit_price=match.group(3),
                    model=model,
                    generation=generation,
                    pack_count=int(pack.group(1)) if pack else None,
                    external_id=external.group(1) if external else None,
                )
            )

    economics = _economics(lines)
    story_date, story_weekday = _story_date(field("STORY DATE"))
    doors = _doors(lines)
    texture = _texture(lines)
    stale = _stale(lines)
    slides, continuity = _ledger(lines)
    beats = _beats(lines)
    for slide in slides:
        if slide.index in beats and not slide.beat:
            slide.beat = beats[slide.index]

    label = None
    for line in lines:
        if line.startswith("LABEL:"):
            label = line.split(":", 1)[1].strip()
            break

    works = None
    works_raw = field("DOES STORY WORK WITHOUT ECONOMICS")
    if works_raw:
        works = works_raw.strip().upper().startswith("YES")

    return StoryLockDocument(
        title=title,
        label=label,
        core_story=field("CORE STORY"),
        hook=_clean_hook(field("HOOK")),
        floating_hook=floating,
        stakes=field("STAKES"),
        trigger=field("TRIGGER / PROVOCATION"),
        action=field("ACTION"),
        expected_next_beat=field("EXPECTED NEXT BEAT"),
        reveal=field("REVEAL / PAYOFF"),
        commerce_relation=field("COMMERCE RELATION"),
        story_works_without_economics=works,
        dialogue=dialogue,
        line_items=items,
        economics=economics,
        story_date=story_date,
        story_weekday=story_weekday,
        slides=slides,
        continuity=continuity,
        comment_doors=doors,
        viral_texture=texture,
        stale_notes=stale,
        extra={},
    )


def _clean_hook(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip().strip('"')


def _economics(lines: list[str]) -> Economics | None:
    subtotal = discount = tax = total = label = None
    in_math = False
    for line in lines:
        if line.startswith("S2 LOCKED MATH"):
            in_math = True
            continue
        if in_math and line.startswith("PRIMARY"):
            break
        if not in_math:
            continue
        if "Subtotal" in line:
            subtotal = _money(line)
        elif "Discount" in line and "$" in line:
            label_match = re.match(r"\s+(.+?)\s+-", line)
            if label_match:
                label = label_match.group(1).strip()
            amount = _money(line)
            if amount is not None:
                discount = amount[1:] if amount.startswith("-") else amount
        elif line.strip().startswith("Tax"):
            tax = _money(line)
        elif line.strip().startswith("Total"):
            total = _money(line)
    if not any([subtotal, discount, tax, total]):
        return None
    return Economics(
        subtotal=subtotal,
        discount=discount,
        discount_label=label,
        tax=tax,
        total=total,
        staged=True,
        notes="Parsed from the story lock economics block. Staged when the lock says so.",
    )


def _money(line: str) -> str | None:
    match = re.search(r"-?\$([0-9]+\.[0-9]{2})", line)
    if not match:
        return None
    sign = "-" if "-$" in line.replace(" ", "") or re.search(r"-\s*\$", line) else ""
    return f"{sign}{match.group(1)}"


def _story_date(raw: str | None) -> tuple[str | None, str | None]:
    if not raw:
        return None, None
    match = re.search(
        r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+"
        r"([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})",
        raw,
    )
    if not match:
        return None, None
    weekday = match.group(1)
    month = _MONTHS.get(match.group(2)[:3].lower())
    if month is None:
        return None, weekday
    parsed = date(int(match.group(4)), month, int(match.group(3)))
    return parsed.isoformat(), weekday


def _doors(lines: list[str]) -> list[CommentDoorDocument]:
    doors: list[CommentDoorDocument] = []
    for line in lines:
        if line.startswith("PRIMARY COMMENT DOOR:"):
            doors.append(CommentDoorDocument(kind="primary", text=line.split(":", 1)[1].strip()))
        elif line.startswith("SECONDARY COMMENT DOORS:"):
            rest = line.split(":", 1)[1]
            for part in rest.split("/"):
                text = part.strip()
                if text:
                    doors.append(CommentDoorDocument(kind="secondary", text=text))
    return doors


def _texture(lines: list[str]) -> list[TextureDetail]:
    details: list[TextureDetail] = []
    current: int | None = None
    in_block = False
    for line in lines:
        if line.startswith("APPROVED MICRO-DETAILS"):
            in_block = True
            continue
        if in_block and line.startswith("S2 LOCKED"):
            break
        if not in_block:
            continue
        slide = re.match(r"\s+S(\d+)\s+—\s+(.*)", line)
        if slide:
            current = int(slide.group(1))
            chunk = slide.group(2).strip()
            if chunk:
                details.append(TextureDetail(slide_index=current, text=chunk, category=None))
    return details


def _stale(lines: list[str]) -> list[str]:
    notes: list[str] = []
    in_block = False
    for line in lines:
        if line.startswith("STALE ASSETS"):
            in_block = True
            continue
        if in_block and line.startswith("NEXT REPRODUCTION"):
            break
        if in_block and "STALE" in line:
            notes.append(line.strip())
    return notes


def _beats(lines: list[str]) -> dict[int, str]:
    beats: dict[int, str] = {}
    in_block = False
    for line in lines:
        if line.startswith("SLIDE-BY-SLIDE"):
            in_block = True
            continue
        if in_block and line.startswith("APPROVED"):
            break
        match = re.match(r"\s+S(\d+)\s+—\s+(.*)", line)
        if in_block and match:
            beats[int(match.group(1))] = match.group(2).strip()
    return beats


def _ledger(lines: list[str]) -> tuple[list[SlideDocument], list[ContinuityFact]]:
    slides: dict[int, SlideDocument] = {}
    facts: list[ContinuityFact] = []
    current: int | None = None
    in_block = False
    for line in lines:
        if line.startswith("CONTINUITY LEDGER"):
            in_block = True
            continue
        if in_block and line.startswith("STATE-TRANSITION"):
            break
        if not in_block:
            continue
        header = re.match(r"^S(\d+)\s*$", line.strip())
        if header:
            current = int(header.group(1))
            slides[current] = SlideDocument(index=current)
            continue
        if current is None or ":" not in line:
            continue
        field, value = line.strip().split(":", 1)
        field = field.strip()
        value = value.strip()
        slide = slides[current]
        facts.append(ContinuityFact(slide_index=current, field=field, value=value))
        upper = field.upper()
        if upper == "VISIBLE CLOCK":
            bar = re.search(r"status bar\s+(\d{1,2}:\d{2})", value, re.IGNORECASE)
            if bar and re.search(r"\bPM\b", value, re.IGNORECASE):
                slide.visible_clock = f"{bar.group(1)} PM"
            elif bar:
                slide.visible_clock = f"status bar {bar.group(1)}"
            else:
                slide.visible_clock = value
        elif upper == "VISIBLE DATE":
            slide.visible_date = value
        elif upper == "OVERLAY":
            slide.overlay = value
        elif upper == "ORDER STATE":
            slide.order_state = value
        elif upper.startswith("KNOWS"):
            slide.actor_knowledge = value
        elif upper == "ACTOR LOCATION":
            slide.actor_location = value
        elif upper == "RELATIVE TIME":
            slide.relative_time = value
    return [slides[index] for index in sorted(slides)], facts
