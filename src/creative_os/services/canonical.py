import json
from typing import Any

from creative_os.schemas.story_lock import StoryLockDocument
from creative_os.util import sha256_text


def canonical_payload(document: StoryLockDocument | dict[str, Any]) -> dict[str, Any]:
    if isinstance(document, StoryLockDocument):
        return document.model_dump(mode="json")
    return StoryLockDocument.model_validate(document).model_dump(mode="json")


def canonical_json(document: StoryLockDocument | dict[str, Any]) -> str:
    payload = canonical_payload(document)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def document_hash(document: StoryLockDocument | dict[str, Any]) -> str:
    return sha256_text(canonical_json(document))


def stable_digest(payload: dict[str, Any]) -> str:
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256_text(text)
