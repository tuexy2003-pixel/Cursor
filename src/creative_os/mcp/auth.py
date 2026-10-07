"""MCP bearer credential. Operator identity is not a secret and is not accepted here."""

import hmac

from creative_os.config import get_settings


def configured_mcp_token() -> str | None:
    secret = get_settings().mcp_token
    if secret is None:
        return None
    value = secret.get_secret_value().strip()
    return value or None


def mcp_bearer_matches(authorization: str | None) -> bool:
    expected = configured_mcp_token()
    if not expected or not authorization:
        return False
    scheme, _, presented = authorization.partition(" ")
    if scheme.lower() != "bearer" or not presented:
        return False
    if len(presented) != len(expected):
        return False
    return hmac.compare_digest(presented, expected)
