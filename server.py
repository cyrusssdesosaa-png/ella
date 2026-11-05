"""Ella — local AI assistant. Listens on 127.0.0.1 only."""

import json
import base64
import binascii
import hmac
import re
import secrets
import shutil
import socket
import threading
import time
import urllib.request
import zipfile
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from projects import list_projects
from routines import adapt, check_in, profile, record_usage, retry_outbox, run_model, scout_now, usage_summary
from router import load_env, ollama_models
from vault import find_note, graph, today_text
from stt import transcribe
from tts import synthesize, warmup as tts_warmup
from store import (
    BACKUPS,
    DATA,
    RoutineLock,
    add_activity,
    ensure_dirs,
    locked_update,
    log_line,
    now_iso,
    read_json,
    write_json,
)

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
HOST = "127.0.0.1"
PORT = 8765
ALLOWED_HOSTS = {"127.0.0.1", "localhost"}
API_TOKEN = secrets.token_urlsafe(32)
MAX_JSON_BYTES = 1 * 1024 * 1024
MAX_ASK_BYTES = 20 * 1024 * 1024
MAX_STT_BYTES = 25 * 1024 * 1024
MAX_IMAGE_BYTES = 12 * 1024 * 1024
MAX_IMAGE_DIMENSION = 8192
MAX_IMAGE_PIXELS = 12_000_000
MAX_IMAGE_DATA_URL_CHARS = ((MAX_IMAGE_BYTES + 2) // 3) * 4 + 128
MAX_REQUEST_TARGET_CHARS = 8192
MAX_SEARCH_QUERY_CHARS = 200
MAX_CHAT_TEXT_CHARS = 16000
MAX_TTS_TEXT_CHARS = 2000
HEADER_READ_TIMEOUT_SECONDS = 15
BODY_READ_TIMEOUT_SECONDS = 60
GET_ROUTES = {
    "/", "/index.html", "/app.js", "/styles.css",
    "/api/state", "/api/search", "/api/graph", "/api/note",
}
POST_ROUTES = {
    "/api/stt", "/api/tts", "/api/profile", "/api/checkin", "/api/scout",
    "/api/adapt", "/api/outbox", "/api/backup", "/api/restore", "/api/ask",
    "/api/projects", "/api/brain", "/api/stop",
}
LOCK = RoutineLock()
SESSIONS = DATA / "sessions"
PROJECTS_FILE = ROOT / "bots" / "projects.json"
SKILLS_DIR = ROOT / "skills"
BRAIN_DIR = Path("C:/Users/USER/fckkk/brain")
PROFILES_DIR = ROOT / "profiles"


class RequestError(Exception):
    """A safe, client-facing HTTP error with no internal detail."""

    def __init__(self, status, message, close=False):
        super().__init__(message)
        self.status = status
        self.message = message
        self.close = close


def _require_object(value, label="request"):
    if not isinstance(value, dict):
        raise RequestError(400, f"{label.capitalize()} must be a JSON object.")
    return value


def _require_string(value, label, maximum, allow_empty=False):
    if not isinstance(value, str):
        raise RequestError(400, f"{label} must be a string.")
    if (not allow_empty and not value.strip()) or len(value) > maximum:
        raise RequestError(400, f"{label} is empty or too long.")
    if any(ord(char) < 32 and char not in "\t\n\r" for char in value):
        raise RequestError(400, f"{label} contains unsupported control characters.")
    return value


def _reject_controls(value, label):
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise RequestError(400, f"{label} contains unsupported control characters.")
    return value


def _validate_keys(body, allowed):
    unexpected = set(body) - set(allowed)
    if unexpected:
        raise RequestError(400, "Request contains unsupported fields.")


def _project_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", value):
        raise RequestError(400, "Invalid project identifier.")
    return value


def _safe_component(value, label, maximum=128):
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise RequestError(400, f"Invalid {label}.")
    if value in {".", ".."} or "/" in value or "\\" in value:
        raise RequestError(400, f"Invalid {label}.")
    if any(ord(char) < 32 or ord(char) == 127 for char in value) or any(char in '<>:"|?*' for char in value):
        raise RequestError(400, f"Invalid {label}.")
    if value.endswith((".", " ")):
        raise RequestError(400, f"Invalid {label}.")
    if re.match(r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)", value, re.IGNORECASE):
        raise RequestError(400, f"Invalid {label}.")
    return value


def _safe_markdown_path(root, name, label):
    """Resolve one Markdown basename and reject traversal or symlink escapes."""
    try:
        component = _safe_component(name, label)
        candidate_name = Path(component)
        if candidate_name.suffix and candidate_name.suffix.lower() != ".md":
            return None
        if candidate_name.suffix:
            candidate_name = candidate_name.with_suffix(".md")
        else:
            candidate_name = Path(f"{component}.md")
        base = root.resolve()
        candidate = (base / candidate_name).resolve()
        candidate.relative_to(base)
        return candidate
    except (RequestError, OSError, RuntimeError, ValueError):
        return None


def _validate_project(project):
    project = _require_object(project, "project")
    allowed = {"id", "name", "color", "icon", "path", "prompt", "profile", "brain_files", "skills", "links", "actions"}
    _validate_keys(project, allowed)
    result = dict(project)
    result["id"] = _project_id(result.get("id"))
    result["name"] = _reject_controls(_require_string(result.get("name"), "Project name", 100), "Project name")
    result["color"] = result.get("color", "#4a7fe0")
    if not isinstance(result["color"], str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", result["color"]):
        raise RequestError(400, "Project color must be a six-digit hex color.")
    result["icon"] = _reject_controls(_require_string(result.get("icon", "📁"), "Project icon", 32), "Project icon")
    result["path"] = _reject_controls(_require_string(result.get("path", ""), "Project path", 1024, allow_empty=True), "Project path")
    result["prompt"] = _require_string(result.get("prompt", ""), "Project prompt", 20000, allow_empty=True)

    profile_name = result.get("profile", "")
    if profile_name:
        _safe_component(profile_name, "profile name")
        if not _safe_markdown_path(PROFILES_DIR, profile_name, "profile name"):
            raise RequestError(400, "Invalid profile name.")
    elif not isinstance(profile_name, str):
        raise RequestError(400, "Profile name must be a string.")
    result["profile"] = profile_name

    for key in ("brain_files", "skills"):
        values = result.get(key, [])
        if not isinstance(values, list) or len(values) > 32:
            raise RequestError(400, f"Project {key} must be a bounded list.")
        for value in values:
            _safe_component(value, f"{key} entry")
            if key == "brain_files" and not _safe_markdown_path(BRAIN_DIR, value, "brain file"):
                raise RequestError(400, "Invalid brain file name.")
        result[key] = values

    links = result.get("links", [])
    if not isinstance(links, list) or len(links) > 40:
        raise RequestError(400, "Project links must be a bounded list.")
    for link in links:
        link = _require_object(link, "project link")
        _validate_keys(link, {"label", "url"})
        _reject_controls(_require_string(link.get("label", ""), "Link label", 200, allow_empty=True), "Link label")
        _reject_controls(_require_string(link.get("url"), "Link URL or path", 2048), "Link URL or path")
    result["links"] = links

    actions = result.get("actions", [])
    if not isinstance(actions, list) or len(actions) > 40:
        raise RequestError(400, "Project actions must be a bounded list.")
    for action in actions:
        action = _require_object(action, "project action")
        _validate_keys(action, {"label", "prompt"})
        _reject_controls(_require_string(action.get("label"), "Action label", 100), "Action label")
        _require_string(action.get("prompt"), "Action prompt", 2000, allow_empty=True)
    result["actions"] = actions
    return result


def _validate_projects(projects):
    if not isinstance(projects, list) or len(projects) > 100:
        raise RequestError(400, "Projects must be a bounded list.")
    checked = [_validate_project(project) for project in projects]
    ids = [project["id"] for project in checked]
    if len(set(ids)) != len(ids):
        raise RequestError(400, "Project identifiers must be unique.")
    return checked


def _image_dimensions(data, media_type):
    """Read bounded raster headers without decoding image pixels."""
    if media_type == "image/png":
        if (
            len(data) < 33
            or data[:8] != b"\x89PNG\r\n\x1a\n"
            or int.from_bytes(data[8:12], "big") != 13
            or data[12:16] != b"IHDR"
        ):
            raise RequestError(400, "Image content does not match its PNG type.")
        width = int.from_bytes(data[16:20], "big")
        height = int.from_bytes(data[20:24], "big")
    elif media_type == "image/jpeg":
        if len(data) < 4 or data[:2] != b"\xff\xd8":
            raise RequestError(400, "Image content does not match its JPEG type.")
        width = height = 0
        offset = 2
        scan_limit = min(len(data), 1024 * 1024)
        sof_markers = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
        while offset + 4 <= scan_limit:
            if data[offset] != 0xFF:
                break
            while offset < scan_limit and data[offset] == 0xFF:
                offset += 1
            if offset >= scan_limit:
                break
            marker = data[offset]
            offset += 1
            if marker in {0xD8, 0x01} or 0xD0 <= marker <= 0xD7:
                continue
            if marker in {0xD9, 0xDA} or offset + 2 > scan_limit:
                break
            segment_length = int.from_bytes(data[offset:offset + 2], "big")
            if segment_length < 2 or offset + segment_length > len(data):
                break
            if marker in sof_markers:
                if segment_length < 8 or offset + 8 > len(data):
                    break
                component_count = data[offset + 7]
                if component_count == 0 or segment_length < 8 + 3 * component_count:
                    break
                height = int.from_bytes(data[offset + 3:offset + 5], "big")
                width = int.from_bytes(data[offset + 5:offset + 7], "big")
                break
            offset += segment_length
        if not width or not height:
            raise RequestError(400, "JPEG dimensions are missing or invalid.")
    elif media_type == "image/webp":
        if len(data) < 20 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
            raise RequestError(400, "Image content does not match its WebP type.")
        riff_length = int.from_bytes(data[4:8], "little") + 8
        if riff_length > len(data) or riff_length < 12:
            raise RequestError(400, "WebP container length is invalid.")
        width = height = 0
        offset = 12
        scan_limit = min(riff_length, 1024 * 1024)
        while offset + 8 <= scan_limit:
            chunk_type = data[offset:offset + 4]
            chunk_length = int.from_bytes(data[offset + 4:offset + 8], "little")
            payload_start = offset + 8
            payload_end = payload_start + chunk_length
            if payload_end > riff_length:
                break
            payload = data[payload_start:payload_end]
            if chunk_type == b"VP8X" and len(payload) >= 10:
                width = 1 + int.from_bytes(payload[4:7], "little")
                height = 1 + int.from_bytes(payload[7:10], "little")
                break
            if chunk_type == b"VP8 " and len(payload) >= 10 and payload[3:6] == b"\x9d\x01\x2a":
                width = int.from_bytes(payload[6:8], "little") & 0x3FFF
                height = int.from_bytes(payload[8:10], "little") & 0x3FFF
                break
            if chunk_type == b"VP8L" and len(payload) >= 5 and payload[0] == 0x2F:
                bits = int.from_bytes(payload[1:5], "little")
                width = (bits & 0x3FFF) + 1
                height = ((bits >> 14) & 0x3FFF) + 1
                break
            offset = payload_end + (chunk_length & 1)
        if not width or not height:
            raise RequestError(400, "WebP dimensions are missing or invalid.")
    else:
        raise RequestError(415, "Unsupported image type.")

    if width <= 0 or height <= 0 or width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION or width * height > MAX_IMAGE_PIXELS:
        raise RequestError(413, "Image dimensions exceed the 12-megapixel limit.")
    return width, height


def _validate_audio_container(data, media_type):
    signatures = {
        "audio/webm": data.startswith(b"\x1a\x45\xdf\xa3"),
        "audio/ogg": data.startswith(b"OggS"),
        "audio/wav": len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WAVE",
        "audio/x-wav": len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WAVE",
        "audio/mp4": len(data) >= 12 and data[4:8] == b"ftyp",
    }
    if not signatures.get(media_type, False):
        raise RequestError(400, "Audio content does not match its declared media type.")

SKILL_MAP = {
    "core": [
        "talk",
        "memory",
        "day",
        "projects",
        "token-scout",
        "adapt",
        "how-i-help",
        "use-the-skills",
        "usecomputer",
        "desktop-controller",
        "powershell-windows-cli",
        "deepresearch",
        "doc-to-skill",
    ],
    "code": ["addyosmani set", "superpowers", "mattpocock", "ponytail", "sentry", "vercel", "python-debugging", "pytest-testing"],
    "aura": ["unity-cli", "unity gameplay", "android builds"],
    "wally": ["dotnet skills", "aaron csharp skills"],
    "mike": ["youtube-outliers", "youtube", "ffmpeg-skill", "remotion-captions", "hyperframes-media", "voiceover-pipeline", "whop"],
    "jobs": ["claim-check", "resume-tailor", "gws-gmail draft only"],
    "chatter": ["CHATTER-MASTER", "night-shift-reply", "adults-only"],
    "cutie": ["screenshot coach", "owned cards", "late surger"],
}


def search_notes(query):
    query = query.strip().lower()
    if not query:
        return []
    hits = []
    roots = [ROOT / "skills", ROOT / "profiles", ROOT / "vault", DATA]
    for folder in roots:
        if not folder.exists():
            continue
        for path in folder.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".md", ".json", ".txt"}:
                continue
            if "backups" in path.parts or "skill-history" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if query in text.lower() or query in path.name.lower():
                line = next((ln.strip() for ln in text.splitlines() if query in ln.lower()), "")
                hits.append({"path": str(path), "line": line[:180]})
            if len(hits) >= 30:
                return hits
    return hits


def make_backup():
    ensure_dirs()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = BACKUPS / f"ella-{stamp}.zip"
    include = [
        DATA / "profile.json",
        DATA / "memory.json",
        DATA / "activity.json",
        DATA / "checkin.json",
        DATA / "free-models.json",
        DATA / "outbox.json",
        ROOT / "skills" / "mine" / "how-i-help.md",
    ]
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in include:
            if path.exists():
                archive.write(path, path.name)
    add_activity("backup", dest.name)
    return dest.name


def restore_backup(name):
    if not isinstance(name, str) or not re.fullmatch(r"ella-\d{8}-\d{6}\.zip", name):
        return {"ok": False, "error": "backup not found"}
    src = (BACKUPS / name).resolve()
    if src.parent != BACKUPS.resolve() or not src.is_file():
        return {"ok": False, "error": "backup not found"}
    make_backup()
    allowed = {
        "profile.json": DATA / "profile.json",
        "memory.json": DATA / "memory.json",
        "activity.json": DATA / "activity.json",
        "checkin.json": DATA / "checkin.json",
        "free-models.json": DATA / "free-models.json",
        "outbox.json": DATA / "outbox.json",
        "how-i-help.md": ROOT / "skills" / "mine" / "how-i-help.md",
    }
    with zipfile.ZipFile(src) as archive:
        for info in archive.infolist():
            target = allowed.get(Path(info.filename).name)
            if target is None:
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(info))
    add_activity("restore", name)
    return {"ok": True, "name": name}


def setup_checks():
    env = load_env()
    ollama = False
    base = (env.get("OLLAMA_URL") or "http://127.0.0.1:11434").rstrip("/")
    try:
        with urllib.request.urlopen(base + "/api/tags", timeout=2) as res:
            ollama = res.status == 200
    except Exception:
        ollama = False
    has_key = bool(env.get("OPENROUTER_API_KEY") or env.get("GROQ_API_KEY"))
    jarvis_paths = [
        Path.home() / "AppData" / "Local" / "Programs" / "ella" / "Ella.exe",
        Path.home() / "AppData" / "Local" / "Ella" / "Ella.exe",
        Path(r"C:\Program Files\Ella\Ella.exe"),
    ]
    return [
        {"name": "panel", "ok": True, "detail": f"http://{HOST}:{PORT}"},
        {"name": "model", "ok": has_key or ollama, "detail": "OpenRouter, Groq, or Ollama"},
        {"name": "opencode", "ok": shutil.which("opencode") is not None, "detail": "coder, optional for the panel"},
        {"name": "ella.exe", "ok": any(path.exists() for path in jarvis_paths), "detail": "desktop app, optional"},
    ]


def maybe_missed_checkin():
    def work():
        person = profile()
        if not person.get("setup_done"):
            return
        today = datetime.now().strftime("%Y-%m-%d")
        stamp = read_json(DATA / "checkin.json", {}).get("at") or ""
        if stamp.startswith(today):
            return
        if read_json(DATA / "missed.json", {}).get("day") == today:
            return
        raw = (person.get("checkin") or "09:00").split(":")
        try:
            hour, minute = int(raw[0]), int(raw[1])
        except (ValueError, IndexError):
            hour, minute = 9, 0
        now = datetime.now()
        if (now.hour, now.minute) < (hour, minute):
            return
        write_json(DATA / "missed.json", {"day": today})
        run_locked(check_in)

    threading.Thread(target=work, daemon=True).start()


def brain_file():
    return read_json(DATA / "brain.json", {"mode": "local", "model": "llama3.2:3b"})


def local_model_names():
    try:
        return ollama_models(load_env())
    except Exception:
        return []


def save_brain(body):
    body = _require_object(body)
    _validate_keys(body, {"mode", "model"})
    current = brain_file()
    mode = body.get("mode") or current.get("mode") or "local"
    if not isinstance(mode, str) or mode not in {"local", "cloud"}:
        raise RequestError(400, "Mode must be local or cloud.")
    model = body.get("model") or current.get("model") or "llama3.2:3b"
    if not isinstance(model, str) or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", model.strip()):
        raise RequestError(400, "Invalid model name.")
    model = model.strip()
    payload = {"mode": mode, "model": model}
    write_json(DATA / "brain.json", payload)
    add_activity("brain", f"{mode} {model}")
    return payload


def state():
    person = profile()
    facts = read_json(DATA / "memory.json", {"facts": []}).get("facts") or []
    return {
        "profile": person,
        "facts": facts[-30:],
        "checkin": read_json(DATA / "checkin.json", {}),
        "activity": read_json(DATA / "activity.json", [])[:20],
        "quota": read_json(DATA / "quota.json", {"remaining": None, "provider": ""}),
        "models": len(read_json(DATA / "free-models.json", {}).get("models") or []),
        "free_models": [
            {"id": m.get("id") or "", "name": m.get("name") or m.get("id") or ""}
            for m in (read_json(DATA / "free-models.json", {}).get("models") or [])[:24]
            if isinstance(m, dict)
        ],
        "usage": usage_summary(),
        "outbox": len(read_json(DATA / "outbox.json", [])),
        "backups": sorted(p.name for p in BACKUPS.glob("*.zip"))[-8:],
        "skills": SKILL_MAP,
        "stopped": (DATA / "stop.flag").exists(),
        "projects": list_projects(),
        "setup": setup_checks(),
        "today": today_text()[:1500],
        "brain": brain_file(),
        "local_models": local_model_names(),
    }


def save_profile(body):
    body = _require_object(body)
    _validate_keys(body, {"name", "timezone", "does", "checkin", "fact"})
    limits = {"name": 120, "timezone": 128, "does": 2000, "checkin": 5, "fact": 1000}
    for key, maximum in limits.items():
        if key in body:
            value = _require_string(body[key], key, maximum, allow_empty=(key != "checkin"))
            if key == "checkin" and not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", value):
                raise RequestError(400, "Check-in time must use HH:MM (24-hour time).")
    current = profile()
    current.update(
        {
            "name": (body.get("name") or current.get("name") or "").strip(),
            "timezone": (body.get("timezone") or "Asia/Manila").strip(),
            "does": (body.get("does") or "").strip(),
            "checkin": (body.get("checkin") or "09:00").strip(),
            "setup_done": True,
        }
    )
    write_json(DATA / "profile.json", current)
    fact = (body.get("fact") or "").strip()
    if fact:
        mem = read_json(DATA / "memory.json", {"facts": []})
        mem["facts"] = (mem.get("facts") or [])[-29:] + [{"at": now_iso(), "text": fact}]
        write_json(DATA / "memory.json", mem)
    add_activity("profile", "profile saved")
    return current


def load_projects():
    if PROJECTS_FILE.exists():
        try:
            projects = json.loads(PROJECTS_FILE.read_text(encoding="utf-8"))
            return _validate_projects(projects)
        except Exception:
            pass
    return []


def save_projects(projects):
    projects = _validate_projects(projects)
    PROJECTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROJECTS_FILE.write_text(json.dumps(projects, indent=2), encoding="utf-8")


def project_session_path(project_id):
    safe = _project_id(project_id)
    try:
        root = ROOT.resolve()
        sessions = SESSIONS.resolve()
        sessions.relative_to(root)
        target = (sessions / f"project-{safe}.json").resolve()
        target.relative_to(sessions)
    except (OSError, RuntimeError, ValueError):
        raise RequestError(400, "Project session path is invalid.") from None
    return target


def load_project_session(project_id):
    path = project_session_path(project_id)
    return read_json(path, {"messages": []})


def save_project_session(project_id, session):
    SESSIONS.mkdir(parents=True, exist_ok=True)
    path = project_session_path(project_id)
    payload = session if isinstance(session, dict) else {"messages": []}
    locked_update(path, {"messages": []}, lambda _: payload)


def append_project_session(project_id, user_msg, ella_msg):
    """Append a successful turn under lock so concurrent asks cannot drop messages."""
    SESSIONS.mkdir(parents=True, exist_ok=True)
    path = project_session_path(project_id)

    def transform(session):
        msgs = list((session or {}).get("messages") or [])
        msgs.append(user_msg)
        msgs.append(ella_msg)
        if len(msgs) > 100:
            msgs = msgs[-100:]
        return {"messages": msgs}

    return locked_update(path, {"messages": []}, transform)


def run_vision(text, image_data_url):
    """Send image + text to moondream via Ollama for vision analysis."""
    used_model = "moondream:latest"
    usage = {
        "provider": "ollama",
        "model": used_model,
        "prompt": 0,
        "completion": 0,
        "total": 0,
        "tps": 0,
    }
    try:
        raw = image_data_url.split(",", 1)[1]
        payload = json.dumps({
            "model": used_model,
            "prompt": text,
            "images": [raw],
            "stream": False,
        }).encode()
        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as r:
            resp = json.loads(r.read())
        # Prefer what Ollama reports it actually ran.
        usage["model"] = (resp.get("model") or used_model).strip() or used_model
        prompt = int(resp.get("prompt_eval_count") or 0)
        completion = int(resp.get("eval_count") or 0)
        dur = resp.get("eval_duration") or 0
        usage["prompt"] = max(0, prompt)
        usage["completion"] = max(0, completion)
        usage["total"] = usage["prompt"] + usage["completion"]
        if dur and completion:
            usage["tps"] = round(completion / (dur / 1e9), 1)
        reply = resp.get("response") or ""
        if not reply:
            return "", "I couldn't make sense of that image. Try a clearer screenshot.", usage
        return reply.strip(), None, usage
    except Exception as exc:
        log_line(f"vision request failed: {type(exc).__name__}")
        return "", "Image analysis failed. Check the local vision model and try again.", usage


def ask(body):
    body = _require_object(body)
    _validate_keys(body, {"text", "project", "image"})
    text = _require_string(body.get("text", ""), "Message", MAX_CHAT_TEXT_CHARS, allow_empty=True).strip()
    project_id = body.get("project", "")
    if project_id:
        project_id = _project_id(project_id)

    if not text:
        if not body.get("image"):
            raise RequestError(400, "Message text or an image is required.")

    image = body.get("image", "")
    if not isinstance(image, str):
        raise RequestError(400, "Image must be encoded image data.")
    if image:
        if len(image) > MAX_IMAGE_DATA_URL_CHARS:
            raise RequestError(413, "Image is too large or invalid.")
        match = re.fullmatch(r"data:image/(png|jpeg|webp);base64,([A-Za-z0-9+/]*={0,2})", image, re.IGNORECASE)
        if not match:
            raise RequestError(400, "Image must be PNG, JPEG, or WebP data encoded as base64.")
        try:
            decoded = base64.b64decode(match.group(2), validate=True)
        except (ValueError, binascii.Error):
            raise RequestError(400, "Image data is malformed.") from None
        if not decoded or len(decoded) > MAX_IMAGE_BYTES:
            raise RequestError(413, "Image is empty or exceeds the 12 MiB limit.")
        _image_dimensions(decoded, f"image/{match.group(1).lower()}")

    if not text:
        text = "What do you see in this image?"

    if project_id:
        return ask_project(text, project_id, image=image)

    low = text.lower()
    if low in {"stop", "stop."}:
        ensure_dirs()
        (DATA / "stop.flag").write_text(now_iso(), encoding="utf-8")
        add_activity("screen", "stop set")
        return {"ok": True, "text": "Stop is on. Nothing gets clicked."}
    if low in {"check in", "check-in", "good morning"}:
        return check_in()
    if low == "backup":
        return {"ok": True, "text": f"Backup saved. {make_backup()}"}
    usage = None
    if image:
        reply, error, usage = run_vision(text, image)
        if reply and usage:
            # Vision bypasses run_model; still log actual provider+model+tokens.
            usage = record_usage(usage.get("provider") or "ollama", usage, "vision")
    else:
        reply, error, usage = run_model("chat", text)
    if error or not reply:
        return {"ok": False, "error": error or "No model answered"}
    add_activity("ask", reply.splitlines()[0][:160])
    return {"ok": True, "text": reply, "usage": usage, "usage_summary": usage_summary()}


def load_skill(name):
    """Load a SKILL.md file by folder name from the skills directory."""
    try:
        component = _safe_component(name, "skill name")
        base = SKILLS_DIR.resolve()
        path = (base / component / "SKILL.md").resolve()
        path.relative_to(base)
    except (RequestError, OSError, RuntimeError, ValueError):
        return ""
    if path.exists():
        try:
            text = path.read_text(encoding="utf-8")
            if len(text) > 2000:
                text = text[:2000]
            return text
        except Exception:
            pass
    return ""


def load_brain_file(name):
    """Load a brain/*.md file by name. Cap at 4000 chars to fit context."""
    path = _safe_markdown_path(BRAIN_DIR, name, "brain file")
    if path and path.is_file():
        try:
            text = path.read_text(encoding="utf-8")
            if len(text) > 4000:
                text = text[:4000] + "\n[truncated]"
            return text
        except Exception:
            pass
    return ""


def load_profile(name):
    """Load a profile .md file."""
    path = _safe_markdown_path(PROFILES_DIR, name, "profile name")
    if path and path.is_file():
        try:
            text = path.read_text(encoding="utf-8")
            if len(text) > 2000:
                text = text[:2000]
            return text
        except Exception:
            pass
    return ""


def build_project_prompt(proj):
    """Build a full system prompt from the project config + loaded skills + brain + profile + links."""
    base = proj.get("prompt") or ""
    parts = [base]

    # Load profile if specified
    profile_name = proj.get("profile")
    if profile_name:
        content = load_profile(profile_name)
        if content:
            parts.append(f"\n--- Profile ---\n{content}")

    # Load brain files if specified
    brain_names = proj.get("brain_files") or []
    for name in brain_names:
        content = load_brain_file(name)
        if content:
            parts.append(f"\n--- Brain: {name} ---\n{content}")

    # Load skills
    skill_names = proj.get("skills") or []
    for name in skill_names:
        content = load_skill(name)
        if content:
            parts.append(f"\n--- Skill: {name} ---\n{content}")

    # Include linked resources
    links = proj.get("links") or []
    if links:
        link_lines = [f"- {lnk.get('label','')}: {lnk.get('url','')}" for lnk in links if lnk.get("url")]
        if link_lines:
            parts.append("\n--- Linked Resources ---\n" + "\n".join(link_lines))

    return "\n".join(parts)


def ask_project(text, project_id, image=""):
    project_id = _project_id(project_id)
    projects = load_projects()
    proj = next((p for p in projects if p.get("id") == project_id), None)
    if not proj:
        raise RequestError(404, "Project not found.")

    session = load_project_session(project_id)
    messages = list(session.get("messages") or [])

    # Build model history from THIS project's session only — never main chat.
    prior = []
    for m in messages:
        content = (m.get("text") or "").strip()
        if not content:
            continue
        role = m.get("role") or "user"
        if role in ("ella", "assistant"):
            prior.append({"role": "assistant", "content": content})
        else:
            prior.append({"role": "user", "content": content})
    prior = prior[-10:]

    usage = None
    if image:
        reply, error, usage = run_vision(text, image)
        if reply and usage:
            usage = record_usage(usage.get("provider") or "ollama", usage, "vision")
    else:
        full_prompt = build_project_prompt(proj)
        reply, error, usage = run_model(
            "chat", text, project_prompt=full_prompt, history=prior
        )
    if error or not reply:
        return {"ok": False, "error": error or "No model answered"}

    user_msg = {"role": "user", "text": text, "at": now_iso()}
    ella_msg = {"role": "ella", "text": reply, "at": now_iso()}
    append_project_session(project_id, user_msg, ella_msg)
    add_activity("project", f"{proj['name']}: {reply.splitlines()[0][:80]}")
    return {"ok": True, "text": reply, "project": project_id, "usage": usage, "usage_summary": usage_summary()}


def run_locked(fn):
    if not LOCK.acquire():
        return {"ok": False, "error": "another routine is already running"}
    try:
        return fn()
    finally:
        LOCK.release()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def setup(self):
        super().setup()
        self.connection.settimeout(HEADER_READ_TIMEOUT_SECONDS)

    def parse_request(self):
        self.connection.settimeout(HEADER_READ_TIMEOUT_SECONDS)
        try:
            if not super().parse_request():
                return False
        except (socket.timeout, TimeoutError):
            self.close_connection = True
            try:
                self._send(408, {"ok": False, "error": "Request headers timed out."})
            except OSError:
                pass
            return False
        self.connection.settimeout(None)
        if len(self.path) > MAX_REQUEST_TARGET_CHARS:
            self.close_connection = True
            self.send_error(414)
            return False
        try:
            self._validate_host()
        except RequestError as exc:
            self.close_connection = True
            self._send(exc.status, {"ok": False, "error": exc.message})
            return False
        return True

    def _validate_host(self):
        values = self.headers.get_all("Host") or []
        if len(values) != 1:
            raise RequestError(400, "A single valid local Host header is required.")
        value = values[0]
        if value.strip() != value or value.lower() not in {f"{name}:{PORT}" for name in ALLOWED_HOSTS}:
            raise RequestError(400, "Host must be localhost or 127.0.0.1 on Ella's port.")
        self._host_name = value.rsplit(":", 1)[0].lower()

    def _send(self, code, body, content_type="application/json; charset=utf-8", extra_headers=None):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data: blob:; media-src 'self' blob:; "
            "connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'",
        )
        for name, value in (extra_headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(data)

    def send_error(self, code, message=None, explain=None):
        if code == 501:
            code = 405
        if code == 405:
            self.close_connection = True
        try:
            phrase = HTTPStatus(code).phrase
        except ValueError:
            code, phrase = 500, "Internal server error"
        headers = {"Allow": "GET, POST"} if code == 405 else None
        self._send(code, {"ok": False, "error": phrase}, extra_headers=headers)

    def _authorize_api(self):
        origins = self.headers.get_all("Origin") or []
        if len(origins) > 1:
            raise RequestError(403, "Origin rejected.", close=True)
        if origins:
            origin = origins[0]
            try:
                parsed = urlparse(origin)
                valid_origin = (
                    parsed.scheme == "http"
                    and parsed.hostname == self._host_name
                    and parsed.port == PORT
                    and not parsed.username
                    and not parsed.password
                    and not parsed.path
                    and not parsed.params
                    and not parsed.query
                    and not parsed.fragment
                    and parsed.netloc.lower() == f"{self._host_name}:{PORT}"
                )
            except ValueError:
                valid_origin = False
            if not valid_origin:
                raise RequestError(403, "Origin rejected.", close=True)

        fetch_sites = self.headers.get_all("Sec-Fetch-Site") or []
        if len(fetch_sites) > 1 or (fetch_sites and fetch_sites[0].lower() == "cross-site"):
            raise RequestError(403, "Cross-site API requests are not allowed.", close=True)
        if fetch_sites and fetch_sites[0].lower() not in {"same-origin", "same-site", "none"}:
            raise RequestError(403, "Fetch metadata rejected.", close=True)

        tokens = self.headers.get_all("X-Ella-Request-Token") or []
        if len(tokens) != 1 or not hmac.compare_digest(tokens[0], API_TOKEN):
            raise RequestError(401, "Ella request authorization failed. Reload the panel and try again.", close=True)

    def _request_path(self):
        if not self.path.startswith("/") or self.path.startswith("//"):
            raise RequestError(400, "Only local origin-form request targets are supported.", close=True)
        try:
            return urlparse(self.path)
        except ValueError:
            raise RequestError(400, "Malformed request target.") from None

    def _reject_get_body(self):
        if self.headers.get_all("Transfer-Encoding"):
            raise RequestError(400, "GET request bodies are not supported.", close=True)
        lengths = self.headers.get_all("Content-Length") or []
        if len(lengths) > 1:
            raise RequestError(400, "Invalid Content-Length.", close=True)
        if lengths and lengths[0].strip() != "0":
            raise RequestError(400, "GET request bodies are not supported.", close=True)

    def _read_body(self, max_bytes, content_types, allow_empty=False):
        transfer_encoding = self.headers.get_all("Transfer-Encoding") or []
        if transfer_encoding:
            raise RequestError(400, "Transfer-encoded request bodies are not supported.", close=True)
        encodings = self.headers.get_all("Content-Encoding") or []
        if len(encodings) > 1 or (encodings and encodings[0].lower() != "identity"):
            raise RequestError(415, "Encoded request bodies are not supported.", close=True)

        lengths = self.headers.get_all("Content-Length") or []
        if len(lengths) != 1 or not re.fullmatch(r"(?:0|[1-9][0-9]{0,8})", lengths[0].strip()):
            raise RequestError(400, "A single valid Content-Length header is required.", close=True)
        length = int(lengths[0])
        if length > max_bytes:
            raise RequestError(413, "Request body exceeds this route's size limit.", close=True)
        if length == 0 and not allow_empty:
            raise RequestError(400, "Request body is required.")

        types = self.headers.get_all("Content-Type") or []
        if len(types) != 1:
            raise RequestError(415, "A supported Content-Type is required.", close=True)
        media_type = types[0].split(";", 1)[0].strip().lower()
        if media_type not in content_types:
            raise RequestError(415, "Unsupported Content-Type.", close=True)
        if media_type == "application/json":
            parameters = types[0].split(";")[1:]
            for parameter in parameters:
                if parameter.strip() and parameter.strip().lower().replace('"', "") != "charset=utf-8":
                    raise RequestError(415, "JSON requests must use UTF-8 encoding.", close=True)

        deadline = time.monotonic() + BODY_READ_TIMEOUT_SECONDS
        chunks = []
        remaining = length
        try:
            while remaining:
                time_left = deadline - time.monotonic()
                if time_left <= 0:
                    raise RequestError(408, "Request body read timed out.", close=True)
                self.connection.settimeout(time_left)
                chunk = self.rfile.read1(min(64 * 1024, remaining))
                if not chunk:
                    raise RequestError(400, "Request body ended before Content-Length.", close=True)
                chunks.append(chunk)
                remaining -= len(chunk)
        except (socket.timeout, TimeoutError):
            raise RequestError(408, "Request body read timed out.", close=True) from None
        finally:
            try:
                self.connection.settimeout(None)
            except OSError:
                self.close_connection = True
        raw = b"".join(chunks)
        return raw, media_type

    @staticmethod
    def _unique_json_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def _read_json(self, max_bytes=MAX_JSON_BYTES):
        raw, _media_type = self._read_body(max_bytes, {"application/json"})
        try:
            data = json.loads(raw.decode("utf-8"), object_pairs_hook=self._unique_json_object)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError, RecursionError):
            raise RequestError(400, "Request body must contain valid UTF-8 JSON.") from None
        return _require_object(data)

    def _query_value(self, parsed, name, maximum=MAX_SEARCH_QUERY_CHARS):
        try:
            params = parse_qs(parsed.query, keep_blank_values=True, max_num_fields=8)
        except ValueError:
            raise RequestError(400, "Invalid query string.") from None
        if set(params) - {name} or len(params.get(name, [])) > 1:
            raise RequestError(400, "Invalid query parameters.")
        value = (params.get(name) or [""])[0]
        return _require_string(value, "Query", maximum, allow_empty=True)

    def _send_result(self, result, failure_status=502, failure_message=None):
        if isinstance(result, dict) and result.get("ok") is False:
            status = 409 if result.get("error") == "another routine is already running" else failure_status
            if failure_message and status != 409:
                result = dict(result)
                result["error"] = failure_message
            self._send(status, result)
        else:
            self._send(200, result)

    def _unexpected_error(self, exc):
        try:
            log_line(f"API request failed: {self.command} {type(exc).__name__}")
        except Exception:
            pass
        try:
            self._send(500, {"ok": False, "error": "Ella could not complete this request."})
        except OSError:
            self.close_connection = True

    def do_GET(self):
        try:
            parsed = self._request_path()
            path = parsed.path
            self._reject_get_body()
            if path == "/api" or path.startswith("/api/"):
                self._authorize_api()
            if path in POST_ROUTES:
                self.close_connection = True
                self._send(405, {"ok": False, "error": "Method not allowed."}, extra_headers={"Allow": "POST"})
                return
            if path not in GET_ROUTES:
                self._send(404, {"ok": False, "error": "Not found."})
                return
            if path in {"/", "/index.html"}:
                page = (WEB / "index.html").read_bytes()
                page = page.replace(b"__ELLA_REQUEST_TOKEN__", API_TOKEN.encode("ascii"))
                self._send(200, page, "text/html; charset=utf-8")
            elif path == "/app.js":
                self._send(200, (WEB / "app.js").read_bytes(), "text/javascript; charset=utf-8")
            elif path == "/styles.css":
                self._send(200, (WEB / "styles.css").read_bytes(), "text/css; charset=utf-8")
            elif path == "/api/state":
                self._send(200, state())
            elif path == "/api/search":
                self._send(200, {"hits": search_notes(self._query_value(parsed, "q"))})
            elif path == "/api/graph":
                self._send(200, {"notes": graph()})
            elif path == "/api/note":
                self._send(200, find_note(self._query_value(parsed, "q")))
        except RequestError as exc:
            if exc.close:
                self.close_connection = True
            self._send(exc.status, {"ok": False, "error": exc.message})
        except Exception as exc:
            self._unexpected_error(exc)

    def do_POST(self):
        try:
            parsed = self._request_path()
            path = parsed.path
            if path == "/api" or path.startswith("/api/"):
                self._authorize_api()
            if path in GET_ROUTES:
                self.close_connection = True
                self._send(405, {"ok": False, "error": "Method not allowed."}, extra_headers={"Allow": "GET"})
                return
            if path not in POST_ROUTES:
                self.close_connection = True
                self._send(404, {"ok": False, "error": "Not found."})
                return

            if path == "/api/stt":
                raw, media_type = self._read_body(
                    MAX_STT_BYTES,
                    {"audio/webm", "audio/ogg", "audio/wav", "audio/x-wav", "audio/mp4"},
                )
                suffix = {
                    "audio/webm": ".webm", "audio/ogg": ".ogg", "audio/wav": ".wav",
                    "audio/x-wav": ".wav", "audio/mp4": ".mp4",
                }[media_type]
                _validate_audio_container(raw, media_type)
                result = transcribe(raw, suffix)
                if not result.get("ok"):
                    error = result.get("error", "")
                    if error.startswith("Speech-to-text failed:"):
                        log_line("speech transcription failed")
                        result = {"ok": False, "error": "Speech-to-text is unavailable. Check the local speech setup."}
                        self._send(503, result)
                    else:
                        self._send(422, result)
                else:
                    self._send(200, result)
                return

            if path == "/api/tts":
                body = self._read_json()
                _validate_keys(body, {"text"})
                text = _require_string(body.get("text"), "Text", MAX_TTS_TEXT_CHARS)
                result = synthesize(text)
                if not result.get("ok"):
                    self._send(503, {"ok": False, "error": "Speech synthesis is unavailable. Check the local voice setup."})
                else:
                    self._send(200, result["audio"], "audio/wav")
                return

            if path == "/api/profile":
                self._send(200, {"ok": True, "profile": save_profile(self._read_json())})
                return
            if path in {"/api/checkin", "/api/scout", "/api/adapt", "/api/outbox", "/api/backup", "/api/stop"}:
                body = self._read_json()
                _validate_keys(body, set())
                if path == "/api/checkin":
                    self._send_result(run_locked(check_in), 503, "Check-in failed. Check the local model service and try again.")
                elif path == "/api/scout":
                    self._send_result(run_locked(scout_now), 503, "Model catalog refresh failed. Check network availability and try again.")
                elif path == "/api/adapt":
                    self._send_result(run_locked(adapt), 503, "The skill update could not be completed.")
                elif path == "/api/outbox":
                    self._send_result(run_locked(retry_outbox), 503, "The retry task could not be completed.")
                elif path == "/api/backup":
                    self._send(200, {"ok": True, "name": make_backup()})
                else:
                    ensure_dirs()
                    flag = DATA / "stop.flag"
                    if flag.exists():
                        flag.unlink()
                        add_activity("screen", "stop cleared")
                        self._send(200, {"ok": True, "stopped": False})
                    else:
                        flag.write_text(now_iso(), encoding="utf-8")
                        add_activity("screen", "stop set")
                        log_line("screen stop set")
                        self._send(200, {"ok": True, "stopped": True})
                return

            if path == "/api/restore":
                body = self._read_json()
                _validate_keys(body, {"name"})
                name = _require_string(body.get("name"), "Backup name", 32)
                result = restore_backup(name)
                self._send(200 if result.get("ok") else 404, result)
                return

            if path == "/api/ask":
                body = self._read_json(MAX_ASK_BYTES)
                self._send_result(
                    run_locked(lambda: ask(body)),
                    failure_message="Model request failed. Check the selected provider and local service.",
                )
                return

            if path == "/api/projects":
                self._handle_projects(self._read_json())
                return

            if path == "/api/brain":
                self._send(200, {"ok": True, "brain": save_brain(self._read_json())})
                return
        except RequestError as exc:
            if exc.close:
                self.close_connection = True
            self._send(exc.status, {"ok": False, "error": exc.message})
        except Exception as exc:
            self._unexpected_error(exc)

    def _handle_projects(self, body):
        action = body.get("action", "list")
        if not isinstance(action, str):
            raise RequestError(400, "Project action must be a string.")
        if action == "list":
            _validate_keys(body, {"action"})
            self._send(200, {"ok": True, "projects": load_projects()})
        elif action == "save":
            _validate_keys(body, {"action", "projects"})
            save_projects(body.get("projects"))
            self._send(200, {"ok": True})
        elif action == "add":
            _validate_keys(body, {"action", "project"})
            project = _validate_project(body.get("project"))
            projects = [item for item in load_projects() if item["id"] != project["id"]]
            projects.append(project)
            save_projects(projects)
            self._send(200, {"ok": True, "projects": projects})
        elif action in {"session", "clear_session", "update"}:
            allowed = {"action", "project_id"} | ({"updates"} if action == "update" else set())
            _validate_keys(body, allowed)
            project_id = _project_id(body.get("project_id"))
            projects = load_projects()
            index = next((i for i, project in enumerate(projects) if project["id"] == project_id), None)
            if index is None:
                raise RequestError(404, "Project not found.")
            if action == "session":
                self._send(200, {"ok": True, "session": load_project_session(project_id)})
            elif action == "clear_session":
                save_project_session(project_id, {"messages": []})
                self._send(200, {"ok": True})
            else:
                updates = _require_object(body.get("updates"), "Project updates")
                _validate_keys(updates, {"links", "actions", "prompt", "name", "color", "icon"})
                project = dict(projects[index])
                project.update(updates)
                projects[index] = _validate_project(project)
                save_projects(projects)
                self._send(200, {"ok": True, "projects": projects})
        else:
            raise RequestError(400, "Unknown project action.")

    def _method_not_allowed(self):
        self.close_connection = True
        self._send(
            405,
            {"ok": False, "error": "Method not allowed."},
            extra_headers={"Allow": "GET, POST"},
        )

    def do_PUT(self):
        self._method_not_allowed()

    def do_PATCH(self):
        self._method_not_allowed()

    def do_DELETE(self):
        self._method_not_allowed()

    def do_OPTIONS(self):
        self._method_not_allowed()

    def do_HEAD(self):
        self._method_not_allowed()

    def do_TRACE(self):
        self._method_not_allowed()

    def do_CONNECT(self):
        self._method_not_allowed()


def main():
    ensure_dirs()
    if not (DATA / "profile.json").exists():
        write_json(
            DATA / "profile.json",
            {
                "name": "",
                "timezone": "Asia/Manila",
                "does": "",
                "checkin": "09:00",
                "setup_done": False,
            },
        )
    if not (DATA / "memory.json").exists():
        write_json(DATA / "memory.json", {"facts": []})
    if not (DATA / "brain.json").exists():
        write_json(DATA / "brain.json", {"mode": "local", "model": "llama3.2:3b"})
    log_line("server start")
    threading.Thread(target=tts_warmup, daemon=True).start()
    maybe_missed_checkin()
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Ella at http://{HOST}:{PORT}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
