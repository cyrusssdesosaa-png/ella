"""Daily notes for the memory vault. Manila dates. One note per day."""

from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VAULT = ROOT / "vault"
DAILY = VAULT / "01 - Daily Notes"
INDEX = VAULT / "VAULT-INDEX.md"


def manila_now():
    try:
        from zoneinfo import ZoneInfo

        return datetime.now(ZoneInfo("Asia/Manila"))
    except Exception:
        return datetime.now()


def today_path(now=None):
    now = now or manila_now()
    folder = DAILY / f"{now.month:02d} - {now.strftime('%B %Y')}"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / f"{now.strftime('%Y-%m-%d')}.md"


def _fresh_note(now):
    heading = now.strftime("%A, %B ") + str(now.day) + now.strftime(", %Y")
    stamp = now.strftime("%Y-%m-%d")
    return (
        "---\n"
        "status: active\n"
        "project: personal\n"
        "type: log\n"
        f"created: {stamp}\n"
        "---\n\n"
        f"# {heading}\n\n"
        "## Index\n\n"
    )


def append_session(topic, done, progress, decisions, notes, profile_updates="-"):
    now = manila_now()
    path = today_path(now)
    if path.exists():
        text = path.read_text(encoding="utf-8")
    else:
        text = _fresh_note(now)
    count = text.count("\n## Session ")
    number = count + 1
    clock = now.strftime("%H:%M")
    line = f"- **{topic}.** {done}\n"
    if "## Index\n" in text and line not in text:
        text = text.replace("## Index\n", "## Index\n\n" + line, 1)
    block = (
        f"\n## Session {number}. {clock}: {topic}\n\n"
        "### What Got Done\n"
        f"- {done}\n\n"
        "### What's Still In Progress\n"
        f"- {progress}\n\n"
        "### Decisions Made\n"
        f"- {decisions}\n\n"
        "### Notes Touched\n"
        f"- {notes}\n\n"
        "### Profile Updates\n"
        f"- {profile_updates}\n"
    )
    path.write_text(text.rstrip() + "\n" + block, encoding="utf-8")
    return str(path)


def today_text():
    path = today_path()
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


CATEGORIES = {
    "00 - Inbox": "Files",
    "01 - Daily Notes": "Notes",
    "02 - Jarvis": "Skills",
    "03 - Aura": "Worlds",
    "04 - GOD": "Tools",
    "05 - Wally": "Concepts",
    "06 - Desk": "Wiki",
    "07 - Night Shift": "Router",
    "08 - Personal": "Notes",
    "09 - Archive": "Files",
    "10 - Resources": "Suites",
}


def graph():
    notes = []
    for path in sorted(VAULT.rglob("*.md")):
        if path.name == "NOTICE.md":
            continue
        rel = path.relative_to(VAULT)
        folder = rel.parts[0] if len(rel.parts) > 1 else "Vault"
        notes.append(
            {
                "name": path.stem,
                "folder": folder,
                "category": CATEGORIES.get(folder, "Concepts"),
            }
        )
    return notes


def find_note(query):
    query = query.strip().lower()
    if not query:
        return {"matches": []}
    named = []
    loose = []
    for path in VAULT.rglob("*.md"):
        stem = path.stem.lower()
        if query in stem:
            named.append(path)
        elif query in path.name.lower():
            loose.append(path)
    picks = named or loose
    if len(picks) == 1:
        text = picks[0].read_text(encoding="utf-8")
        return {"path": str(picks[0]), "text": text[:8000]}
    return {"matches": [path.stem for path in picks[:8]]}


def index_text():
    if not INDEX.exists():
        return ""
    return INDEX.read_text(encoding="utf-8")
