"""Explicit context scope. Assignments are copied from records, never inferred."""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from creative_os.models import Account, Campaign, Creative, Ecosystem, Program


class ScopeError(ValueError):
    pass


@dataclass(frozen=True)
class ContextScope:
    program_id: str | None = None
    account_id: str | None = None
    campaign_id: str | None = None
    creative_id: str | None = None
    ecosystem_id: str | None = None


def scope_from_creative(creative: Creative) -> ContextScope:
    return ContextScope(
        program_id=creative.program_id,
        account_id=creative.account_id,
        campaign_id=creative.campaign_id,
        creative_id=creative.id,
        ecosystem_id=creative.ecosystem_id,
    )


def validate_scope(session: Session, scope: ContextScope) -> ContextScope:
    if scope.program_id is None:
        raise ScopeError("a context scope requires a program")
    program = session.get(Program, scope.program_id)
    if program is None:
        raise ScopeError("program was not found")
    if scope.account_id is not None:
        account = session.get(Account, scope.account_id)
        if account is None or account.program_id != scope.program_id:
            raise ScopeError("account does not belong to the program")
    if scope.campaign_id is not None:
        campaign = session.get(Campaign, scope.campaign_id)
        if campaign is None or campaign.program_id != scope.program_id:
            raise ScopeError("campaign does not belong to the program")
        if campaign.account_id and scope.account_id and campaign.account_id != scope.account_id:
            raise ScopeError("campaign account does not match the selected account")
    if scope.ecosystem_id is not None and session.get(Ecosystem, scope.ecosystem_id) is None:
        raise ScopeError("ecosystem was not found")
    if scope.creative_id is not None:
        creative = session.get(Creative, scope.creative_id)
        if creative is None or creative.program_id != scope.program_id:
            raise ScopeError("creative does not belong to the program")
        if scope.account_id and creative.account_id and creative.account_id != scope.account_id:
            raise ScopeError("creative account does not match the selected account")
        if scope.campaign_id and creative.campaign_id and creative.campaign_id != scope.campaign_id:
            raise ScopeError("creative campaign does not match the selected campaign")
        if scope.ecosystem_id and creative.ecosystem_id and creative.ecosystem_id != scope.ecosystem_id:
            raise ScopeError("creative ecosystem does not match the selected ecosystem")
    return scope
