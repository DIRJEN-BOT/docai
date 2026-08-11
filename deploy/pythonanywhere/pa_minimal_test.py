import sys
import threading
import wsgiref.simple_server

from a2wsgi import ASGIMiddleware


async def app(scope, receive, send):
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [(b"content-type", b"text/plain")],
        }
    )
    await send({"type": "http.response.body", "body": b"HELLO_MINIMAL"})
    return None


srv = wsgiref.simple_server.make_server("127.0.0.1", 8124, ASGIMiddleware(app))
threading.Thread(target=srv.serve_forever, daemon=True).start()

import requests  # noqa: E402

r = requests.get("http://127.0.0.1:8124/", timeout=15)
print("MINIMAL_TEST", r.status_code, r.text)
srv.shutdown()
print("MINIMAL_TEST_DONE")