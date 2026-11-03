# Cy projects knowledge pack

This folder is the memory for Cyrus's own AI. It is not a copy of Claude or Cursor. It is the record of the projects built together, and the skills that AI should load.

Read this order:

1. `profiles/INDEX.md` to pick the project.
2. `profiles/operator.md` for who Cyrus is and how he works.
3. The one project profile that matches the task.
4. The one skill in `skills/` that matches the task.

Load one project profile and one skill per turn. Do not paste the whole library into every reply.

Big builds stay on `D:\` (the 1 TB drive, volume label "1tb yey"). `C:` stays light. This knowledge pack lives on `C:\Users\USER\fckkk\cy projects` because that is the Jarvis workspace.

## What it needs

- Python 3.11 or newer.
- `pip install -r requirements.txt` for voice (`faster-whisper`, Piper, PyAV).
- Ollama running with `ollama serve`, and the model `qwen2.5:7b`. Screenshots use `moondream`.
- Piper voice files in `D:\ella-voices` (or set `ELLA_VOICES`). The voice name is `jenny_dioco-medium`.
- Copy `.env.example` to `.env` and paste your own keys. `.env` is not in git.
- Start the panel with `startup.bat`. It serves `http://127.0.0.1:8765`.

Chat logs, backups, and `.env` stay on this PC.

## Side panel

`startup.bat` serves Ella at `http://127.0.0.1:8765`. The full map of what is on screen is `vault/02 - Jarvis/panel.md`. The panel has the ring, chat, voice, a token ledger, and one window per project bot. OpenCode edits the opened project. This panel does not.

`CLAUDE.md` is the boot file. `vault/VAULT-INDEX.md` is the map. A job reads that map, then one note. The newest 30 facts stay in `data/memory.json`.

Copy `.env.example` to `.env` and paste your own keys. Chat uses OpenRouter's free models. Check-ins use Groq, then Ollama.

Cursor finds the same skills through `.cursor/skills/` in this folder. Those entries point here. Edit the files in `skills/` and `profiles/`. Do not keep a second copy.
