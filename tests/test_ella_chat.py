"""Ella regression tests. Run against live server on 127.0.0.1:8765."""

import json
import re
import time
import urllib.request

BASE = "http://127.0.0.1:8765"
PASS = 0
FAIL = 0
LOG = []
_TOKEN = None


def request_token():
    global _TOKEN
    if _TOKEN is None:
        with urllib.request.urlopen(BASE, timeout=10) as response:
            page = response.read().decode("utf-8")
        match = re.search(r'<meta name="ella-request-token" content="([A-Za-z0-9_-]+)">', page)
        if not match:
            raise RuntimeError("Ella request token was not found in the local panel page")
        _TOKEN = match.group(1)
    return _TOKEN


def api_headers(content_type):
    return {
        "Content-Type": content_type,
        "X-Ella-Request-Token": request_token(),
    }


def ask(text):
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(
        f"{BASE}/api/ask", data=data,
        headers=api_headers("application/json"),
    )
    t0 = time.monotonic()
    with urllib.request.urlopen(req, timeout=60) as r:
        resp = json.loads(r.read())
    elapsed = time.monotonic() - t0
    return resp, elapsed


def tts(text):
    data = json.dumps({"text": text}).encode()
    req = urllib.request.Request(
        f"{BASE}/api/tts", data=data,
        headers=api_headers("application/json"),
    )
    t0 = time.monotonic()
    with urllib.request.urlopen(req, timeout=30) as r:
        ct = r.headers.get("Content-Type", "")
        body = r.read()
    elapsed = time.monotonic() - t0
    return ct, len(body), elapsed


def stt(wav_bytes):
    req = urllib.request.Request(
        f"{BASE}/api/stt", data=wav_bytes,
        headers=api_headers("audio/wav"),
    )
    t0 = time.monotonic()
    with urllib.request.urlopen(req, timeout=60) as r:
        resp = json.loads(r.read())
    elapsed = time.monotonic() - t0
    return resp, elapsed


def check(name, condition, detail=""):
    global PASS, FAIL
    status = "PASS" if condition else "FAIL"
    if condition:
        PASS += 1
    else:
        FAIL += 1
    line = f"  [{status}] {name}"
    if detail:
        line += f" — {detail}"
    print(line)
    LOG.append({"test": name, "status": status, "detail": detail})


def leaked(text):
    markers = ["setup_done", "timezone", "Vault index", "Profile:", "Facts:"]
    return any(m in text for m in markers)


print("=" * 60)
print("Ella Chat Regression Tests")
print("=" * 60)

# --- Bug 1: Identity ---
print("\n1. Identity")
r, t = ask("hey Ella, who are you?")
reply = r.get("text", "")
check("identity: says Ella", "ella" in reply.lower(), reply[:120])
check("identity: not Cyrus", "i'm cyrus" not in reply.lower(), reply[:120])
check("identity: no leak", not leaked(reply), reply[:80])

# --- Bug 2: Time ---
print("\n2. Time accuracy")
r, t = ask("what time is it right now?")
reply = r.get("text", "")
now_hour = time.strftime("%I").lstrip("0")
check("time: mentions hour", now_hour in reply or time.strftime("%H") in reply, reply[:120])
check("time: no leak", not leaked(reply), reply[:80])

# --- Bug 3: Check-in spam ---
print("\n3. Check-in spam guard")
r1, _ = ask("good morning")
r2, _ = ask("good morning")
t1 = r1.get("text", "")
t2 = r2.get("text", "")
check("checkin: second call reuses first", t1 == t2, f"len1={len(t1)} len2={len(t2)}")

# --- Conversation memory ---
print("\n4. Conversation memory")
ask("my favorite color is blue")
r, _ = ask("what is my favorite color?")
reply = r.get("text", "")
check("memory: remembers blue", "blue" in reply.lower(), reply[:120])

# --- Greeting ---
print("\n5. Greeting")
r, t = ask("hey Ella can you hear me")
reply = r.get("text", "")
check("greeting: short reply", len(reply) < 300, f"len={len(reply)}")
check("greeting: no leak", not leaked(reply), reply[:80])

# --- Voice round trip ---
print("\n6. Voice round trip")
ct, size, t_tts = tts("Hello Cyrus, I am Ella.")
check("tts: returns wav", "audio" in ct, f"ct={ct} size={size}")
check("tts: under 3s", t_tts < 3.0, f"{t_tts:.2f}s")

# Feed TTS output back to STT
tts_data = json.dumps({"text": "Testing one two three"}).encode()
tts_req = urllib.request.Request(f"{BASE}/api/tts", data=tts_data, headers=api_headers("application/json"))
with urllib.request.urlopen(tts_req, timeout=30) as resp:
    wav = resp.read()
stt_r, t_stt = stt(wav)
check("stt: transcribes", stt_r.get("ok", False), stt_r.get("text", ""))

# --- Summary ---
print("\n" + "=" * 60)
print(f"Results: {PASS} passed, {FAIL} failed out of {PASS + FAIL}")
print("=" * 60)

if FAIL:
    exit(1)
