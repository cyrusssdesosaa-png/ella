"""Real Stop: a cancel epoch shared by every in-flight model request.

Each /api/ask grabs a token (the current epoch) when it arrives. /api/cancel
bumps the epoch, so every request that started earlier is cancelled - even
ones still queued behind the routine lock. The next request gets a fresh
token, so nothing needs resetting.
"""

import http.client
import socket
import threading
import urllib.parse

_lock = threading.Lock()
_epoch = 0
_local = threading.local()
POLL_SECONDS = 0.1


class Cancelled(Exception):
    pass


def begin():
    """Bind a fresh token to this thread and return it."""
    with _lock:
        token = _epoch
    _local.token = token
    return token


def end():
    _local.token = None


def cancel_all():
    global _epoch
    with _lock:
        _epoch += 1
        return _epoch


def is_cancelled(token=None):
    if token is None:
        token = getattr(_local, "token", None)
    if token is None:
        return False
    with _lock:
        return _epoch > token


def check():
    if is_cancelled():
        raise Cancelled()


def post_json(url, data, headers, timeout):
    """POST bytes; return (status, headers, body_bytes). Raises Cancelled.

    The socket is closed from this thread when Stop fires, so Ollama sees the
    disconnect and aborts generation instead of finishing in the background.
    """
    token = getattr(_local, "token", None)
    if is_cancelled(token):
        raise Cancelled()
    parts = urllib.parse.urlsplit(url)
    cls = http.client.HTTPSConnection if parts.scheme == "https" else http.client.HTTPConnection
    conn = cls(parts.hostname, parts.port, timeout=timeout)
    path = parts.path or "/"
    if parts.query:
        path += "?" + parts.query
    box = {}

    def work():
        try:
            conn.request("POST", path, body=data, headers=headers)
            res = conn.getresponse()
            box["result"] = (res.status, res.headers, res.read())
        except BaseException as exc:  # noqa: BLE001 - re-raised in caller
            box["error"] = exc

    worker = threading.Thread(target=work, daemon=True, name="ella-model-request")
    worker.start()
    try:
        while worker.is_alive():
            worker.join(POLL_SECONDS)
            if worker.is_alive() and is_cancelled(token):
                try:
                    if conn.sock is not None:
                        conn.sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                conn.close()
                raise Cancelled()
    finally:
        if not worker.is_alive():
            conn.close()
    if is_cancelled(token):
        raise Cancelled()
    if "error" in box:
        raise box["error"]
    return box["result"]
