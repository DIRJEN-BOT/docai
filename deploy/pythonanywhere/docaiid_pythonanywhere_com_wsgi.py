# PythonAnywhere WSGI — pure-WSGI docai adapter (no fastapi/a2wsgi/anyio)
import os
import sys

PROJECT = "/home/docaiid"
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, "src"))

from docai.pa_wsgi import application  # noqa: E402
