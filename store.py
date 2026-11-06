"""Atomic JSON saves, cross-process file locking, and the activity list."""

import contextlib
import json
import os
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import msvcrt
except ImportError:  # non-Windows hosts (offline tests). Windows keeps msvcrt.
    msvcrt = None

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
HISTORY = DATA / "skill-history"
BACKUPS = DATA / "backups"

# Intra-process reentrant locks (ThreadingHTTPServer concurrency safety).
# Reentrant so the same thread can re-acquire (e.g. make_backup holding a lock
# while calling add_activity which locks the same file again).
_file_locks: dict[str, threading.RLock] = {}
_locks_guard = threading.Lock()


def _thread_lock_for(path: Path) -> threading.RLock:
    key = str(path.resolve())
    with _locks_guard:
        if key not in _file_locks:
            _file_locks[key] = threading.RLock()
        return _file_locks[key]


def _cross_process_lock(path: Path, timeout: float = 5.0):
    """Acquire an exclusive cross-process lock on a dedicated lock file.

    Uses msvcrt.locking() on Windows, with non-blocking retries so a hung or
    crashed sibling cannot permanently block the lock file. Other hosts use
    fcntl so the same helpers can be tested offline. Returns the open file
    descriptor. Must be released with _cross_process_unlock().
    """
    lock_path = path.with_suffix(path.suffix + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR)
    deadline = time.monotonic() + timeout
    while True:
        try:
            if msvcrt is not None:
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return fd
        except OSError:
            if time.monotonic() >= deadline:
                os.close(fd)
                raise
            time.sleep(0.05)


def _cross_process_unlock(fd: int):
    try:
        if msvcrt is not None:
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(fd, fcntl.LOCK_UN)
    except OSError:
        pass
    os.close(fd)


@contextlib.contextmanager
def file_transaction(path: Path):
    """Context manager for a locked file transaction.

    Acquires the intra-process RLock first, then the cross-process lock.
    Releases in reverse order. All read-modify-write operations on a file
    must occur within this context to prevent lost updates and colliding
    temporary files.
    """
    threading_lock = _thread_lock_for(path)
    threading_lock.acquire()
    try:
        lock_fd = _cross_process_lock(path)
        try:
            yield
        finally:
            _cross_process_unlock(lock_fd)
    finally:
        threading_lock.release()


@contextlib.contextmanager
def multi_file_transaction(paths: list[Path]):
    """Acquire locks for multiple files in consistent sorted order.

    Prevents deadlocks when an operation (e.g. backup/restore) touches more
    than one JSON file. Locks are acquired in alphabetical order by resolved
    path string and released in reverse order.
    """
    sorted_paths = sorted({str(p.resolve()) for p in paths})
    acquired: list[tuple[str, object]] = []
    try:
        for key in sorted_paths:
            p = Path(key)
            tl = _thread_lock_for(p)
            tl.acquire()
            acquired.append(("threading", tl))
        for key in sorted_paths:
            p = Path(key)
            fd = _cross_process_lock(p)
            acquired.append(("cross_process", fd))
        yield
    finally:
        # Single release path: release only what was actually acquired, once.
        for kind, lock in reversed(acquired):
            try:
                if kind == "cross_process":
                    _cross_process_unlock(lock)
                else:
                    lock.release()
            except Exception:
                pass  # never mask the original error with a release failure


def locked_update(path: Path, default, transform_fn):
    """Read a JSON file, apply transform_fn under lock, write result atomically.

    The lock is held for the entire read-modify-write transaction. Returns the
    transformed result. This is the safe replacement for read-json/modify/
    write_json sequences.
    """
    ensure_dirs()
    with file_transaction(path):
        data = read_json(path, default)
        result = transform_fn(data)
        atomic_write(path, json.dumps(result, indent=2, ensure_ascii=False))
        return result


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def ensure_dirs():
    DATA.mkdir(exist_ok=True)
    HISTORY.mkdir(exist_ok=True)
    BACKUPS.mkdir(exist_ok=True)


def atomic_write(path: Path, text: str):
    """Write text to path atomically using a unique temporary file.

    The temporary file is created in the same directory as the destination
    (same filesystem) with a unique name via tempfile.mkstemp(), written
    completely, then replaced with os.replace(). Temporary files are cleaned
    up on failure.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=path.name + ".",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def write_json(path: Path, payload):
    """Atomically write a JSON payload without locking.

    Callers that perform read-modify-write must use locked_update() or
    file_transaction() instead to hold the lock across the full transaction.
    """
    atomic_write(path, json.dumps(payload, indent=2, ensure_ascii=False))


def log_line(message):
    ensure_dirs()
    path = DATA / "jarvis.log"
    with file_transaction(path):
        line = f"{now_iso()} {message}\n"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line)


def add_activity(kind, text):
    ensure_dirs()
    path = DATA / "activity.json"

    def transform(rows):
        rows.insert(0, {"at": now_iso(), "kind": kind, "text": text[:400]})
        return rows[:80]

    locked_update(path, [], transform)


def snapshot_skill(name, text):
    ensure_dirs()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    folder = HISTORY / name
    folder.mkdir(parents=True, exist_ok=True)
    atomic_write(folder / f"{stamp}.md", text)
    copies = sorted(folder.glob("*.md"))
    for old in copies[:-7]:
        old.unlink(missing_ok=True)


def make_backup_locked(include_paths: list[Path]):
    """Read multiple files under consistent lock ordering for a backup snapshot.

    Calls the caller-provided read function while all file locks are held,
    preventing reads from observing partially written intermediate states.
    Returns a dict mapping resolved path strings to file contents.
    """
    ensure_dirs()
    with multi_file_transaction(include_paths):
        results = {}
        for p in include_paths:
            key = str(p)
            if p.suffix == ".json":
                results[key] = read_json(p, None)
            else:
                results[key] = p.read_text(encoding="utf-8")
        return results


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
