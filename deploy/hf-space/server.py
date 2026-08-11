"""DocAI HF Space entrypoint.

Runs the same FastAPI app as `docai.api` (health, /parse JSON+CSV, demo page).
The src-layout package is vendored under src/ so the Space is self-contained.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from docai.api import app  # noqa: E402
