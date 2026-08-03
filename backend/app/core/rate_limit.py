"""Simple in-memory sliding-window rate-limit middleware."""
from __future__ import annotations

import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-IP, per-minute rate limiting using a sliding window."""

    def __init__(self, app, default_limit: int = 120, auth_limit: int = 10) -> None:
        super().__init__(app)
        self.default_limit = default_limit
        self.auth_limit = auth_limit
        self._windows: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path

        is_auth_path = path.endswith("/auth/register") or path.endswith("/auth/login")
        limit = self.auth_limit if is_auth_path else self.default_limit

        key = f"{client_ip}:{path if is_auth_path else 'global'}"
        now = time.monotonic()
        window = self._windows[key]

        while window and now - window[0] > 60:
            window.popleft()

        if len(window) >= limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please slow down."},
                headers={"Retry-After": "60"},
            )

        window.append(now)
        return await call_next(request)
