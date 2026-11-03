# Ella P0 — Build Result

**Date:** Tuesday, November 3, 2026  
**Builder:** Cursor Agent (Claude Opus 4.6)  
**Status:** All P0 items tested and working. All 3 critical bugs fixed.

---

## What Ella Is

A fully local AI assistant for Cyrus's PC. Runs on `127.0.0.1:8765` with a
futuristic ring UI, a brain graph built from vault notes, and a local voice
loop. Both LOCAL (Ollama) and CLOUD (OpenRouter / Groq) modes work, with a
one-click switch.

---

## P0 Deliverables — All Done

### 1. Local Voice Loop ✅

| Component       | Library            | Model / Voice              | Device   |
|-----------------|--------------------|----------------------------|----------|
| STT (listen)    | faster-whisper 1.2 | `base.en`                  | CPU int8 (CUDA fallback) |
| LLM (think)     | Ollama             | `qwen2.5:7b`               | GPU      |
| TTS (speak)     | piper-tts 1.8      | `en_GB-jenny_dioco-medium` | CPU      |

**Flow:** browser mic → MediaRecorder (WebM/Opus) → `POST /api/stt` →
faster-whisper transcript → `POST /api/ask` → Ollama reply → `POST /api/tts`
→ Piper WAV → `<audio>` playback in browser.

**Silence / VAD:** the JS mic listener auto-stops after 1.4 s of quiet or
15 s max. `vad_filter=True` on Whisper. Piper text capped at 2000 chars.

**Voices downloaded** to `D:\ella-voices`:
- `jenny_dioco-medium` (63 MB, active)
- `cori-high` (114 MB, backup British female)
- `alba-medium` (63 MB, backup British female)

Switch voice: set `ELLA_VOICE=cori-high` in `.env` or env var.

### 2. Ring UI with States ✅

| State         | Status pill  | Ring color | Trigger              |
|---------------|-------------|------------|----------------------|
| Online        | ● ONLINE    | Cyan idle  | Default / after done |
| Listening     | ● LISTENING | Cyan pulse | Mic button pressed   |
| Transcribing  | ● TRANSCRIBING | Orange | Audio sent to STT  |
| Thinking      | ● THINKING  | Orange spin| Ask sent to Ollama   |
| Speaking      | ● SPEAKING  | Green glow | TTS audio playing    |

The arc-reactor ring label reads **E.L.L.A.** in the center. Six cyan arcs
spin, an orange accent arc moves with speaking state, and the inner core
pulses with amplitude.

### 3. Cloud / Local Switch ✅

- **LOCAL mode (default):** Ollama only. No internet needed. Switch model
  from the pill or `data/brain.json`.
- **CLOUD mode:** OpenRouter free tier → Groq → Ollama fallback. All 36 API
  keys stay in `.env`. Nothing removed.
- **Switch:** click the teal pill in the ring column. Persists in
  `data/brain.json`.

### 4. PC App Packaging (pywebview) ✅

```
python ella.py          # launch desktop window
python ella.py --debug  # launch with DevTools
```

- `ella.py` spawns `server.py` in a child process, waits for it to respond,
  then opens a pywebview window titled "E.L.L.A." at 1280 × 800.
- Closing the window kills the server.
- Background color `#05070a` matches the ring UI.
- pywebview 6.2.1 already installed; uses Edge WebView2 on Windows.

---

## Bug Fixes — All 3 Critical Bugs Fixed

### Bug 1: Identity — "I'm Cyrus" → FIXED ✅

**Problem:** The 3b model consistently identified itself as Cyrus despite
explicit system prompt instructions.

**Root cause:** llama3.2:3b too small to follow identity instructions reliably.
Also, profile notes (name: Cyrus) were leaking into the system prompt.

**Fix:**
1. Switched default model to `qwen2.5:7b` (4.7 GB, fits in 8 GB VRAM)
2. Split `_messages()` into chat mode (short ~300-char identity prompt) and
   routine mode (full context)
3. Added `_identity_check()` regex guard that replaces "I'm Cyrus" → "I'm Ella"
4. Added `_strip_leaked_context()` safety net

**Result:** "I'm Ella, your local AI assistant. How can I help you today?"

### Bug 2: Wrong Time — FIXED ✅

**Problem:** Model said "09:00" when it was 11:15 AM. Real time was never
passed to the model.

**Fix:** Added `_now_str()` that injects `datetime.now().strftime("%A %B %d, %Y %I:%M %p")` into the system prompt. The qwen2.5:7b model reads and uses it correctly.

**Result:** "It's 11:53 AM on a Tuesday, November 03, 2026."

### Bug 3: Check-in Spam — FIXED ✅

**Problem:** Four check-ins ran in two minutes, duplicating daily notes. The
`maybe_missed_checkin()` startup thread kept calling the model.

**Fix:** Added today-guard in `check_in()`: reads `checkin.json`, if
`stamp.startswith(today)` returns cached text immediately. Guard was not
executing earlier because a zombie server process (PID from pywebview test)
was holding port 8765 with old code.

**Result:** Second "good morning" returns identical cached text instantly.

### Bonus: TTS Cold Start — FIXED

**Problem:** First TTS call took 6.6s to load Piper voice model.

**Fix:** Added `warmup()` function called in a background thread at server start.
First user TTS call now takes 0.15s.

---

## Regression Test Results — 12/12 PASS ✅

```
============================================================
Ella Chat Regression Tests
============================================================

1. Identity
  [PASS] identity: says Ella — I'm Ella, your local AI assistant.
  [PASS] identity: not Cyrus
  [PASS] identity: no leak

2. Time accuracy
  [PASS] time: mentions hour — It's 11:53 AM on a Tuesday, November 03, 2026.
  [PASS] time: no leak

3. Check-in spam guard
  [PASS] checkin: second call reuses first — len1=248 len2=248

4. Conversation memory
  [PASS] memory: remembers blue — You said your favorite color is blue!

5. Greeting
  [PASS] greeting: short reply — len=49
  [PASS] greeting: no leak

6. Voice round trip
  [PASS] tts: returns wav — ct=audio/wav size=68652
  [PASS] tts: under 3s — 0.15s
  [PASS] stt: transcribes — Testing 123

Results: 12 passed, 0 failed out of 12
============================================================
```

---

## 6-Message Test Conversation

Tested live against qwen2.5:7b on the running server:

| # | User | Ella | Notes |
|---|------|------|-------|
| 1 | "hey Ella, who are you?" | "I'm Ella, your local AI assistant. How can I help you today?" | Identity correct ✅ |
| 2 | "what time is it right now?" | "It's 11:52 AM on Tuesday, November 03, 2026." | Real Manila time ✅ |
| 3 | "good morning" | Check-in: priorities, tasks, what's waiting | Check-in fires once ✅ |
| 4 | "good morning" (repeat) | Same cached check-in text | No spam, instant return ✅ |
| 5 | "my favorite color is blue" | "That's great! Blue is a lovely color." | Stored in memory ✅ |
| 6 | "what is my favorite color?" | "Your favorite color is blue!" | Remembered from turn 5 ✅ |

---

## Files Changed

| File | What |
|------|------|
| `server.py` | Docstring, imports, `/api/tts` POST endpoint, Ella name, TTS warmup at start |
| `router.py` | User-Agent `Ella/1.0`, X-Title `Ella`, model settings (temp 0.6, top_p 0.9, num_ctx 4096) |
| `routines.py` | Chat/routine prompt split, identity check, today-guard, conversation memory |
| `tts.py` | Added `warmup()` for pre-loading voice model at startup |
| `projects.py` | Expanded SKIP set to filter junk folders (Temp, Logs, _pip_backup, etc.) |
| `web/app.js` | Conversation mode (double-click mic), TTS markdown cleanup |
| `data/brain.json` | Switched model to `qwen2.5:7b` |

## Files Created

| File | What |
|------|------|
| `tts.py` | Piper TTS wrapper with warmup. Returns WAV bytes. |
| `ella.py` | pywebview desktop app launcher. Spawns server, opens window. |
| `bots/ella.json` | Bot identity file |
| `tests/test_ella_chat.py` | 12-test regression suite |

## Not Changed (by design)

| File | Why |
|------|-----|
| `.env` | 36 cloud API keys untouched. OpenRouter, Groq, all others stay. |
| `router.py complete()` | Cloud cascade (openrouter → groq → ollama) untouched. |
| `scout.py` | Free-model scout untouched. |
| `bots/mike/*` | Mike untouched. `rules.md` still empty. |

---

## How to Run

**Browser (dev):**
```
cd "C:\Users\USER\fckkk\cy projects"
python server.py
# open http://127.0.0.1:8765
```

**Desktop app:**
```
cd "C:\Users\USER\fckkk\cy projects"
python ella.py
```

**Requirements already installed:** `faster-whisper`, `piper-tts`, `pywebview`.  
**Ollama must be running:** `ollama serve` (and `ollama pull qwen2.5:7b` once).

---

## UI Redesign (12:14 PM)

Complete FRIDAY-style redesign of the web UI. Backup at `web/_backup_20261103_121403/`.

### Layout

| Area | What |
|------|------|
| **Center Stage** | 320px animated orb — idle cyan breathe, listening reacts to mic, thinking orange spin, speaking green pulse (Web Audio AnalyserNode) |
| **State Label** | Below orb: "Online", "Listening", "Thinking", "Speaking" — color-coded |
| **Live Caption** | Word-by-word typing of Ella's response, 20px centered text |
| **Chat Panel** | Right side, 380px, collapsible. User bubbles right-aligned dark, Ella bubbles left-aligned cyan edge. Timestamps, model tags, copy button. Quick-reply chips. |
| **Input Bar** | Bottom center, 60% width, glass pill. Text input, mic button, send button, stop button (only during speech) |
| **Top Bar** | E.L.L.A. wordmark, LOCAL·QWEN2.5:7B brain pill, status dots, Manila clock, settings gear |
| **Left Rail** | 56px icon nav: Home, Inbox, Tasks, Brain, Health, Settings |
| **Brain Tab** | Full vault graph with hubs, labels on hover, controls drawer (Repel/Link/Filter), inspector panel |

### Style
- Background #05080d with radial glow behind orb
- Cyan #22e5ff, amber #ffb020, green #2bff9a
- Glassmorphism panels: backdrop-blur 12px, 1px cyan border
- Inter font for body, Rajdhani for headings and wordmark
- Smooth 250ms transitions, reduced-motion option

### Features
- Session greeting: Ella says "Morning, Cyrus" (once per session, time-appropriate)
- Keyboard: Space = push-to-talk, Esc = stop, Ctrl+K = focus input, Ctrl+N = new chat
- Settings page: ambient graph toggle, reduced motion, conversation mode
- TTS amplitude drives orb pulse via Web Audio AnalyserNode
- Mic level drives orb pulse during listening

### Screenshots Verified

| State | What's visible |
|-------|---------------|
| Home idle | Orb breathing cyan, "ONLINE", chat panel with history |
| Listening | Orb reacting, "LISTENING", mic button glowing |
| Thinking | Brief orange flash, "THINKING" |
| Speaking | Green orb pulsing with audio, "SPEAKING", stop button, live caption typing |
| Chat 6+ msgs | User/Ella bubbles with timestamps and qwen2.5:7b tags, copy buttons |
| Brain tab | Full graph with hubs, filters, inspector, controls drawer |

---

## Known Limits

- Whisper runs on **CPU int8** (CUDA CTranslate2 build not matching Python
  3.14 yet). Transcription takes ~2 s for a short sentence.
- Piper runs on **CPU**. Synthesis takes ~0.15 s warm, ~6 s cold start.
- pywebview window is not yet packaged as a standalone `.exe` (PyInstaller
  step deferred — the `python ella.py` launcher works now).
- Conversation mode (toggle in Settings or double-click mic).
