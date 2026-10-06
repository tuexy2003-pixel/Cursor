from collections import defaultdict
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from creative_os.models import Creative, PolicyRule
from creative_os.util import ensure_utc, utcnow

SCOPE_RANK = {"GLOBAL": 0, "PROGRAM": 1, "ACCOUNT": 2, "CAMPAIGN": 3, "CREATIVE": 4}


class PolicyIntegrityError(RuntimeError):
    pass


def applicable(rule: PolicyRule, creative: Creative) -> bool:
    if rule.scope_level == "GLOBAL":
        return True
    if rule.scope_level == "PROGRAM":
        return rule.scope_id == creative.program_id
    if rule.scope_level == "ACCOUNT":
        return creative.account_id is not None and rule.scope_id == creative.account_id
    if rule.scope_level == "CAMPAIGN":
        return creative.campaign_id is not None and rule.scope_id == creative.campaign_id
    if rule.scope_level == "CREATIVE":
        return rule.scope_id == creative.id
    return False


def eligible(rule: PolicyRule, as_of: datetime) -> bool:
    if rule.status != "active":
        return False
    if rule.approval_state != "APPROVED":
        return False
    moment = ensure_utc(as_of)
    if rule.effective_from is not None and ensure_utc(rule.effective_from) > moment:
        return False
    if rule.effective_to is not None and ensure_utc(rule.effective_to) <= moment:
        return False
    return True


def resolve_policy(
    session: Session,
    creative: Creative,
    as_of: datetime | None = None,
) -> list[PolicyRule]:
    included, _excluded = resolve_policy_detail(session, creative, as_of)
    return included


def resolve_policy_detail(
    session: Session,
    creative: Creative,
    as_of: datetime | None = None,
) -> tuple[list[PolicyRule], list[tuple[PolicyRule, str]]]:
    moment = ensure_utc(as_of or utcnow())
    rows = session.scalars(select(PolicyRule).order_by(PolicyRule.code, PolicyRule.id)).all()
    grouped: dict[tuple[str, str], list[PolicyRule]] = defaultdict(list)
    for rule in rows:
        if eligible(rule, moment) and applicable(rule, creative):
            grouped[(rule.code, rule.rule_kind)].append(rule)
    included: list[PolicyRule] = []
    excluded: list[tuple[PolicyRule, str]] = []
    for key in sorted(grouped):
        group = grouped[key]
        _reject_ambiguous(group)
        if key[1] == "INVARIANT":
            globals_ = [rule for rule in group if rule.scope_level == "GLOBAL"]
            if globals_:
                included.append(globals_[0])
                for rule in group:
                    if rule.scope_level != "GLOBAL":
                        excluded.append((rule, "active approved global invariant is non-overridable"))
                continue
        best_rank = max(SCOPE_RANK.get(rule.scope_level, 99) for rule in group)
        best = [rule for rule in group if SCOPE_RANK.get(rule.scope_level, 99) == best_rank]
        if len(best) != 1:
            raise PolicyIntegrityError(f"ambiguous policy {key[0]} {key[1]} at scope rank {best_rank}")
        included.append(best[0])
        for rule in group:
            if rule.id != best[0].id:
                excluded.append((rule, "more specific scope applies"))
    return included, excluded


def _reject_ambiguous(group: list[PolicyRule]) -> None:
    seen: dict[tuple[str, str | None], PolicyRule] = {}
    for rule in group:
        identity = (rule.scope_level, rule.scope_id)
        previous = seen.get(identity)
        if previous is not None:
            raise PolicyIntegrityError(
                "ambiguous active policy "
                f"{rule.code} {rule.rule_kind} at {rule.scope_level}:{rule.scope_id} "
                f"({previous.id} and {rule.id})"
            )
        seen[identity] = rule
