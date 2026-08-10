"""Vercel serverless entrypoint for the DocAI FastAPI app.

Vercel mounts this file under /api. Rewrites in vercel.json expose /parse,
/health, / and /docs at the site root too. A leading "/api" prefix (when
present) is stripped before routing, so the same app works both locally and
on Vercel without code changes.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make the src-layout package importable when running serverless.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from docai.api import app as _app  # noqa: E402


class _StripApiPrefix:
    """Strip a leading /api prefix from request paths (Vercel convention)."""

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "")
            if path == "/api" or path.startswith("/api/"):
                scope["path"] = path[len("/api"):] or "/"
                raw = scope.get("raw_path")
                if raw is not None:
                    scope["raw_path"] = raw[len(b"/api"):] or b"/"
        await self.inner(scope, receive, send)


app = _StripApiPrefix(_app)