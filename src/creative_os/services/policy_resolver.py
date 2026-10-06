from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from creative_os.models import Creative, PolicyRule

SCOPE_RANK = {"GLOBAL": 0, "PROGRAM": 1, "ACCOUNT": 2, "CAMPAIGN": 3, "CREATIVE": 4}


def applicable(rule: PolicyRule, creative: Creative) -> bool:
    if rule.status != "active":
        return False
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


def resolve_policy(session: Session, creative: Creative) -> list[PolicyRule]:
    """Most specific scope wins for the same code and kind. Every applicable invariant code is kept."""
    rows = session.scalars(select(PolicyRule).order_by(PolicyRule.code, PolicyRule.id)).all()
    grouped: dict[tuple[str, str], list[PolicyRule]] = defaultdict(list)
    for rule in rows:
        if applicable(rule, creative):
            grouped[(rule.code, rule.rule_kind)].append(rule)
    resolved: list[PolicyRule] = []
    for key in sorted(grouped):
        group = grouped[key]
        group.sort(key=lambda rule: (SCOPE_RANK.get(rule.scope_level, 99), rule.id))
        resolved.append(group[-1])
    return resolved
