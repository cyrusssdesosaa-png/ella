# Ella

Ella is Cyrus's existing local personal-assistant panel and project knowledge workspace. Its current implementation combines a Python standard-library HTTP server, a browser-based single-page interface, Ollama/cloud model routing, local speech-to-text and text-to-speech wrappers, project prompt windows, and a Markdown vault. The long-term direction is local-first, private, modular, and approval-gated; several parts of that vision remain planned rather than implemented.

## Current status

- **Implemented in the repository:** localhost panel, chat, Local/Cloud mode setting, Ollama/OpenRouter/Groq adapters, browser image submission to an Ollama vision model, vault search/graph/note reading, project prompt windows, JSON-based project sessions, check-ins, usage ledger, local STT, and Piper TTS wrappers. On `phase1-reliability`, Phase 1A–1J plus a Phase 2 permission/task/context/model-registry base are in source and awaiting manual verify (`FEATURE_STATUS.md`). That base does not send external actions.
- **Not established by this checkout:** which models and voice files are installed, whether Ollama is running, the live provider mode, hardware utilization, and whether the historical test results remain reproducible. Runtime data under `data/` and `.env` are intentionally absent from this checkout.
- **Important:** “local-first” is not equivalent to “offline-only.” The Cloud mode, model scout, and Google-hosted fonts can make external requests. Local mode in the model router selects Ollama only.

See [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md) for verified details and [docs/ELLA_MASTER_PLAN.md](docs/ELLA_MASTER_PLAN.md) for the intended direction.

## Architecture at a glance

- `server.py` serves the UI and JSON/audio endpoints on `127.0.0.1:8765` using `ThreadingHTTPServer`.
- `web/` contains the existing vanilla HTML/CSS/JavaScript interface. It uses `fetch()` requests; there is no WebSocket/SSE event stream.
- `router.py` routes local requests only to Ollama; Cloud chat tries OpenRouter, Groq, then Ollama, while routines try Groq then Ollama. Unknown modes stay on Ollama.
- `permissions.py`, `tasks.py`, `context_manager.py`, and `model_registry.py` are the Phase 2 base. Vision stays `moondream:latest`. L4 steps are stored and not run.
- `stt.py` wraps faster-whisper with CUDA then CPU fallback. `tts.py` wraps Piper. Voice files and model weights are external local assets.
- `store.py` persists runtime state as JSON and logs under the ignored `data/` directory. The Markdown vault under `vault/` is separate durable knowledge; it is not a database.
- `bots/projects.json`, `profiles/`, and `skills/` provide project-specific prompts and reference material. The project windows are prompt-driven chats, not autonomous tool-running agents.

The detailed source-backed diagrams are in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Requirements and configuration

- Windows development environment; Python 3.11+ is described in the existing project notes, but the repository does not pin a Python version.
- Python dependencies are listed in [requirements.txt](requirements.txt): faster-whisper, Piper, and PyAV. `ella.py` also imports `pywebview`, which is not listed there; it is only needed for the optional desktop wrapper.
- Ollama is a separate service. Its default URL is `http://127.0.0.1:11434`; model selection is persisted at runtime in `data/brain.json`. On a fresh checkout the code default is `llama3.2:3b`, despite historical notes describing `qwen2.5:7b`.
- Piper voice files default to `D:\ella-voices`; configure `ELLA_VOICES` and `ELLA_VOICE` as environment variables if needed. STT defaults to `base.en`, configurable with `ELLA_STT_MODEL`.
- Optional provider keys are read from a local `.env`; see [.env.example](.env.example). Do not commit `.env` or paste secrets into docs, logs, prompts, or source. Local mode does not require cloud keys.
- Project paths and some persona material refer to Cyrus's machine and may need review before use on another computer.

## Safe startup (not run as part of this audit)

1. Install the required Python packages in the intended environment using `requirements.txt`.
2. Start/configure Ollama separately if local inference is wanted; `startup.bat` does **not** launch Ollama.
3. From the repository directory, run `startup.bat` to start the browser panel at `http://127.0.0.1:8765`. It repeatedly restarts `server.py` after nonzero exits, so stop it with the terminal's normal interrupt when finished. Do not use this script as a production service manager.
4. The optional `python ella.py` desktop wrapper requires `pywebview`; it spawns a server child process and opens the same web UI.

This documentation audit did not start Ella, Ollama, or integrations and did not execute tests. Review [docs/TEST_CHECKLIST.md](docs/TEST_CHECKLIST.md) before manual verification.

## Repository knowledge assets

- `profiles/` contains project and operator context.
- `skills/` contains task-specific instructions; `.cursor/skills/` includes related Cursor entries. Treat personal project context as user data and do not duplicate it into general engineering docs.
- `bots/` contains project-window configuration and bot reference files. Preserve these assets; the existing backend does not execute their declared actions as system tools.
- `vault/` is the Markdown knowledge vault. Existing historical notes and vault attribution are preserved.

## Documentation index

- [Current state](docs/CURRENT_STATE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Master plan](docs/ELLA_MASTER_PLAN.md)
- [Roadmap](docs/ROADMAP.md)
- [Bug audit](docs/BUG_AUDIT.md)
- [Known issues](docs/KNOWN_ISSUES.md)
- [Security](docs/SECURITY.md)
- [API design](docs/API_DESIGN.md)
- [Database design](docs/DATABASE_DESIGN.md)
- [Integrations](docs/INTEGRATIONS.md)
- [Development rules](docs/DEVELOPMENT_RULES.md)
- [Decisions](docs/DECISIONS.md)
- [Changelog](docs/CHANGELOG.md)
- [Manual test checklist](docs/TEST_CHECKLIST.md)

## Development workflow

For each change: inspect the implementation and working tree, state the problem and affected files, prefer a focused backward-compatible edit, review the diff, update the relevant documentation, and provide a manual test checklist. Do not run live services or tests without Cyrus's direction. Do not push or commit changes automatically. The complete rules are in [docs/DEVELOPMENT_RULES.md](docs/DEVELOPMENT_RULES.md).
