"""Ella — local AI assistant. Listens on 127.0.0.1 only."""

import json
import shutil
import threading
import urllib.request
import zipfile
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from projects import list_projects
from routines import adapt, check_in, profile, retry_outbox, run_model, scout_now, usage_summary
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
    log_line,
    now_iso,
    read_json,
    write_json,
)

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
HOST = "127.0.0.1"
PORT = 8765
LOCK = RoutineLock()
SESSIONS = DATA / "sessions"
PROJECTS_FILE = ROOT / "bots" / "projects.json"
SKILLS_DIR = ROOT / "skills"
BRAIN_DIR = Path("C:/Users/USER/fckkk/brain")
PROFILES_DIR = ROOT / "profiles"

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
    src = (BACKUPS / name).resolve()
    if src.parent != BACKUPS.resolve() or not src.exists() or src.suffix != ".zip":
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
    current = brain_file()
    mode = body.get("mode") or current.get("mode") or "local"
    if mode not in {"local", "cloud"}:
        mode = "local"
    model = (body.get("model") or current.get("model") or "llama3.2:3b").strip()
    safe = model.replace(".", "").replace(":", "").replace("-", "").replace("_", "")
    if not model or not safe.isalnum():
        model = current.get("model") or "llama3.2:3b"
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
            return json.loads(PROJECTS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def save_projects(projects):
    PROJECTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROJECTS_FILE.write_text(json.dumps(projects, indent=2), encoding="utf-8")


def project_session_path(project_id):
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in project_id)
    return SESSIONS / f"project-{safe}.json"


def load_project_session(project_id):
    path = project_session_path(project_id)
    return read_json(path, {"messages": []})


def save_project_session(project_id, session):
    SESSIONS.mkdir(parents=True, exist_ok=True)
    write_json(project_session_path(project_id), session)


def run_vision(text, image_data_url):
    """Send image + text to moondream via Ollama for vision analysis."""
    import base64 as b64
    try:
        raw = image_data_url
        if "," in raw:
            raw = raw.split(",", 1)[1]
        payload = json.dumps({
            "model": "moondream:latest",
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
        reply = resp.get("response") or ""
        if not reply:
            return "", "I couldn't make sense of that image. Try a clearer screenshot."
        return reply.strip(), None
    except Exception as exc:
        return "", f"Vision error: {exc}"


def ask(body):
    text = (body.get("text") or "").strip()
    project_id = (body.get("project") or "").strip()

    if not text:
        return {"ok": False, "error": "Say what you want done."}

    image = (body.get("image") or "").strip()

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
        reply, error = run_vision(text, image)
    else:
        reply, error, usage = run_model("chat", text)
    if error or not reply:
        return {"ok": False, "error": error or "No model answered"}
    add_activity("ask", reply.splitlines()[0][:160])
    return {"ok": True, "text": reply, "usage": usage, "usage_summary": usage_summary()}


def load_skill(name):
    """Load a SKILL.md file by folder name from the skills directory."""
    path = SKILLS_DIR / name / "SKILL.md"
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
    path = BRAIN_DIR / name
    if not path.suffix:
        path = path.with_suffix(".md")
    if path.exists():
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
    path = PROFILES_DIR / name
    if not path.suffix:
        path = path.with_suffix(".md")
    if path.exists():
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
    projects = load_projects()
    proj = next((p for p in projects if p.get("id") == project_id), None)
    if not proj:
        return {"ok": False, "error": f"Unknown project: {project_id}"}

    session = load_project_session(project_id)
    messages = session.get("messages") or []
    messages.append({"role": "user", "text": text, "at": now_iso()})

    usage = None
    if image:
        reply, error = run_vision(text, image)
    else:
        full_prompt = build_project_prompt(proj)
        reply, error, usage = run_model("chat", text, project_prompt=full_prompt)
    if error or not reply:
        return {"ok": False, "error": error or "No model answered"}

    messages.append({"role": "ella", "text": reply, "at": now_iso()})
    if len(messages) > 100:
        messages = messages[-100:]
    save_project_session(project_id, {"messages": messages})
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

    def _send(self, code, body, content_type="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _read_body(self, max_mb=20):
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        if length > max_mb * 1024 * 1024:
            self.rfile.read(length)
            return {"_error": f"Body too large ({length} bytes)"}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path in {"/", "/index.html"}:
            self._send(200, (WEB / "index.html").read_bytes(), "text/html; charset=utf-8")
            return
        if path == "/app.js":
            self._send(200, (WEB / "app.js").read_bytes(), "text/javascript; charset=utf-8")
            return
        if path == "/styles.css":
            self._send(200, (WEB / "styles.css").read_bytes(), "text/css; charset=utf-8")
            return
        if path == "/api/state":
            self._send(200, state())
            return
        if path == "/api/search":
            q = (parse_qs(parsed.query).get("q") or [""])[0]
            self._send(200, {"hits": search_notes(q)})
            return
        if path == "/api/graph":
            self._send(200, {"notes": graph()})
            return
        if path == "/api/note":
            q = (parse_qs(parsed.query).get("q") or [""])[0]
            self._send(200, find_note(q))
            return
        self._send(404, {"error": "not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/stt":
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length > 0 else b""
            kind = (self.headers.get("Content-Type") or "").lower()
            suffix = ".wav" if "wav" in kind else ".ogg" if "ogg" in kind else ".mp4" if "mp4" in kind else ".webm"
            self._send(200, transcribe(raw, suffix))
            return
        if path == "/api/tts":
            body = self._read_body()
            text = (body.get("text") or "").strip()
            result = synthesize(text)
            if not result.get("ok"):
                self._send(200, result)
            else:
                self._send(200, result["audio"], "audio/wav")
            return
        body = self._read_body()
        if path == "/api/profile":
            self._send(200, {"ok": True, "profile": save_profile(body)})
            return
        if path == "/api/checkin":
            self._send(200, run_locked(check_in))
            return
        if path == "/api/scout":
            self._send(200, run_locked(scout_now))
            return
        if path == "/api/adapt":
            self._send(200, run_locked(adapt))
            return
        if path == "/api/outbox":
            self._send(200, run_locked(retry_outbox))
            return
        if path == "/api/backup":
            self._send(200, {"ok": True, "name": make_backup()})
            return
        if path == "/api/restore":
            self._send(200, restore_backup(body.get("name") or ""))
            return
        if path == "/api/ask":
            self._send(200, run_locked(lambda: ask(body)))
            return
        if path == "/api/projects":
            action = body.get("action", "list")
            if action == "list":
                self._send(200, {"ok": True, "projects": load_projects()})
            elif action == "save":
                save_projects(body.get("projects") or [])
                self._send(200, {"ok": True})
            elif action == "add":
                projects = load_projects()
                proj = body.get("project", {})
                if not proj.get("id") or not proj.get("name"):
                    self._send(200, {"ok": False, "error": "id and name required"})
                else:
                    projects = [p for p in projects if p["id"] != proj["id"]]
                    projects.append(proj)
                    save_projects(projects)
                    self._send(200, {"ok": True, "projects": projects})
            elif action == "session":
                pid = body.get("project_id", "")
                session = load_project_session(pid)
                self._send(200, {"ok": True, "session": session})
            elif action == "update":
                pid = body.get("project_id", "")
                updates = body.get("updates", {})
                projects = load_projects()
                found = False
                for p in projects:
                    if p["id"] == pid:
                        for key in ("links", "actions", "prompt", "name", "color", "icon"):
                            if key in updates:
                                p[key] = updates[key]
                        found = True
                        break
                if found:
                    save_projects(projects)
                    self._send(200, {"ok": True, "projects": projects})
                else:
                    self._send(200, {"ok": False, "error": f"project {pid} not found"})
            elif action == "clear_session":
                pid = body.get("project_id", "")
                save_project_session(pid, {"messages": []})
                self._send(200, {"ok": True})
            else:
                self._send(200, {"ok": False, "error": "unknown action"})
            return
        if path == "/api/brain":
            self._send(200, {"ok": True, "brain": save_brain(body)})
            return
        if path == "/api/stop":
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
        self._send(404, {"error": "not found"})


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
