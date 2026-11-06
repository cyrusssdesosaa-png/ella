"""Model calls. Local mode uses Ollama only. Cloud mode uses the free APIs.

Anything other than an explicit cloud mode stays on Ollama. No new vendors.
"""

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

import cancel
from model_registry import DEFAULT_LOCAL_CHAT, GROQ_CHAT, OPENROUTER_CHAT

ROOT = Path(__file__).resolve().parent
TIMEOUT = 30


def provider_order(mode, kind):
    """Local-first provider order.

    Only an explicit cloud mode may name the existing cloud adapters.
    Any other mode, including a missing or unknown one, stays on Ollama.
    """
    if mode != "cloud":
        return ("ollama",)
    if kind == "routine":
        return ("groq", "ollama")
    return ("openrouter", "groq", "ollama")


def load_env():
    env = {}
    path = ROOT / ".env"
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def _post(url, payload, headers):
    data = json.dumps(payload).encode("utf-8")
    headers = {"User-Agent": "Ella/1.0", **headers}
    try:
        status, res_headers, raw = cancel.post_json(url, data, headers, TIMEOUT)
        if status >= 400:
            detail = raw.decode("utf-8", errors="replace")[:300]
            return None, None, f"HTTP {status}: {detail}"
        body = json.loads(raw.decode("utf-8"))
        remaining = res_headers.get("x-ratelimit-remaining") or res_headers.get(
            "X-RateLimit-Remaining"
        )
        return body, remaining, None
    except cancel.Cancelled:
        raise
    except Exception as exc:
        return None, None, str(exc)


def _text_from(body):
    if not body:
        return ""
    choices = body.get("choices") or []
    if not choices:
        message = body.get("message") or {}
        return (message.get("content") or "").strip()
    message = choices[0].get("message") or {}
    return (message.get("content") or "").strip()


def _usage_from(body, provider, model=""):
    usage = {"prompt": 0, "completion": 0, "total": 0, "provider": provider, "model": model or "", "tps": 0}
    if not isinstance(body, dict):
        return usage
    if provider == "ollama":
        prompt = int(body.get("prompt_eval_count") or 0)
        completion = int(body.get("eval_count") or 0)
        dur = body.get("eval_duration") or 0
        if dur and completion:
            usage["tps"] = round(completion / (dur / 1e9), 1)
        # Ollama echoes the model that served the request.
        usage["model"] = (body.get("model") or model or "").strip() or (model or "")
    else:
        raw = body.get("usage") or {}
        prompt = int(raw.get("prompt_tokens") or 0)
        completion = int(raw.get("completion_tokens") or 0)
        usage["model"] = (body.get("model") or model or "").strip() or (model or "")
    usage["prompt"] = max(0, prompt)
    usage["completion"] = max(0, completion)
    usage["total"] = usage["prompt"] + usage["completion"]
    return usage


def ollama_base(env):
    return (env.get("OLLAMA_URL") or "http://127.0.0.1:11434").rstrip("/")


def ollama_models(env):
    req = urllib.request.Request(ollama_base(env) + "/api/tags", headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=3) as res:
        payload = json.loads(res.read().decode("utf-8"))
    names = []
    for item in payload.get("models") or []:
        name = item.get("name") or ""
        if name:
            names.append(name)
    return names


def ollama_chat(env, messages, model=None):
    url = ollama_base(env) + "/api/chat"
    used = model or DEFAULT_LOCAL_CHAT
    payload = {
        "model": used,
        "messages": messages,
        "stream": False,
        "keep_alive": "10m",
        "options": {
            "temperature": 0.6,
            "top_p": 0.9,
            "num_ctx": 4096,
            "stop": ["User:", "Human:", "### User", "<|user|>"],
        },
    }
    body, remaining, err = _post(url, payload, {"Content-Type": "application/json"})
    if err:
        return "", None, err, _usage_from(None, "ollama", used)
    return _text_from(body), remaining, None, _usage_from(body, "ollama", used)


def groq_chat(env, messages):
    key = env.get("GROQ_API_KEY") or ""
    used = GROQ_CHAT
    if not key:
        return "", None, "No Groq key", _usage_from(None, "groq", used)
    body, remaining, err = _post(
        "https://api.groq.com/openai/v1/chat/completions",
        {"model": used, "messages": messages},
        {"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
    )
    if err:
        return "", remaining, err, _usage_from(None, "groq", used)
    return _text_from(body), remaining, None, _usage_from(body, "groq", used)


def openrouter_chat(env, messages, model):
    key = env.get("OPENROUTER_API_KEY") or ""
    used = model or OPENROUTER_CHAT
    if not key:
        return "", None, "No OpenRouter key", _usage_from(None, "openrouter", used)
    body, remaining, err = _post(
        "https://openrouter.ai/api/v1/chat/completions",
        {"model": used, "messages": messages},
        {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
            "HTTP-Referer": "http://127.0.0.1:8765",
            "X-Title": "Ella",
        },
    )
    if err:
        return "", remaining, err, _usage_from(None, "openrouter", used)
    return _text_from(body), remaining, None, _usage_from(body, "openrouter", used)


def complete(env, messages, kind, model=None, mode="local", local_model=None):
    """Local mode stays on Ollama. Explicit cloud mode uses the free APIs, then Ollama.

    Unknown modes stay on Ollama so a bad brain value cannot silently go to cloud.
    """
    order = provider_order(mode, kind)
    errors = []
    remaining = None
    last_usage = _usage_from(None, "")
    for name in order:
        for _attempt in (1, 2):
            cancel.check()
            if name == "groq":
                text, remaining, err, usage = groq_chat(env, messages)
            elif name == "ollama":
                text, remaining, err, usage = ollama_chat(env, messages, local_model)
            else:
                text, remaining, err, usage = openrouter_chat(env, messages, model)
            last_usage = usage
            if text:
                usage["provider"] = name
                if not usage.get("model"):
                    if name == "ollama":
                        usage["model"] = local_model or DEFAULT_LOCAL_CHAT
                    elif name == "groq":
                        usage["model"] = GROQ_CHAT
                    else:
                        usage["model"] = model or OPENROUTER_CHAT
                return text, name, remaining, None, usage
            errors.append(f"{name}: {err or 'empty reply'}")
    return "", "", remaining, "; ".join(errors), last_usage
