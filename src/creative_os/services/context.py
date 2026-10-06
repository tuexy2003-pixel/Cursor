from sqlalchemy.orm import Session

from creative_os.models import Creative
from creative_os.services.context_compiler import compile_context


def assemble_context(session: Session, creative: Creative, limit: int = 24) -> dict[str, object]:
    """Compatibility summary. The dry-run package is compile_context, not this dict."""
    package = compile_context(session, creative, stage="full", heuristic_budget=max(limit, 1))
    return {
        "creative_id": creative.id,
        "global_policy_codes": [item["code"] for item in package["global_invariants"]],
        "program_policy_codes": [item["code"] for item in package["program_policies"]],
        "account_policy_codes": [item["code"] for item in package["account_policies"]],
        "campaign_policy_codes": [item["code"] for item in package["campaign_policies"]],
        "creative_policy_codes": [item["code"] for item in package["creative_locks"]],
        "active_skill_ids": [item["version_id"] for item in package["skill_versions"]],
        "story_lock_version_id": None
        if package["current_story_lock_version"] is None
        else package["current_story_lock_version"]["id"],
        "benchmark_names": [item["name"] for item in package["benchmarks"]],
        "holdouts_excluded": True,
        "mechanic_counts": package["mechanic_context"]["windows"]["lifetime"],
        "compiler": "context-compiler-v1",
        "provider_execution": "NOT_IMPLEMENTED",
    }
