"""Model calls. Local mode uses Ollama only. Cloud mode uses the free APIs."""

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TIMEOUT = 30


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
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
            body = json.loads(res.read().decode("utf-8"))
            remaining = res.headers.get("x-ratelimit-remaining") or res.headers.get(
                "X-RateLimit-Remaining"
            )
            return body, remaining, None
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        return None, None, f"HTTP {exc.code}: {detail}"
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


def _usage_from(body, provider):
    usage = {"prompt": 0, "completion": 0, "total": 0, "provider": provider, "tps": 0}
    if not isinstance(body, dict):
        return usage
    if provider == "ollama":
        prompt = int(body.get("prompt_eval_count") or 0)
        completion = int(body.get("eval_count") or 0)
        dur = body.get("eval_duration") or 0
        if dur and completion:
            usage["tps"] = round(completion / (dur / 1e9), 1)
    else:
        raw = body.get("usage") or {}
        prompt = int(raw.get("prompt_tokens") or 0)
        completion = int(raw.get("completion_tokens") or 0)
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
    payload = {
        "model": model or "llama3.2:3b",
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
        return "", None, err, _usage_from(None, "ollama")
    return _text_from(body), remaining, None, _usage_from(body, "ollama")


def groq_chat(env, messages):
    key = env.get("GROQ_API_KEY") or ""
    if not key:
        return "", None, "No Groq key", _usage_from(None, "groq")
    body, remaining, err = _post(
        "https://api.groq.com/openai/v1/chat/completions",
        {"model": "llama-3.1-8b-instant", "messages": messages},
        {"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
    )
    if err:
        return "", remaining, err, _usage_from(None, "groq")
    return _text_from(body), remaining, None, _usage_from(body, "groq")


def openrouter_chat(env, messages, model):
    key = env.get("OPENROUTER_API_KEY") or ""
    if not key:
        return "", None, "No OpenRouter key", _usage_from(None, "openrouter")
    body, remaining, err = _post(
        "https://openrouter.ai/api/v1/chat/completions",
        {"model": model or "openrouter/free", "messages": messages},
        {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
            "HTTP-Referer": "http://127.0.0.1:8765",
            "X-Title": "Ella",
        },
    )
    if err:
        return "", remaining, err, _usage_from(None, "openrouter")
    return _text_from(body), remaining, None, _usage_from(body, "openrouter")


def complete(env, messages, kind, model=None, mode="local", local_model=None):
    """Local mode stays on Ollama. Cloud mode uses the free APIs, then Ollama."""
    if mode == "local":
        order = ("ollama",)
    elif kind == "routine":
        order = ("groq", "ollama")
    else:
        order = ("openrouter", "groq", "ollama")
    errors = []
    remaining = None
    last_usage = _usage_from(None, "")
    for name in order:
        for _attempt in (1, 2):
            if name == "groq":
                text, remaining, err, usage = groq_chat(env, messages)
            elif name == "ollama":
                text, remaining, err, usage = ollama_chat(env, messages, local_model)
            else:
                text, remaining, err, usage = openrouter_chat(env, messages, model)
            last_usage = usage
            if text:
                usage["provider"] = name
                return text, name, remaining, None, usage
            errors.append(f"{name}: {err or 'empty reply'}")
    return "", "", remaining, "; ".join(errors), last_usage
