import threading
import time

print("T1: thread test")
threading.Thread(target=lambda: print("THREAD_RAN"), daemon=True).start()
time.sleep(1)

print("T2: plain WSGI")
import wsgiref.simple_server
import requests


def app(environ, start_response):
    start_response("200 OK", [("Content-Type", "text/plain")])
    return [b"PLAIN_WSGI_HAI"]


srv = wsgiref.simple_server.make_server("127.0.0.1", 8128, app)
threading.Thread(target=srv.serve_forever, daemon=True).start()
time.sleep(1)
r = requests.get("http://127.0.0.1:8128/", timeout=15)
print("PLAIN_WSGI_TEST", r.status_code, r.text)
srv.shutdown()

print("T3: a2wsgi minimal")
from a2wsgi import ASGIMiddleware


async def aapp(scope, receive, send):
    await send({"type": "http.response.start", "status": 200, "headers": [(b"content-type", b"text/plain")]})
    await send({"type": "http.response.body", "body": b"A2WSGI_HAI"})


srv2 = wsgiref.simple_server.make_server("127.0.0.1", 8129, ASGIMiddleware(aapp))
threading.Thread(target=srv2.serve_forever, daemon=True).start()
time.sleep(1)
r2 = requests.get("http://127.0.0.1:8129/", timeout=15)
print("A2WSGI_TEST", r2.status_code, r2.text)
srv2.shutdown()
print("ALL_TESTS_DONE")