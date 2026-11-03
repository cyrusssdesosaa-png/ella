"""Ella — desktop app wrapper. Launches the server and opens a pywebview window."""

import multiprocessing
import os
import signal
import sys
import threading
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

SERVER_URL = "http://127.0.0.1:8765"
TITLE = "E.L.L.A."


def _server_process():
    """Run server.py in a child process."""
    from server import main
    main()


def _wait_for_server(timeout=20):
    """Block until the server responds or timeout."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(SERVER_URL + "/api/state", timeout=2):
                return True
        except Exception:
            time.sleep(0.4)
    return False


def main():
    import webview

    proc = multiprocessing.Process(target=_server_process, daemon=True)
    proc.start()

    if not _wait_for_server():
        print("Server did not start in time.", flush=True)
        proc.terminate()
        sys.exit(1)

    window = webview.create_window(
        TITLE,
        SERVER_URL,
        width=1280,
        height=800,
        min_size=(900, 600),
        background_color="#05070a",
        text_select=False,
    )

    def on_closed():
        proc.terminate()
        proc.join(timeout=3)
        if proc.is_alive():
            proc.kill()

    window.events.closed += on_closed

    webview.start(debug=("--debug" in sys.argv))


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
