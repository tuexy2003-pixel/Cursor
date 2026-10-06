from pathlib import Path

from creative_os.config import repo_root
from creative_os.importers.story_lock_parser import parse_story_lock_markdown
from creative_os.validation.checks import (
    arithmetic_status,
    aspect_ratio_status,
    rights_export_status,
    weekday_status,
)
from creative_os.validation.regression import MODEL_CODES, run_regression_case


def test_current_lock_parser_uses_approved_values() -> None:
    text = Path(
        repo_root() / "source_snapshots/2026-10-05/story_locks/TARGET_chore_stuff_STORY_LOCK_current.md"
    ).read_text(encoding="utf-8")
    document = parse_story_lock_markdown(text)
    assert document.floating_hook == "my birthday is literally today 😭"
    assert document.hook == "don't look at the order tho"
    assert document.story_date == "2026-10-05"
    assert document.story_weekday == "Monday"
    assert document.economics is not None
    assert document.economics.subtotal == "142.97"
    assert document.economics.discount == "125.00"
    assert document.economics.tax == "1.26"
    assert document.economics.total == "19.23"
    assert len(document.line_items) == 5
    airpods = document.line_items[2]
    assert airpods.model == "AirPods 5"
    assert airpods.unit_price == "129.99"
    assert len(document.dialogue) == 5
    assert any(door.kind == "primary" for door in document.comment_doors)
    assert document.slides[0].visible_clock == "4:14 PM"


def test_math_spec_total_is_not_the_parser_result() -> None:
    text = Path(
        repo_root() / "source_snapshots/2026-10-05/story_locks/TARGET_CHORE_STUFF_TRANSACTION_MATH_SPEC.md"
    ).read_text(encoding="utf-8")
    assert "$5.33" in text
    document = parse_story_lock_markdown(text)
    assert document.economics is None or document.economics.total != "19.23"


def test_deterministic_regression_classifications() -> None:
    assert run_regression_case("T16")[0] == "PASS"
    assert run_regression_case("T17")[0] == "PASS"
    assert run_regression_case("T14")[0] == "PASS"
    assert run_regression_case("T05")[0] == "PASS"
    assert run_regression_case("T06")[0] == "PASS"
    assert run_regression_case("T18")[0] == "PASS"
    assert run_regression_case("T04")[0] == "FAIL"
    assert run_regression_case("T13")[0] == "HUMAN_REVIEW_REQUIRED"
    for code in MODEL_CODES:
        assert run_regression_case(code)[0] == "MODEL_REVIEW_REQUIRED"


def test_aspect_and_rights_edges() -> None:
    assert aspect_ratio_status(851, 1849)[0] == "PASS"
    assert aspect_ratio_status(853, 1844)[0] == "PASS"
    assert aspect_ratio_status(1080, 1920)[0] == "FAIL"
    assert weekday_status("2026-10-05", "Monday")[0] == "PASS"
    assert arithmetic_status("12.98", "8.00", "0.35", "5.33")[0] == "PASS"
    assert rights_export_status("BASE", "REFERENCE_ONLY", True)[0] == "FAIL"
    assert rights_export_status("BASE", "UNKNOWN", True)[0] == "HUMAN_REVIEW_REQUIRED"
    assert rights_export_status("BASE", "USER_OWNED", True)[0] == "PASS"
