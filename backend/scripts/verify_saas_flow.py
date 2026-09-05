"""Run a small end-to-end smoke check against a running LeTrusto backend.

Usage:
    python scripts/verify_saas_flow.py --base-url http://127.0.0.1:8000

The script creates a uniquely named test account and leaves its widget/event rows
in place so the public response can be inspected after the run.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from typing import Any

import httpx


PASSWORD = "SmokeTest-2026!"


def request_json(client: httpx.Client, method: str, path: str, **kwargs: Any) -> dict[str, Any] | list[Any]:
    response = client.request(method, path, **kwargs)
    if not response.is_success:
        raise RuntimeError(f"{method} {path} returned {response.status_code}: {response.text}")
    return response.json()


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the deployed SaaS widget flow")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Backend origin, without /api/v1")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    unique = uuid.uuid4().hex[:10]
    email = f"saas-smoke-{unique}@example.com"

    with httpx.Client(base_url=base_url, timeout=15.0) as client:
        registered = request_json(
            client,
            "POST",
            "/api/v1/auth/register",
            json={"email": email, "password": PASSWORD, "full_name": "SaaS Smoke Test"},
        )
        access_token = registered.get("access_token")
        if not access_token:
            raise RuntimeError("Registration response did not contain access_token")
        headers = {"Authorization": f"Bearer {access_token}"}

        widget = request_json(
            client,
            "POST",
            "/api/v1/widgets",
            headers=headers,
            json={
                "name": "Production smoke widget",
                "domain_name": "example.com",
                "theme_color": "#e11d48",
                "position": "bottom-left",
                "display_delay": 3,
                "is_active": True,
            },
        )
        widget_id = widget.get("id")
        if not widget_id:
            raise RuntimeError("Widget response did not contain id")

        event = request_json(
            client,
            "POST",
            f"/api/v1/widgets/{widget_id}/events",
            headers=headers,
            json={
                "customer_name": "Smoke Customer",
                "customer_location": "Bengaluru",
                "action_text": "just purchased the starter plan",
                "rating": 5,
                "review_text": "A public smoke-test review.",
                "is_approved": True,
            },
        )
        if event.get("widget_id") != widget_id:
            raise RuntimeError("Event response was not attached to the created widget")

        public = request_json(client, "GET", f"/api/v1/public/embed/{widget_id}")
        public_response = client.get(f"/api/v1/public/embed/{widget_id}", headers={"Origin": "https://customer-example.test"})
        if public_response.headers.get("access-control-allow-origin") != "*":
            raise RuntimeError("Public embed response did not allow wildcard CORS")
        if public.get("id") != widget_id:
            raise RuntimeError("Public embed response returned the wrong widget id")
        events = public.get("events")
        if not isinstance(events, list) or not events or events[0].get("customer_name") != "Smoke Customer":
            raise RuntimeError("Public embed response did not contain the approved smoke event")

    print(json.dumps({
        "status": "ok",
        "email": email,
        "widget_id": widget_id,
        "public_event_count": len(events),
        "public_keys": sorted(public.keys()),
        "event_keys": sorted(events[0].keys()),
    }, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (httpx.HTTPError, RuntimeError) as exc:
        print(f"SaaS smoke test failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
