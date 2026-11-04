# Ella: current state

**Audit date:** 2026-11-04
**Scope:** source and checked-in assets in this checkout; no app, service, integration, or test was run.

This document records what repository code supports. It does not claim the machine has the models, voice assets, keys, dependencies, or hardware state needed to use every path.

## Repository baseline

- Root: `D:\ella`; Git root is this directory.
- Branch: `main`, tracking `origin/main` at `https://github.com/cyrusssdesosaa-png/ella`.
- Baseline HEAD: `e7da87e` (`Document Ella development history and blueprint`), preceded by `d5f013e` (`Record Ella check-in session`) and `fb8e2c5` (`Harden Ella local API and document system audits`). UI-1 frontend work is currently uncommitted in the working tree.
- Initial audit working tree was clean. No ignored runtime files were present; no `.env`, `data/`, or backup archive was in the worktree. Documentation edits made for this takeover are described in `docs/CHANGELOG.md`.
- No separate root `docs/` folder existed before this documentation set. The repository has one live-server test script, inspected but not run; its API helpers now obtain the per-process token from the served page.

## UI-1 Command Center shell (uncommitted frontend work)

- Added a grouped 13-destination Command Center navigation rail in `web/index.html`: Dashboard, Ella Chat, Projects, Bots, Tasks, Automations, Inbox, Integrations, Memory, Approvals, Activity, System Monitor, and Settings.
- Added placeholder views for Bots, Tasks, Automations, Integrations, and Approvals. Existing views are reused for Dashboard/Ella Chat, Projects, Memory, Inbox/Activity, System Monitor, and Settings.
- Added styling in `web/styles.css` for rail grouping, labels, expand/collapse, page headers, placeholder panels, status badges, responsive breakpoints, and topbar height adjustment.
- Added view-alias handling in `web/app.js`; no backend routes or security behavior changed.
- No task, automation, integration, approval, bot-runtime, hardware-monitoring, or full Command Center data integration is implemented. Placeholder pages state their unimplemented status.


## Actual components

| Area | Verified implementation | Limits / status |
|---|---|---|
| HTTP server | `server.py` uses `ThreadingHTTPServer`, bound to `127.0.0.1:8765`; serves three web assets and GET/POST JSON/audio routes. | Phase 1A adds exact loopback Host validation, per-process token auth for all API routes, Origin/Fetch Metadata checks, strict bounded body parsing, per-route schemas, controlled errors, and security headers. No TLS or explicit lifecycle manager. Not runtime-tested. |
| Browser UI | `web/index.html`, `web/app.js`, `web/styles.css`: vanilla single-page panel with ring, chat, canvas visualizations, navigation, project launcher/windows, graph, systems and activity surfaces. | Existing fetch architecture preserved; shared and direct audio requests attach the page token. Project rendering now escapes or uses DOM text APIs and validated styles. Not runtime-tested. No SSE/WebSocket. Google Fonts CDN is referenced. |
| Chat/providers | `routines.py` builds prompts and in-memory main chat history; `router.py` calls Ollama, OpenRouter and Groq. | `brain.json` chooses Local or Cloud. Local calls only Ollama. Cloud chat tries OpenRouter → Groq → Ollama; routines try Groq → Ollama. In Cloud, Ollama fallback means “Cloud” does not guarantee a cloud-only response. |
| Vision | `/api/ask` can send an attached image to a hard-coded local Ollama `moondream:latest` generate route. | This path bypasses `router.py` and does not use a model scheduler. Actual model presence and VRAM use are unknown. |
| Voice | `stt.py` wraps faster-whisper (`base.en` default, CUDA then CPU fallback); `tts.py` wraps Piper (`jenny_dioco-medium` default, voice files under `D:\ella-voices` by default). Browser uses MediaRecorder and `/api/stt`, then asks the model and calls `/api/tts`. | STT forces English. API now caps audio at 25 MiB and restricts media types; TTS errors are sanitized. External model/voice files and optional CUDA libraries are not checked in. Runtime behavior remains unverified. |
| Project windows | `bots/projects.json` defines project persona prompts/actions/links; `server.py` stores up to 100 messages per project in ignored `data/sessions/`. | These are prompt-configured chat windows, not autonomous agents. Project history is stored but is not included in the model prompt; main chat context can leak into project prompts. |
| Runtime persistence | `store.py` writes JSON settings, profile, facts, activity, token calls, check-ins, outbox, sessions, and backup files under `data/`; log lines go to `data/jarvis.log`. | No relational database, schema migration, encryption layer, vector database, or common multi-file transaction. Main chat history is process memory only. |
| Vault | `vault/` contains Markdown project/personal knowledge, indexes, daily notes and an attribution notice. `vault.py` searches by filename, builds a file-name graph, reads notes and appends session notes. | It is not semantic retrieval. Graph edges/relationships are not derived; search is substring-based. Preserve contents and attribution. |
| Skills and profiles | `skills/`, `profiles/`, `.cursor/skills/`, `bots/` provide project knowledge and agent instructions. Project cards load every configured skill/profile/brain file into their prompt through `server.py`. | There is no automatic task-based skill selector in backend. Several configured names do not resolve to `skills/<name>/SKILL.md`; `SKILL_MAP` is a UI listing, not a loader. Cursor skill copies are a tracked subset, not generated/synchronized. Keep all assets intact. |
| Routines/scout | `routines.py` implements check-in, adapt, outbox retry and token logging; `scout.py` fetches OpenRouter's public model catalog. | Not a general scheduler. Startup may launch a missed-check-in thread. Scout is network-dependent. |
| Desktop wrapper | `ella.py` launches a child server process and a pywebview window. | Not a packaged installer. `pywebview` is imported but absent from `requirements.txt`; wrapper does not start Ollama. |
| Startup | `startup.bat` changes to repo directory and loops running `python server.py` after nonzero exit. | It does not start Ollama. A persistent failure can cause repeated restarts. |

## Configuration and runtime defaults

- `.env.example` contains empty placeholders for OpenRouter/Groq, an Ollama URL, and an optional provider key. `router.load_env()` reads `.env` directly; it does not load the process environment or a full dotenv format.
- Fresh runtime defaults in `server.py`/`routines.py` are Local mode and `llama3.2:3b`. Historical `README.md`, `RESULT.md`, and vault notes state `qwen2.5:7b`; the ignored runtime `data/brain.json` was absent here, so the active per-machine choice cannot be verified.
- Token reports include prompt/completion counts when supplied by provider, keep 80 calls and cumulative prompt/completion totals. `cost` is hard-coded 0; `ctx_used` is latest prompt tokens against a static 4,096 context label. This is not a cost ledger or context-occupancy measurement.
- Settings and personal project content are not necessarily secrets but can be sensitive. Do not copy private details into public-facing docs.

## Phase 1A security status

Source now requires a random in-memory token on every API route, delivered only in the no-store HTML document; Host is limited to the supported local aliases, supplied API Origins must match that host, and no CORS access is granted. JSON/audio routes have explicit size/type limits and validation; project IDs and file-loader names are constrained to their intended roots; project/UI text is escaped and style values are allowlisted. See `docs/SECURITY.md` and `docs/API_DESIGN.md` for exact behavior. No tests, requests, services or browser flows were run after these changes; manual verification is pending.

## Prompt claims: verification labels

| Claim | Status | Audit note |
|---|---|---|
| Browser panel at loopback port 8765 | **Verified in code** | `server.py` binds the stated host/port; not live-tested. |
| `startup.bat` starts Ella | **Verified in code** | Starts/restarts `server.py`; does not start Ollama. |
| Ollama endpoint at 11434 | **Partially verified** | Default URL is in code and `.env.example`; service/model availability unknown. |
| `qwen2.5:7b` is active/default | **Outdated for a fresh checkout / runtime unknown** | Code fallback is `llama3.2:3b`; runtime JSON absent. Historical notes are not runtime evidence. |
| `moondream` screenshot analysis | **Partially verified** | Hard-coded Ollama call exists; model installed and fit unknown. |
| Piper files under `D:\ella-voices` | **Verified as code default only** | Presence and actual voice unverified. |
| OpenRouter/Groq integrations | **Verified in source, not live-tested** | Keys/config not present; no network calls made. |
| Local-only / offline guarantee | **Not implemented as a guarantee** | Local model mode stays on Ollama, but cloud mode, scout and Google Fonts can use network. |
| STT and TTS full loop | **Partially verified** | Wiring exists; not executed; status/error shortcomings remain. |
| Project bots execute jobs/tools | **Not implemented** | Prompt-driven chats and quick actions only; no tool execution framework. |
| Session persistence | **Partial** | Project sessions persist; primary chat is in-memory and lost on restart. |
| Task engine, approvals, integration center, audit log | **Not implemented** | Some labels, activity items, and stop flag exist, not these systems. |
| GPU/hardware monitoring | **Unknown / not implemented in repo** | No machine probe for CPU/RAM/GPU/VRAM/temperature. Hardware profile is user-provided, not code-verified. |
| Packaged PC app | **Not implemented as a package** | `ella.py` is an un-packaged wrapper. |
| Existing 12/12 test result | **Historical claim only** | `RESULT.md` reports it; test file calls the live server and uses real model/voice routes. No tests run during this audit. |

## Existing assets preserved

- Bots and configs: `bots/`, including `projects.json`, Ella/Jarvis identity JSON, and Mike reference/rules files.
- Profiles: `profiles/` project/operator notes.
- Skills: `skills/` and `.cursor/skills/`.
- Knowledge vault: complete `vault/` tree, including daily notes, active priorities, project notes, and `vault/NOTICE.md` attribution.
- Existing UI and backend: `web/` and root Python files.
- Historical instructions/report: `CLAUDE.md`, `CURSOR_TASK_LOCAL_GPU.md`, `MEMORY.md`, `NOTES.txt`, `RESULT.md`.
- The backend reads `bots/projects.json` as its project-window registry; `bots/ella.json` and `bots/jarvis.json` are not loaded by that registry. `CLAUDE.md` retains the Jarvis identity, so identity-era instructions are mixed.
- Project cards have incomplete profile/path mappings; one configured project has an empty path. Runtime behavior should be confirmed before treating card metadata as functional access.

They were not rewritten or deleted. See `docs/ARCHITECTURE.md`, `docs/BUG_AUDIT.md`, and `docs/KNOWN_ISSUES.md` for evidence-linked details.
