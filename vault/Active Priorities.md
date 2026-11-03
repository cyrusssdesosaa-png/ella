---
status: active
project: meta
type: plan
---

# Active Priorities

- [x] OpenRouter and Groq keys are in `.env`. The values stay out of notes.
- [x] The default brain is local Ollama. Cloud is a switch on the panel.
- [x] Start Ollama, then pick a small installed model. Default is now `qwen2.5:7b` (4.7 GB).
- [x] Rename assistant from Jarvis to Ella. Ring label, title, persona, toasts all updated.
- [x] Local voice loop: faster-whisper STT + Piper TTS (jenny_dioco-medium). Both wired through `/api/stt` and `/api/tts`.
- [x] Side panel is up at `http://127.0.0.1:8765`.
- [x] Memory vault is the long memory. The newest 30 facts stay in `data/memory.json`.
- [x] Bug 1 fixed: Ella says "I'm Ella" not "I'm Cyrus" (qwen2.5:7b + identity guard).
- [x] Bug 2 fixed: Real Manila time injected into system prompt.
- [x] Bug 3 fixed: Check-in today-guard prevents spam. Root cause was zombie server process.
- [x] TTS warm start: Piper pre-loads at server start. First call 0.15s.
- [x] 12/12 regression tests pass (`tests/test_ella_chat.py`).
- [ ] PyInstaller .exe packaging.
- [ ] GitHub skill packs stay uncloned until each one is scanned.
- [ ] Mike does not post. `bots/mike/rules.md` is empty.
