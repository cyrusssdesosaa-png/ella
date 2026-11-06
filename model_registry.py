"""Truthful capability lookup for models Ella is configured to call.

Vision is moondream:latest through the local Ollama generate path. This
module does not load a model, contact Ollama, or invent token prices.
Hardware target is one RTX 3050 8GB and 16GB RAM, so nothing here is
kept resident.
"""

from __future__ import annotations

VISION_MODEL = "moondream:latest"
DEFAULT_LOCAL_CHAT = "llama3.2:3b"
GROQ_CHAT = "llama-3.1-8b-instant"
OPENROUTER_CHAT = "openrouter/free"

_NO_PRICE = "Token price is not registered."

_MODELS = {
    DEFAULT_LOCAL_CHAT: {
        "id": DEFAULT_LOCAL_CHAT,
        "provider": "ollama",
        "local": True,
        "chat": True,
        "vision": False,
        "role": "chat",
        "configured": True,
        "notes": "Default local chat model when brain.json has no model. Not used for images. " + _NO_PRICE,
    },
    VISION_MODEL: {
        "id": VISION_MODEL,
        "provider": "ollama",
        "local": True,
        "chat": False,
        "vision": True,
        "role": "vision",
        "configured": True,
        "notes": (
            "Only model Ella calls for images, via Ollama /api/generate. "
            "Not the chat model and not kept loaded. " + _NO_PRICE
        ),
    },
    GROQ_CHAT: {
        "id": GROQ_CHAT,
        "provider": "groq",
        "local": False,
        "chat": True,
        "vision": False,
        "role": "cloud-chat",
        "configured": True,
        "notes": "Existing Groq chat model. Used only after Cloud mode is on. No vision path. " + _NO_PRICE,
    },
    OPENROUTER_CHAT: {
        "id": OPENROUTER_CHAT,
        "provider": "openrouter",
        "local": False,
        "chat": True,
        "vision": False,
        "role": "cloud-chat",
        "configured": True,
        "notes": (
            "Existing OpenRouter fallback id used for chat completions after Cloud mode is on. "
            "Not a claim about one catalog model's vision ability. " + _NO_PRICE
        ),
    },
}

CONFIGURED_IDS = (DEFAULT_LOCAL_CHAT, VISION_MODEL, GROQ_CHAT, OPENROUTER_CHAT)


def vision_model_id() -> str:
    """Model id the vision path calls. Kept as moondream:latest."""
    return VISION_MODEL


def lookup(model_id: str) -> dict:
    """Return what Ella knows. Unknown models stay unknown. Vision stays off them."""
    if not isinstance(model_id, str):
        model_id = ""
    model_id = model_id.strip()
    known = _MODELS.get(model_id)
    if known:
        item = dict(known)
    else:
        item = {
            "id": model_id,
            "provider": "unknown",
            "local": None,
            "chat": None,
            "vision": False,
            "role": "unregistered",
            "configured": False,
            "notes": (
                "Not a configured Ella model. Ella does not send images to it. "
                + _NO_PRICE
            ),
        }
    item["cost_known"] = False
    return item


def capability_snapshot(brain=None, local_names=None) -> dict:
    """Status snapshot. local_names must already have been collected by the caller."""
    mode = "local"
    active_id = DEFAULT_LOCAL_CHAT
    if isinstance(brain, dict):
        if brain.get("mode") in {"local", "cloud"}:
            mode = brain["mode"]
        model = brain.get("model")
        if isinstance(model, str) and model.strip():
            active_id = model.strip()
    installed = []
    for name in list(local_names or [])[:32]:
        if not isinstance(name, str) or not name.strip():
            continue
        item = lookup(name.strip())
        item["installed_reported"] = True
        installed.append(item)
    return {
        "vision_model": vision_model_id(),
        "default_local_chat": DEFAULT_LOCAL_CHAT,
        "mode": mode,
        "active_model": lookup(active_id),
        "configured": [lookup(model_id) for model_id in CONFIGURED_IDS],
        "installed_local": installed,
        "cost_known": False,
    }
