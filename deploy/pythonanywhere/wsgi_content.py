# PythonAnywhere WSGI file content (/var/www/docaiid_pythonanywhere_com_wsgi.py)
# Serves docai FastAPI app under WSGI via a2wsgi.
import os
import sys

PROJECT = "/home/docaiid"
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, "src"))

from a2wsgi import ASGIMiddleware
from docai.api import app

application = ASGIMiddleware(app)