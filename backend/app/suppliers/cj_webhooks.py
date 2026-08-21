"""Verified, provider-neutral parsing primitives for CJ webhooks."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CJWebhookEvent:
    message_id: str
    event_type: str
    message_type: str
    params: dict[str, Any]


def verify_cj_signature(open_id: str, raw_body: bytes, signature: str) -> bool:
    expected = base64.b64encode(hmac.new(open_id.encode("utf-8"), raw_body, hashlib.sha256).digest()).decode("ascii")
    return hmac.compare_digest(expected, signature)


def parse_cj_webhook(raw_body: bytes, *, open_id: str, signature: str) -> CJWebhookEvent:
    if not verify_cj_signature(open_id, raw_body, signature):
        raise ValueError("CJ webhook signature verification failed")
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise ValueError("CJ webhook body is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError("CJ webhook payload must be an object")
    params = payload.get("params")
    if not isinstance(params, dict):
        raise ValueError("CJ webhook params must be an object")
    message_id = str(payload.get("messageId") or "").strip()
    event_type = str(payload.get("type") or "").strip().upper()
    message_type = str(payload.get("messageType") or "").strip().upper()
    if not message_id or not event_type or not message_type:
        raise ValueError("CJ webhook is missing messageId, type, or messageType")
    return CJWebhookEvent(message_id, event_type, message_type, params)


class CJWebhookDeduplicator:
    def __init__(self) -> None:
        self._message_ids: set[str] = set()

    def accept(self, event: CJWebhookEvent) -> bool:
        if event.message_id in self._message_ids:
            return False
        self._message_ids.add(event.message_id)
        return True