"""Smoke test: serve docai.api under WSGI via a2wsgi + waitress (PA-compatible)."""
import os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "src"))

from a2wsgi import ASGIMiddleware
from waitress import serve
from docai.api import app

application = ASGIMiddleware(app)

if __name__ == "__main__":
    port = int(os.environ.get("SMOKE_PORT", "8090"))
    print(f"serving on {port}", flush=True)
    serve(application, host="127.0.0.1", port=port)