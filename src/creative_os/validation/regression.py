from creative_os.validation.checks import (
    arithmetic_status,
    aspect_ratio_status,
    continuity_transition_status,
    lock_precedence_status,
    recursive_edit_status,
    reference_date_status,
    weekday_status,
)

DETERMINISTIC_CODES = {"T04", "T05", "T06", "T14", "T16", "T17", "T18"}
HUMAN_CODES = {"T13"}
MODEL_CODES = {"T01", "T02", "T03a", "T03b", "T07", "T08", "T09", "T10", "T11", "T12", "T15"}


def evaluation_mode_for(code: str) -> str:
    if code in DETERMINISTIC_CODES:
        return "DETERMINISTIC"
    if code in HUMAN_CODES:
        return "HUMAN_REVIEW"
    return "MODEL_REVIEW"


def run_regression_case(code: str) -> tuple[str, str]:
    """Execute the canonical fixture for a regression id.

    Judgment cases return an explicit review status. They never return PASS.
    """
    if code == "T16":
        return arithmetic_status("142.97", "125.00", "1.26", "19.23")
    if code == "T17":
        return weekday_status("2026-10-07", "Wednesday")
    if code == "T14":
        status, message = aspect_ratio_status(1080, 1920)
        if status != "FAIL":
            return "FAIL", "1080x1920 was accepted"
        ok, ok_message = aspect_ratio_status(1206, 2622)
        if ok != "PASS":
            return "FAIL", ok_message
        return "PASS", f"9:16 rejected ({message}); 1206x2622 accepted"
    if code == "T05":
        stale = reference_date_status("Pick up by Wed, Oct 23", "Oct 7")
        current = reference_date_status("Pick up by Wed, Oct 7", "Oct 7")
        if stale[0] != "FAIL" or current[0] != "PASS":
            return "FAIL", f"stale={stale[0]} current={current[0]}"
        return "PASS", "ledger date wins over the reference date"
    if code == "T04":
        return continuity_transition_status(
            hook_says_tomorrow=True,
            payoff_same_calendar_day=True,
            transition_present=False,
        )
    if code == "T06":
        old = lock_precedence_status("AirPods 4", ["AirPods 5"], False, False)
        kept = lock_precedence_status("AirPods 4", ["AirPods 5"], True, False)
        deleted = lock_precedence_status("AirPods 4", ["AirPods 5"], True, True)
        current = lock_precedence_status("AirPods 5", ["AirPods 5"], False, False)
        if (old[0], kept[0], deleted[0], current[0]) != ("FAIL", "PASS", "FAIL", "PASS"):
            return "FAIL", f"old={old[0]} kept={kept[0]} deleted={deleted[0]} current={current[0]}"
        return "PASS", "current model wins; old assets stay on disk and are marked stale"
    if code == "T18":
        chained = recursive_edit_status(False)
        original = recursive_edit_status(True)
        unknown = recursive_edit_status(None)
        if chained[0] != "FAIL" or original[0] != "PASS" or unknown[0] != "HUMAN_REVIEW_REQUIRED":
            return "FAIL", f"chained={chained[0]} original={original[0]} unknown={unknown[0]}"
        return "PASS", "derivative edits fail; original base passes; unknown chain needs a human"
    if code == "T13":
        return (
            "HUMAN_REVIEW_REQUIRED",
            "live retailer verification is not performed by software",
        )
    if code in MODEL_CODES:
        return (
            "MODEL_REVIEW_REQUIRED",
            "this case needs creative judgment; automated PASS is intentionally withheld",
        )
    return "NOT_IMPLEMENTED", f"no runner for {code}"
