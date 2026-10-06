import hashlib
from datetime import UTC, datetime
from decimal import Decimal


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def utcnow() -> datetime:
    return datetime.now(UTC)


def money(value: str | Decimal) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))
