import sys
import time

sys.path.insert(0, "/home/docaiid/src")

BASE_ENV = {
    "REQUEST_METHOD": "GET",
    "SCRIPT_NAME": "",
    "PATH_INFO": "/",
    "QUERY_STRING": "",
    "SERVER_NAME": "test",
    "SERVER_PORT": "80",
    "SERVER_PROTOCOL": "HTTP/1.1",
    "wsgi.version": (1, 0),
    "wsgi.url_scheme": "http",
    "wsgi.input": sys.stdin.buffer,
    "wsgi.errors": sys.stderr,
    "wsgi.multithread": True,
    "wsgi.multiprocess": False,
    "wsgi.run_once": False,
}
HEADERS = []


def sr(*args):
    print("START_RESPONSE", args[0], flush=True)


print("T1: minimal ASGI consumed", flush=True)
from a2wsgi import ASGIMiddleware  # noqa: E402


async def app(scope, receive, send):
    await send({"type": "http.response.start", "status": 200, "headers": [(b"content-type", b"text/plain")]})
    await send({"type": "http.response.body", "body": b"OK_MINIMAL"})


t0 = time.time()
try:
    out = list(ASGIMiddleware(app)(dict(BASE_ENV), sr))
    print("MINIMAL_CONSUMED", out, "in %.1fs" % (time.time() - t0), flush=True)
except Exception as e:  # noqa: BLE001
    print("MINIMAL_EXC", type(e).__name__, str(e)[:300], flush=True)

print("T2: FastAPI /health consumed", flush=True)
from docai.api import app as fastapi_app  # noqa: E402

w = ASGIMiddleware(fastapi_app)
env2 = dict(BASE_ENV)
env2["PATH_INFO"] = "/health"
t0 = time.time()
try:
    out = list(w(env2, sr))
    print("FASTAPI_CONSUMED", out, "in %.1fs" % (time.time() - t0), flush=True)
except Exception as e:  # noqa: BLE001
    print("FASTAPI_EXC", type(e).__name__, str(e)[:300], flush=True)

print("ALL_DONE", flush=True)