"""Durable local task plans.

A request becomes a list of steps. Each step is checked by the permission
engine. State is stored with locked_update so a restart can read it back.
L4 steps are recorded and left unfinished. This module does not call a
model or an external service.

Backup and restore include data/tasks.json under the existing
multi_file_transaction in server.py.
"""

from __future__ import annotations

import re
import secrets

from permissions import evaluate
from store import locked_update, now_iso, read_json

_EMPTY = {"version": 1, "tasks": []}
MAX_TASKS = 40
MAX_STEPS = 16
_ACTION = re.compile(r"^[a-z][a-z0-9._-]{0,63}$")
_TARGET = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
_TASK_ID = re.compile(r"^t_[0-9a-f]{16}$")
_STEP_ID = re.compile(r"^s[1-9][0-9]{0,2}$")

_tasks_path_override = None


class TaskRejected(ValueError):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.status = status


def set_tasks_path(path) -> None:
    """Test hook. None uses data/tasks.json."""
    global _tasks_path_override
    _tasks_path_override = path


def tasks_path():
    if _tasks_path_override is not None:
        return _tasks_path_override
    from store import DATA

    return DATA / "tasks.json"


def _clean_text(value, label: str, maximum: int) -> str:
    if not isinstance(value, str):
        raise TaskRejected(f"{label} must be a string.")
    stripped = value.strip()
    if not stripped or len(stripped) > maximum:
        raise TaskRejected(f"{label} is empty or too long.")
    if any(ord(char) < 32 and char not in "\t\n\r" for char in stripped):
        raise TaskRejected(f"{label} contains unsupported control characters.")
    return stripped


def _normalize(data) -> dict:
    raw = data.get("tasks") if isinstance(data, dict) else None
    tasks = []
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                tasks.append(item)
            if len(tasks) >= MAX_TASKS:
                break
    return {"version": 1, "tasks": tasks}


def _persist_gate() -> dict:
    gate = evaluate("task.persist", 3, target="tasks")
    if not gate["may_modify_local"] or gate["may_execute_external"] or gate["auto_execute"]:
        raise TaskRejected("Task record cannot be saved.")
    return gate


def _judge(step: dict, index: int) -> dict:
    title = step.get("title") if isinstance(step.get("title"), str) else "Step"
    action = step.get("action") if isinstance(step.get("action"), str) else ""
    target = step.get("target") if isinstance(step.get("target"), str) else ""
    level = step.get("level")
    step_id = step.get("id")
    if not isinstance(step_id, str) or not _STEP_ID.fullmatch(step_id):
        step_id = f"s{index + 1}"
    valid_level = isinstance(level, int) and not isinstance(level, bool) and level in (1, 2, 3, 4)
    valid_action = bool(_ACTION.fullmatch(action))
    if not valid_level or not valid_action:
        return {
            "id": step_id,
            "title": title[:200],
            "action": action[:64],
            "target": target[:64],
            "level": 0,
            "status": "blocked",
            "result": None,
            "reason": "Step is invalid.",
            "permission": {
                "action": action[:64],
                "level": 0,
                "permitted": False,
                "may_execute_external": False,
                "auto_execute": False,
                "requires_approval": False,
                "approved": False,
                "reason": "Step is invalid.",
            },
        }

    decision = evaluate(action, level, target=target or None)
    judged = {
        "id": step_id,
        "title": title[:200],
        "action": action,
        "target": target,
        "level": level,
        "status": "blocked",
        "result": None,
        "reason": decision["reason"],
        "permission": decision,
    }
    if decision["level"] != level or decision["may_execute_external"] or decision["auto_execute"]:
        judged["status"] = "blocked"
        judged["reason"] = "Permission decision does not allow this step to run."
        return judged
    if level == 4:
        judged["status"] = "awaiting_approval"
        judged["result"] = None
        judged["reason"] = decision["reason"]
        return judged
    if level == 1 and decision["may_observe"] and not decision["may_modify_local"]:
        judged["status"] = "done"
        judged["result"] = "Recorded. No side effects."
        return judged
    if level == 2 and decision["may_prepare"] and not decision["may_modify_local"]:
        judged["status"] = "done"
        judged["result"] = "Draft kept locally. No side effects."
        return judged
    if level == 3 and decision["may_modify_local"] and target == "tasks":
        judged["status"] = "done"
        judged["result"] = "Saved in the local task record."
        return judged
    if level == 3 and decision["may_modify_local"]:
        judged["status"] = "ready"
        judged["reason"] = "Permission allows this local change. It was not applied automatically."
        return judged
    judged["status"] = "blocked"
    return judged


def _mark_over_limit(step: dict) -> None:
    step["result"] = None
    if step.get("level") == 4:
        step["status"] = "awaiting_approval"
        step["reason"] = "L4 needs explicit user approval and is never auto-executed."
        step["permission"] = evaluate(step.get("action") or "task.external", 4, target=step.get("target") or None)
        return
    step["status"] = "blocked"
    step["reason"] = "Step limit exceeded. Not run."


def progress_of(task: dict) -> dict:
    steps = task.get("steps") or []
    unfinished = []
    done = 0
    for step in steps:
        # L4 is never finished by this engine, even if a file was edited to say so.
        if step.get("status") == "done" and step.get("level") != 4:
            done += 1
            continue
        unfinished.append({
            "id": step.get("id"),
            "title": step.get("title") or "",
            "level": step.get("level"),
            "status": "awaiting_approval" if step.get("level") == 4 else step.get("status"),
            "reason": step.get("reason") or "",
        })
    return {"done": done, "total": len(steps), "unfinished": unfinished}


def _refresh_status(task: dict) -> None:
    progress = progress_of(task)
    task["progress"] = progress
    total = progress["total"]
    task["status"] = "completed" if total and progress["done"] == total else "incomplete"


def _rejudge(task: dict) -> dict:
    steps_in = task.get("steps") if isinstance(task.get("steps"), list) else []
    judged = []
    for index, step in enumerate(steps_in[:32]):
        current = _judge(step if isinstance(step, dict) else {}, index)
        if index >= MAX_STEPS:
            _mark_over_limit(current)
        judged.append(current)
    gate = _persist_gate()
    request = task.get("request") if isinstance(task.get("request"), str) else ""
    record = {
        "id": task.get("id"),
        "request": request[:4000],
        "created_at": task.get("created_at") or now_iso(),
        "updated_at": task.get("updated_at") or now_iso(),
        "steps": judged,
        "persist_permission": {
            "action": gate["action"],
            "level": gate["level"],
            "may_modify_local": gate["may_modify_local"],
            "may_execute_external": gate["may_execute_external"],
            "auto_execute": gate["auto_execute"],
        },
    }
    _refresh_status(record)
    return record


def _public(task: dict) -> dict:
    return {
        "id": task.get("id"),
        "request": task.get("request") or "",
        "status": task.get("status"),
        "created_at": task.get("created_at"),
        "updated_at": task.get("updated_at"),
        "steps": task.get("steps") or [],
        "progress": task.get("progress") or progress_of(task),
        "persist_permission": task.get("persist_permission") or {},
    }


def _parse_steps(steps) -> list[dict]:
    if steps is None:
        steps = [
            {"title": "Read the request", "action": "task.observe", "level": 1},
            {"title": "Draft a local plan", "action": "task.prepare", "level": 2},
        ]
    if not isinstance(steps, list) or not steps or len(steps) > MAX_STEPS:
        raise TaskRejected("Steps must be a list of 1 to 16 steps.")
    cleaned = []
    for item in steps:
        if not isinstance(item, dict):
            raise TaskRejected("Step is invalid.")
        if set(item) - {"title", "action", "level", "target"}:
            raise TaskRejected("Step contains unsupported fields.")
        title = _clean_text(item.get("title"), "Step title", 200)
        action = item.get("action")
        if not isinstance(action, str) or not _ACTION.fullmatch(action):
            raise TaskRejected("Step action is invalid.")
        level = item.get("level")
        if isinstance(level, bool) or not isinstance(level, int) or level not in (1, 2, 3, 4):
            raise TaskRejected("Step level must be 1, 2, 3, or 4.")
        target = item.get("target", "")
        if target is None:
            target = ""
        if not isinstance(target, str) or (target and not _TARGET.fullmatch(target)):
            raise TaskRejected("Step target is invalid.")
        cleaned.append({"title": title, "action": action, "level": level, "target": target})
    return [_judge(step, index) for index, step in enumerate(cleaned)]


def submit_task(request: str, steps=None) -> dict:
    """Plan, permission-check, run only safe steps, and persist."""
    text = _clean_text(request, "Request", 4000)
    judged = _parse_steps(steps)
    gate = _persist_gate()
    stamp = now_iso()
    record = {
        "id": "t_" + secrets.token_hex(8),
        "request": text,
        "created_at": stamp,
        "updated_at": stamp,
        "steps": judged,
        "persist_permission": {
            "action": gate["action"],
            "level": gate["level"],
            "may_modify_local": gate["may_modify_local"],
            "may_execute_external": gate["may_execute_external"],
            "auto_execute": gate["auto_execute"],
        },
    }
    _refresh_status(record)

    def transform(current):
        data = _normalize(current)
        data["tasks"].insert(0, record)
        data["tasks"] = data["tasks"][:MAX_TASKS]
        return data

    locked_update(tasks_path(), _EMPTY, transform)
    return _public(record)


def resume_task(task_id: str) -> dict:
    """Reload a task after a restart and re-apply the permission rules."""
    if not isinstance(task_id, str) or not _TASK_ID.fullmatch(task_id):
        raise TaskRejected("Task id is invalid.")
    path = tasks_path()
    if not path.exists():
        raise TaskRejected("Unknown task.", status=404)
    found: dict = {}

    def transform(current):
        data = _normalize(current)
        tasks = []
        for task in data["tasks"]:
            if task.get("id") == task_id:
                updated = _rejudge(task)
                updated["updated_at"] = now_iso()
                _refresh_status(updated)
                tasks.append(updated)
                found["task"] = _public(updated)
            else:
                tasks.append(task)
        data["tasks"] = tasks
        return data

    locked_update(path, _EMPTY, transform)
    if "task" not in found:
        raise TaskRejected("Unknown task.", status=404)
    return found["task"]


def task_report() -> dict:
    """Read-only progress report. L4 steps are shown unfinished."""
    try:
        data = _normalize(read_json(tasks_path(), _EMPTY))
        views = [_public(_rejudge(task)) for task in data["tasks"]]
    except TaskRejected:
        return {"version": 1, "count": 0, "incomplete": 0, "tasks": [], "error": "Task record could not be read."}
    except Exception:
        return {"version": 1, "count": 0, "incomplete": 0, "tasks": [], "error": "Task record could not be read."}
    incomplete = sum(1 for item in views if item.get("status") != "completed")
    return {"version": 1, "count": len(views), "incomplete": incomplete, "tasks": views}


def task_summary() -> dict:
    report = task_report()
    unfinished = []
    for task in report.get("tasks") or []:
        for item in (task.get("progress") or {}).get("unfinished") or []:
            unfinished.append({
                "task_id": task.get("id"),
                "id": item.get("id"),
                "title": item.get("title"),
                "level": item.get("level"),
                "status": item.get("status"),
                "reason": item.get("reason"),
            })
            if len(unfinished) >= 20:
                break
        if len(unfinished) >= 20:
            break
    summary = {
        "count": report.get("count") or 0,
        "incomplete": report.get("incomplete") or 0,
        "unfinished": unfinished,
    }
    if report.get("error"):
        summary["error"] = report["error"]
    return summary
