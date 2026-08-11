import socket
import threading
import time

print("A: loopback connect same-thread", flush=True)
s = socket.socket()
s.bind(("127.0.0.1", 8130))
s.listen(1)
c = socket.create_connection(("127.0.0.1", 8130), timeout=5)
print("LOOPBACK_CONNECT_OK", flush=True)
c.close()
s.close()

print("B: accept in thread", flush=True)
s2 = socket.socket()
s2.bind(("127.0.0.1", 8131))
s2.listen(1)


def acc():
    conn, _addr = s2.accept()
    conn.sendall(b"RAW_THREAD_ACCEPT_OK")
    conn.close()


threading.Thread(target=acc, daemon=True).start()
c2 = socket.create_connection(("127.0.0.1", 8131), timeout=10)
print("RECV:", c2.recv(64), flush=True)
c2.close()
s2.close()

print("C: wsgiref in MAIN thread + connect", flush=True)
import wsgiref.simple_server


def app(environ, start_response):
    start_response("200 OK", [("Content-Type", "text/plain")])
    return [b"MAIN_WSGI_HAI"]


srv = wsgiref.simple_server.make_server("127.0.0.1", 8132, app)
import requests
r = requests.get("http://127.0.0.1:8132/", timeout=10)
print("MAIN_WSGI", r.status_code, r.text, flush=True)
srv.shutdown()
print("ISO_ALL_DONE", flush=True)