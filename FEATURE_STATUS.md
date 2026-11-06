# Ella FEATURE_STATUS - phase1-reliability

**Branch:** cut from `phase1-reliability` (Phase 1A–1J). Not on `main`.  
**Updated:** 2026-11-06 (Asia/Manila)  
**Convention:** rows marked **implemented, awaiting manual verify** are in source but have not been accepted by Cyrus via a live Ella/Ollama session on his PC. Offline unittest `tests/test_phase2_offline.py` covers the Phase 2 engines only. It does not start Ella or Ollama and is not manual verification.

## Phase 1 reliability on this branch

| ID | Focus | Status | Key commits | Notes |
|---|---|---|---|---|
| 1A | Local API Host/Origin/token, body limits, safe rendering | Implemented, awaiting manual verify | `fb8e2c5` (main lineage) | See `docs/SECURITY.md`, `docs/TEST_CHECKLIST.md`. |
| 1B | Session isolation (main vs project / concurrent turns) | Implemented, awaiting manual verify | `f8771f7` | Per-request session state; no shared mutable chat session across concurrent asks. |
| 1C | Store + outbox locks (atomic unique temps, RMW helpers) | Implemented, awaiting manual verify | `f8771f7` | `file_transaction` / `locked_update` / `multi_file_transaction`; outbox RMW locked. |
| 1D | Honest model / provider labels in UI + responses | Implemented, awaiting manual verify | `f8771f7` | Actual provider/model surfaced; not a full token-cost ledger. |
| 1E | Real Stop - cancel in-flight model/vision | Implemented, awaiting manual verify | `7ee823a` | `/api/cancel` + `cancel.py` epoch; main Stop visible while thinking; skips outbox/history on stop. Offline smoke OK on box for `7ee823a`. |
| 1F | Lock `brain.json` RMW + backup/restore snapshots | Implemented, awaiting manual verify | `0263e9d` | `save_brain` via `locked_update`; backup/restore under `multi_file_transaction`; startup brain create under `file_transaction`. |
| 1G | Lock profile/memory RMW + quota/free-models/missed overwrites | Implemented, awaiting manual verify | `add1b18` | `save_profile` holds profile+memory locks; missed-day claim via `locked_update`; quota/free-models writers via `locked_update`; startup profile/memory init under `file_transaction`. |
| 1H | Project-window Stop + paste/focus routing | Implemented, awaiting manual verify | `659757d` | Project windows show a red Stop while a project ask is in flight, wired to the same `stopEverything()` -> `/api/cancel` as main (cancel is a global epoch: Stop in any window stops all in-flight asks; each busy window shows "Stopped."). Paste target resolved synchronously from the paste target / last-interacted surface (mousedown/focusin), so image paste goes to the project window you clicked even when focus is on its chat area; never falls through to main when a project was the target. Ctrl+K focuses the last-used project window. No drag-drop exists in the UI (not added). |
| 1I | Vision personality/history (BUG-017) + `brain.json` in backup (BUG-009) | Implemented, awaiting manual verify | (this push) | `run_vision` builds prompt via `build_vision_prompt` (same identity / project prompt / history policy as text, truncated for moondream). Main vision updates `_chat_history`; project vision uses `build_project_prompt` + session prior. Uses configured `OLLAMA_URL`. Cancel tokens still honored. `make_backup` / `restore_backup` allowlist now includes `brain.json` (model/local-cloud prefs). Still hard-codes `moondream:latest` as the vision model (not a shared scheduler). Secrets (`.env`, vault) still excluded. |
| 1J | Single-server owner / start-stop gate | Implemented, awaiting manual verify | `3825864` | `server.main` takes an exclusive `msvcrt` lock on `data/server.lock` (PID written for info) before touching any data file; second copy prints "already running (PID n)" and exits code 3. OS drops the lock if the owner dies, so a stale file never blocks start (no manual cleanup; deleting `data/server.lock` is safe when no Ella python is running). HTTP bind uses `SO_EXCLUSIVEADDRUSE` / no `SO_REUSEADDR` (Windows default allowed double-bind on :8765). `ella.py` detects child exit 3 and shows a clear message box instead of opening a window onto the other instance; `startup.bat` stops looping on code 3. Lock released + socket closed on clean shutdown. |

## Phase 2 core architecture

Later Command Center, memory, and agent work should call these modules. They do not replace the Phase 1 chat, Stop, lock, or owner-gate paths.

| ID | Focus | Status | Notes |
|---|---|---|---|
| 2A | Permission engine L1–L4 | Implemented, awaiting manual verify | `permissions.py`. L1 observe, L2 prepare (no side effects), L3 modify local state Ella already owns, L4 external. L4 always needs an explicit user approval object and `may_execute_external` stays false. Prompt text is not approval. |
| 2B | Task engine | Implemented, awaiting manual verify | `tasks.py`. A request becomes steps, each step is permission-checked, and the record is stored with `locked_update` in `data/tasks.json` (also on the backup allowlist, under the existing `multi_file_transaction`). Progress includes unfinished steps. L4 steps stay `awaiting_approval` across a reread and a resume, even if the file is edited to say done. No model call and no external integration. |
| 2C | Context manager | Implemented, awaiting manual verify | `context_manager.py`. Default is local. Cloud routing is allowed only when `brain.json` mode is already `cloud`, and only through the existing OpenRouter / Groq / Ollama order. Secrets are withheld. The check does not send data. Unknown modes fail closed to local. Vision stays local. |
| 2D | Model capability registry | Implemented, awaiting manual verify | `model_registry.py`. Vision calls `moondream:latest` via `vision_model_id()`; chat default remains `llama3.2:3b`. Unknown models stay unknown. `cost_known` is false. No token prices were added. No extra model is loaded. |

`/api/state` includes a `phase2` object (levels, context switch, capability snapshot, unfinished task summary). `GET/POST /api/tasks` reads or saves a plan. Both use the existing Host/Origin/token checks. The panel UI is unchanged.

## Known issues still open (not claimed fixed this turn)

- **1J owner gate** - implemented in source on `phase1-reliability` (`3825864`), awaiting manual verify on Cyrus's PC. It is not an open "not started" item.
- **BUG-001 remnants / broader isolation** - 1B addresses concurrent session isolation in source; full project-history-in-prompt and related isolation defects still need Cyrus live verification before closing.
- **BUG-010 residual** - JSON concurrency risk reduced for locked paths above; any future RMW must use the same helpers. Not a claim that every JSON file is covered. `store.py` uses `fcntl` only when `msvcrt` is missing, so offline tests can run the same helpers. Windows still uses `msvcrt`.
- **Vision model hard-code** - the registry records `moondream:latest` and `run_vision` calls that id. There is still no shared vision/chat scheduler or unload policy (BUG-017 remains open).
- **Backup scope still partial** - `tasks.json` joined the allowlist with Phase 2. Project sessions, usage/quota logs, vault, and `.env` remain outside the allowlist.
- **Phase 2 is not an approval center** - there is no Approvals UI, no standing grant, no audit log product, and no Gmail/calendar/spend integration. L4 is recorded and not run.

## Explicitly not started this turn

- Image drag-and-drop into windows (no DnD handler exists yet)
- Shared vision/chat model scheduler / unload policy
- External integrations (send, post, spend, new cloud vendors)
- Approval Center UI and revocable standing grants
- Token price ledger
- Starting Ella, Ollama, or live GUI tests on Cyrus's PC

## How to verify (owner)

1. Restart Ella from this branch tip and hard-refresh the panel.
2. Walk `docs/TEST_CHECKLIST.md` items for security, chat isolation, Stop during think, profile/fact save, brain mode switch, backup/restore.
3. Vision: in main chat, send an image after a short text exchange; reply should stay in Ella's voice and can reference recent chat. In a project window, send an image; reply should follow that project's prompt and not leak main-chat history.
4. Backup: run Backup, confirm the zip contains `brain.json` and `tasks.json` when a task file exists; change Local/Cloud or model, Restore that zip, confirm brain prefs return.
5. Phase 2, still on his PC: `GET /api/tasks` with the page token returns the task report. A plan whose step level is 4 stays unfinished and does not send anything. With Local mode on, `phase2.context.allow_cloud` is false and `phase2.model_capabilities.vision_model` is `moondream:latest`. Switching the existing Local/Cloud control is what flips the context flag. Do not treat a unit test as this check.
6. Only then flip a row from **awaiting manual verify** to **manually verified**.
