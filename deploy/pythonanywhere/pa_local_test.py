import sys
import threading
import wsgiref.simple_server

sys.path.insert(0, "/home/docaiid/src")
from a2wsgi import ASGIMiddleware  # noqa: E402
from docai.api import app  # noqa: E402

srv = wsgiref.simple_server.make_server("127.0.0.1", 8123, ASGIMiddleware(app))
threading.Thread(target=srv.serve_forever, daemon=True).start()

import requests  # noqa: E402

r = requests.get("http://127.0.0.1:8123/health", timeout=20)
print("WSGI_LOCAL_TEST_STATUS", r.status_code, r.text[:300])
srv.shutdown()
print("WSGI_LOCAL_TEST_DONE")