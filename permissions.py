"""Central permission engine for Ella.

Levels:
  L1 observe — read-only
  L2 prepare — draft or plan, no side effects
  L3 modify — change local state Ella already owns
  L4 external — send, post, spend, or reach outside

L4 always requires explicit user approval and never auto-executes.
Prompt text, another bot, or a bare True flag is not approval.
This module decides. It does not perform the action.
"""

from __future__ import annotations

import re

LEVEL_NAMES = {
    1: "observe",
    2: "prepare",
    3: "modify",
    4: "external",
}

# Labels for local state Ella already writes. Not a filesystem grant.
OWNED_TARGETS = frozenset({
    "profile",
    "memory",
    "facts",
    "activity",
    "brain",
    "sessions",
    "tasks",
    "outbox",
    "checkin",
    "usage",
    "quota",
    "free-models",
    "missed",
})

_ACTION_NAME = re.compile(r"^[a-z][a-z0-9._-]{0,63}$")
_DECLARED: dict[str, dict] = {}


def declare(name: str, level: int, summary: str) -> dict:
    """Register a future tool. Registration is not permission to run it."""
    if not isinstance(name, str) or not _ACTION_NAME.fullmatch(name):
        raise ValueError("Action name is invalid.")
    if isinstance(level, bool) or not isinstance(level, int) or level not in LEVEL_NAMES:
        raise ValueError("Permission level must be L1, L2, L3, or L4.")
    spec = {"name": name, "level": level, "summary": str(summary or "")[:240]}
    _DECLARED[name] = spec
    return dict(spec)


def level_catalog() -> dict:
    return {
        "levels": [
            {"level": 1, "name": "observe", "summary": "Read-only."},
            {"level": 2, "name": "prepare", "summary": "Draft or plan. No side effects."},
            {"level": 3, "name": "modify", "summary": "Change local state Ella already owns."},
            {
                "level": 4,
                "name": "external",
                "summary": "Send, post, spend, or reach outside. Explicit approval required. Never auto-executes.",
            },
        ],
        "declared": [dict(item) for item in _DECLARED.values()],
    }


def _approval_matches(approval, action: str) -> bool:
    """Explicit approval is a structured user decision for this exact action.

    A string, a bare boolean, or approval for a different action does not count.
    """
    if not isinstance(approval, dict):
        return False
    if approval.get("approved") is not True:
        return False
    if approval.get("by") != "user":
        return False
    if approval.get("action") != action:
        return False
    return True


def _base(action: str, level: int, target: str) -> dict:
    return {
        "action": action,
        "level": level,
        "level_name": LEVEL_NAMES.get(level, "invalid"),
        "actor": "ella",
        "target": target,
        "permitted": False,
        "may_observe": False,
        "may_prepare": False,
        "may_modify_local": False,
        "may_execute_external": False,
        "auto_execute": False,
        "requires_approval": level == 4,
        "approved": False,
        "side_effects": "none",
        "reason": "",
    }


def evaluate(action: str, level: int, target: str | None = None, approval=None) -> dict:
    """Decide whether a declared action may proceed. Does not execute it."""
    label = action if isinstance(action, str) else ""
    target_label = target if isinstance(target, str) else ""
    if not _ACTION_NAME.fullmatch(label):
        decision = _base(label[:64], 0, target_label[:64])
        decision["reason"] = "Action name is invalid."
        return decision
    if isinstance(level, bool) or not isinstance(level, int) or level not in LEVEL_NAMES:
        decision = _base(label, 0, target_label[:64])
        decision["reason"] = "Permission level must be L1, L2, L3, or L4."
        return decision

    decision = _base(label, level, target_label[:64])
    if level == 1:
        decision["permitted"] = True
        decision["may_observe"] = True
        decision["side_effects"] = "none"
        decision["reason"] = "Observe only. No side effects."
        return decision
    if level == 2:
        decision["permitted"] = True
        decision["may_observe"] = True
        decision["may_prepare"] = True
        decision["side_effects"] = "none"
        decision["reason"] = "Prepare only. Drafts stay local and nothing is changed or sent."
        return decision
    if level == 3:
        decision["side_effects"] = "local"
        if target_label not in OWNED_TARGETS:
            decision["reason"] = "Modify is limited to local state Ella already owns."
            return decision
        decision["permitted"] = True
        decision["may_observe"] = True
        decision["may_modify_local"] = True
        decision["reason"] = "Local state Ella owns may be changed. Nothing outside this PC is contacted."
        return decision

    approved = _approval_matches(approval, label)
    decision["side_effects"] = "external"
    decision["requires_approval"] = True
    decision["approved"] = approved
    decision["permitted"] = False
    decision["may_execute_external"] = False
    decision["auto_execute"] = False
    if approved:
        decision["reason"] = "Explicit approval was recorded. External actions are not auto-executed."
    else:
        decision["reason"] = "External actions need explicit user approval and are never auto-executed."
    return decision


def check_declared(name: str, target: str | None = None, approval=None) -> dict:
    """Evaluate an action that code has already declared."""
    spec = _DECLARED.get(name)
    if not spec:
        decision = _base(name if isinstance(name, str) else "", 0, target or "")
        decision["reason"] = "Action is not declared."
        return decision
    return evaluate(spec["name"], spec["level"], target=target, approval=approval)


declare("task.observe", 1, "Read a task request. No side effects.")
declare("task.prepare", 2, "Draft a local plan. No side effects.")
declare("task.persist", 3, "Write the task record Ella owns.")
declare("task.external", 4, "Placeholder for a future external action. Never auto-executed.")
