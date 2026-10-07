import re
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

from creative_os.util import money

TARGET_RATIO = Decimal("9") / Decimal("19.6")
DEFAULT_RATIO_TOLERANCE = Decimal("0.008")
CLEARED_RIGHTS = {"CLEARED", "USER_OWNED", "LICENSED", "PUBLIC_DOMAIN"}
_WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}
_CLOCK = re.compile(
    r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?",
    re.IGNORECASE,
)


def arithmetic_status(
    subtotal: str | None,
    discount: str | None,
    tax: str | None,
    total: str | None,
) -> tuple[str, str]:
    if subtotal is None or discount is None or tax is None or total is None:
        return "NOT_APPLICABLE", "economics fields are incomplete"
    expected = money(subtotal) - money(discount) + money(tax)
    actual = money(total)
    if expected == actual:
        return "PASS", f"{subtotal} - {discount} + {tax} = {total}"
    return "FAIL", f"expected {expected} and found {actual}"


def line_items_match_subtotal(prices: list[str], subtotal: str | None) -> tuple[str, str]:
    if subtotal is None or not prices:
        return "NOT_APPLICABLE", "no line prices or subtotal"
    total = sum((money(price) for price in prices), Decimal("0.00"))
    if total == money(subtotal):
        return "PASS", f"line items sum to {subtotal}"
    return "FAIL", f"line items sum to {total}, subtotal is {subtotal}"


def line_items_subtotal_status(items: list[Any], subtotal: str | None) -> tuple[str, str]:
    priced = [item for item in items if item.unit_price]
    if subtotal is None or not priced:
        return "NOT_APPLICABLE", "no line prices or subtotal"
    total = Decimal("0.00")
    for item in priced:
        quantity_text = item.quantity
        if quantity_text is None or str(quantity_text).strip() == "":
            quantity = Decimal(1)
        else:
            try:
                quantity = Decimal(str(quantity_text).strip())
            except InvalidOperation:
                return (
                    "HUMAN_REVIEW_REQUIRED",
                    f"quantity {quantity_text!r} is not a number",
                )
        total += money(item.unit_price) * quantity
    total = total.quantize(Decimal("0.01"))
    if total == money(subtotal):
        return "PASS", f"line items sum to {subtotal}"
    return "FAIL", f"line items sum to {total}, subtotal is {subtotal}"


def weekday_status(iso_date: str, claimed_weekday: str) -> tuple[str, str]:
    parsed = date.fromisoformat(iso_date)
    expected = parsed.strftime("%A")
    if expected.lower() == claimed_weekday.strip().lower():
        return "PASS", f"{iso_date} is {expected}"
    return "FAIL", f"{iso_date} is {expected}, not {claimed_weekday}"


def aspect_ratio_status(
    width: int,
    height: int,
    target: Decimal = TARGET_RATIO,
    tolerance: Decimal = DEFAULT_RATIO_TOLERANCE,
) -> tuple[str, str]:
    if height <= 0 or width <= 0:
        return "FAIL", "width and height must be positive"
    ratio = Decimal(width) / Decimal(height)
    delta = abs(ratio - target)
    if delta <= tolerance:
        return "PASS", f"ratio {ratio:.6f} is within {tolerance} of {target:.6f}"
    return "FAIL", f"ratio {ratio:.6f} differs from {target:.6f} by {delta:.6f}"


def clock_to_minutes(text: str) -> int | None:
    match = _CLOCK.search(text)
    if not match:
        return None
    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    meridiem = (match.group(3) or "").lower()
    if meridiem == "pm" and hour < 12:
        hour += 12
    if meridiem == "am" and hour == 12:
        hour = 0
    if hour > 23 or minute > 59:
        return None
    return hour * 60 + minute


def parse_clock_with_carry(text: str, carry: str | None) -> tuple[int | None, str | None]:
    match = _CLOCK.search(text)
    if not match:
        return None, carry
    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    meridiem = (match.group(3) or "").lower() or carry
    if not match.group(3) and carry:
        meridiem = carry
    if meridiem == "pm" and hour < 12:
        hour += 12
    if meridiem == "am" and hour == 12:
        hour = 0
    if hour > 23 or minute > 59:
        return None, carry
    next_carry = meridiem or carry
    return hour * 60 + minute, next_carry


def timeline_order_status(clocks: list[str | None]) -> tuple[str, str]:
    parsed: list[int] = []
    carry: str | None = None
    for value in clocks:
        if not value:
            continue
        if re.search(r"\bPM\b", value, re.IGNORECASE):
            carry = "pm"
        elif re.search(r"\bAM\b", value, re.IGNORECASE):
            carry = "am"
        minute, carry = parse_clock_with_carry(value, carry)
        if minute is not None:
            parsed.append(minute)
    if len(parsed) < 2:
        return "NOT_APPLICABLE", "fewer than two parseable clocks"
    if parsed != sorted(parsed):
        return "FAIL", f"clocks are not in order: {parsed}"
    return "PASS", f"clocks are ordered: {parsed}"


def continuity_transition_status(
    hook_says_tomorrow: bool,
    payoff_same_calendar_day: bool,
    transition_present: bool,
) -> tuple[str, str]:
    if hook_says_tomorrow and payoff_same_calendar_day and not transition_present:
        return "FAIL", "tomorrow hook followed by a same-day payoff without a transition"
    if not hook_says_tomorrow:
        return "NOT_APPLICABLE", "hook does not claim tomorrow"
    return "PASS", "timeline transition is consistent with the structured flags"


def reference_date_status(visible_date: str, ledger_date_token: str) -> tuple[str, str]:
    if ledger_date_token in visible_date:
        return "PASS", "visible date contains the ledger date"
    return (
        "FAIL",
        f"visible date {visible_date!r} does not contain ledger token {ledger_date_token!r}",
    )


def rights_export_status(role: str, rights_status: str, export_as_base: bool) -> tuple[str, str]:
    if not export_as_base:
        return "NOT_APPLICABLE", "asset is not being exported as a base"
    if rights_status == "REFERENCE_ONLY":
        return "FAIL", "REFERENCE_ONLY cannot ship as a production BASE"
    if rights_status == "UNKNOWN":
        return "HUMAN_REVIEW_REQUIRED", "rights are UNKNOWN; a human must clear a production base"
    if rights_status in CLEARED_RIGHTS and role == "BASE":
        return "PASS", f"{rights_status} base may be considered for export"
    if rights_status in CLEARED_RIGHTS and role != "BASE":
        return "FAIL", f"role {role} cannot export as BASE"
    return "HUMAN_REVIEW_REQUIRED", f"unrecognized rights status {rights_status}"


def provenance_status(
    role: str | None,
    rights_status: str | None,
    original_path: str | None,
    content_hash: str | None,
    file_expected: bool,
) -> tuple[str, str]:
    missing = [
        name
        for name, value in (
            ("role", role),
            ("rights_status", rights_status),
            ("original_path", original_path),
        )
        if not value
    ]
    if missing:
        return "FAIL", f"missing provenance fields: {', '.join(missing)}"
    if file_expected and not content_hash:
        return "WARNING", "file is expected in storage but has no hash"
    if not file_expected and not content_hash:
        return "WARNING", "binary is not in the snapshot; hash is unknown"
    return "PASS", "role, rights, path, and hash are present"


def approval_status(has_approved_event: bool, required: bool) -> tuple[str, str]:
    if not required:
        return "NOT_APPLICABLE", "approval is not required for this state"
    if has_approved_event:
        return "PASS", "current version has an approval event"
    return "FAIL", "required approval event is missing"


def product_match_status(lock_models: list[str], asset_model: str | None) -> tuple[str, str]:
    if not asset_model:
        return "NOT_APPLICABLE", "asset has no structured product model"
    if asset_model in lock_models:
        return "PASS", f"{asset_model} is on the current lock"
    return "FAIL", f"{asset_model} is not on the current lock ({', '.join(lock_models) or 'none'})"


def lock_precedence_status(
    asset_model: str,
    lock_models: list[str],
    marked_stale: bool,
    file_deleted: bool,
) -> tuple[str, str]:
    if file_deleted:
        return "FAIL", "historical files must be kept, not deleted or rewritten"
    if asset_model not in lock_models:
        if marked_stale:
            return "PASS", f"{asset_model} is retained and marked stale"
        return "FAIL", f"{asset_model} disagrees with the current lock and is not marked stale"
    return "PASS", f"{asset_model} matches the current lock"


def recursive_edit_status(edit_source_is_original_base: bool | None) -> tuple[str, str]:
    if edit_source_is_original_base is None:
        return "HUMAN_REVIEW_REQUIRED", "edit parent chain is not recorded"
    if edit_source_is_original_base:
        return "PASS", "edit source is the original base"
    return "FAIL", "edit is chained from a derivative instead of the original base"


def claimed_weekday_name(iso_date: str) -> str:
    return date.fromisoformat(iso_date).strftime("%A")


def weekday_index(name: str) -> int | None:
    return _WEEKDAYS.get(name.strip().lower())
