"""Local-first context gate.

Decides which context may stay on this PC and which may be offered to a
cloud provider. The only cloud switch is the existing brain mode: "local"
or "cloud". Missing or unknown modes stay local.

This module does not call a provider and does not add vendors. Callers must
pass category labels, never prompt text, secrets, or message bodies.
"""

from __future__ import annotations

LOCAL_PROVIDER = "ollama"
# Existing router.complete cloud adapters. Do not extend this tuple here.
CLOUD_PROVIDERS = ("openrouter", "groq")
KNOWN_PROVIDERS = frozenset({LOCAL_PROVIDER, *CLOUD_PROVIDERS})

LOCAL_ONLY_KINDS = frozenset({
    "secret",
    "secrets",
    "env",
    "credential",
    "credentials",
    "api_key",
    "token",
    "password",
    "server_lock",
})


def bundles_for_kind(kind: str) -> list[dict]:
    """Category labels only. These strings are not user content."""
    if kind == "routine":
        return [
            {"kind": "profile", "label": "profile"},
            {"kind": "memory", "label": "facts"},
            {"kind": "vault", "label": "vault index"},
            {"kind": "prompt", "label": "routine prompt"},
        ]
    if kind == "vision":
        return [{"kind": "vision", "label": "image"}]
    return [
        {"kind": "chat", "label": "chat"},
        {"kind": "history", "label": "recent turns"},
    ]


def _labels(items: list[dict]) -> list[str]:
    labels = []
    for item in items:
        label = item.get("label") or item.get("kind") or "context"
        if isinstance(label, str) and label:
            labels.append(label[:80])
    return labels


def route_for(mode, bundles=None, destination=None, kind: str = "chat") -> dict:
    """Return a routing decision. Does not send the context anywhere."""
    clean = [item for item in (bundles or []) if isinstance(item, dict)]
    selected = "cloud" if mode == "cloud" else "local"
    unknown_destination = destination not in (None, "local", "cloud")
    requested = "local" if unknown_destination else (destination or selected)
    local_only = [item for item in clean if str(item.get("kind") or "") in LOCAL_ONLY_KINDS]

    blocked = False
    if unknown_destination:
        blocked = True
        reason = "Unknown destination. Context stays on this PC."
    elif requested == "cloud" and selected != "cloud":
        blocked = True
        reason = "Cloud send blocked. Local mode is on."
    elif requested == "cloud" and local_only:
        blocked = True
        reason = "Secrets and credentials never leave this PC."
    elif requested == "cloud":
        reason = "Cloud mode is on. Existing providers only. This check does not send anything."
    else:
        reason = "Local-first. Context stays on this PC."

    provider_mode = "local"
    allow_cloud = False
    permitted: list[str] = []
    if not blocked and requested == "cloud" and selected == "cloud":
        provider_mode = "cloud"
        allow_cloud = True
        if kind == "routine":
            permitted = ["groq", "ollama"]
        else:
            permitted = ["openrouter", "groq", "ollama"]
    elif not blocked:
        permitted = ["ollama"]

    if blocked and requested == "cloud":
        withheld = _labels(clean) or ["context"]
        may_leave: list[str] = []
        stays = _labels(clean)
    elif provider_mode == "cloud":
        withheld = _labels(local_only)
        may_leave = _labels([item for item in clean if item not in local_only])
        stays = _labels(local_only)
    else:
        withheld = _labels(local_only)
        may_leave = []
        stays = _labels(clean)

    return {
        "mode": selected,
        "local_first": True,
        "cloud_switch": selected == "cloud",
        "destination_requested": "rejected" if unknown_destination else requested,
        "provider_mode": provider_mode,
        "allow_cloud": allow_cloud,
        "blocked": blocked,
        "allow_route": not blocked,
        "permitted_providers": permitted,
        "may_leave": may_leave,
        "stays_local": stays,
        "withheld": withheld,
        "reason": reason,
        "vendors_added": [],
    }


def context_status(mode) -> dict:
    """Small status for /api/state. No prompt text."""
    decision = route_for(mode, bundles_for_kind("chat"), kind="chat")
    return {
        "mode": decision["mode"],
        "local_first": True,
        "cloud_switch": decision["cloud_switch"],
        "allow_cloud": decision["allow_cloud"],
        "blocked": decision["blocked"],
        "permitted_providers": list(decision["permitted_providers"]),
        "vision": "local",
        "reason": decision["reason"],
    }
