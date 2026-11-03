"""Atomic JSON saves, a routine lock, and the activity list."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
HISTORY = DATA / "skill-history"
BACKUPS = DATA / "backups"


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def ensure_dirs():
    DATA.mkdir(exist_ok=True)
    HISTORY.mkdir(exist_ok=True)
    BACKUPS.mkdir(exist_ok=True)


def atomic_write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def write_json(path: Path, payload):
    atomic_write(path, json.dumps(payload, indent=2, ensure_ascii=False))


def log_line(message):
    ensure_dirs()
    line = f"{now_iso()} {message}\n"
    path = DATA / "jarvis.log"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line)


def add_activity(kind, text):
    ensure_dirs()
    path = DATA / "activity.json"
    rows = read_json(path, [])
    rows.insert(0, {"at": now_iso(), "kind": kind, "text": text[:400]})
    write_json(path, rows[:80])


def snapshot_skill(name, text):
    ensure_dirs()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    folder = HISTORY / name
    folder.mkdir(parents=True, exist_ok=True)
    atomic_write(folder / f"{stamp}.md", text)
    copies = sorted(folder.glob("*.md"))
    for old in copies[:-7]:
        old.unlink(missing_ok=True)


class RoutineLock:
    def __init__(self):
        self.path = DATA / "routine.lock"

    def acquire(self):
        ensure_dirs()
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            return False
        os.write(fd, now_iso().encode("utf-8"))
        os.close(fd)
        return True

    def release(self):
        self.path.unlink(missing_ok=True)
