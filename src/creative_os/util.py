import hashlib
from datetime import UTC, datetime
from decimal import Decimal


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def utcnow() -> datetime:
    return datetime.now(UTC)


def ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def post_age_hours(published_at: datetime, captured_at: datetime) -> float:
    delta = ensure_utc(captured_at) - ensure_utc(published_at)
    return delta.total_seconds() / 3600


def money(value: str | Decimal) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))
