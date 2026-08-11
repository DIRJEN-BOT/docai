import sys
import time

sys.path.insert(0, "/home/docaiid/src")
from a2wsgi import ASGIMiddleware


async def app(scope, receive, send):
    await send({"type": "http.response.start", "status": 200, "headers": [(b"content-type", b"text/plain")]})
    await send({"type": "http.response.body", "body": b"OK_MINIMAL"})


w = ASGIMiddleware(app)
env = {
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
t0 = time.time()
try:
    result = w(env, lambda s, h: print("SS", s, flush=True))
    print("A2WSGI_DIRECT_RETURNED", result, "in %.1fs" % (time.time() - t0), flush=True)
except Exception as e:  # noqa: BLE001
    print("A2WSGI_DIRECT_EXC", type(e).__name__, str(e)[:200], flush=True)
print("A2WSGI_DIRECT_DONE", flush=True)