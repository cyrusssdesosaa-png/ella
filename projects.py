"""Short project list. Skips heavy folders and stops after a few seconds."""

import time
from pathlib import Path

SKIP = {
    "node_modules", ".git", "data", "__pycache__", ".cursor",
    "Temp", "temp", "tmp", "Logs", "logs", "Log",
    "_pip_backup", "dist", "build", ".venv", "venv", "env",
    ".idea", ".vs", ".vscode", "obj", "bin", "cache",
    "AppData", "Library", "thumbnails", ".thumbnails",
}
ROOTS = [
    Path(r"C:\Users\USER\fckkk\cy projects"),
    Path(r"C:\Users\USER\fckkk"),
    Path(r"D:\capstone"),
    Path(r"D:\GOD"),
]


def list_projects(limit=40, seconds=4):
    started = time.time()
    found = []
    seen = set()
    for root in ROOTS:
        if len(found) >= limit or time.time() - started > seconds:
            break
        if not root.exists():
            continue
        key = str(root).lower()
        if key not in seen:
            seen.add(key)
            found.append({"name": root.name, "path": str(root)})
        try:
            children = list(root.iterdir())
        except OSError:
            continue
        for child in children:
            if len(found) >= limit or time.time() - started > seconds:
                break
            if not child.is_dir() or child.name in SKIP or child.name.startswith("."):
                continue
            path = str(child)
            if path.lower() in seen:
                continue
            seen.add(path.lower())
            found.append({"name": child.name, "path": path})
    return found
