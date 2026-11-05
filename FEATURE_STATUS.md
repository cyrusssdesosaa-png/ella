# Ella FEATURE_STATUS - phase1-reliability

**Branch:** `phase1-reliability`  
**Updated:** 2026-11-06 (Asia/Manila)  
**Convention:** rows marked **implemented, awaiting manual verify** are in source on this branch but have not been accepted by Cyrus via a live Ella/Ollama session on his PC. Offline box smoke of `7ee823a` covered session isolation / locks / model tags / Stop cancel only.

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

## Known issues still open (not claimed fixed this turn)

- **Single-server owner gate** - runtime reliability gate (one intentional owner of port 8765 / predictable start-stop) remains outstanding; see `docs/ROADMAP.md`.
- **BUG-001 remnants / broader isolation** - 1B addresses concurrent session isolation in source; full project-history-in-prompt and related isolation defects still need Cyrus live verification before closing.
- **BUG-010 residual** - JSON concurrency risk reduced for locked paths above; any future RMW must use the same helpers. Not a claim that every JSON file is covered.
- **Vision model hard-code** - vision still uses `moondream:latest` only (not brain-selected chat model / shared queue). Personality+history gap closed in 1I; resource-scheduler part of BUG-017 remains open.
- **Backup scope still partial** - project sessions, usage/quota logs, vault, and `.env` remain outside the allowlist by design this turn.

## Explicitly not started this turn

- Single-server owner gate
- Image drag-and-drop into windows (no DnD handler exists yet)
- Shared vision/chat model scheduler / unload policy
- Starting Ella, Ollama, or live tests on Cyrus's PC

## How to verify (owner)

1. Restart Ella from this branch tip and hard-refresh the panel.
2. Walk `docs/TEST_CHECKLIST.md` items for security, chat isolation, Stop during think, profile/fact save, brain mode switch, backup/restore.
3. Vision: in main chat, send an image after a short text exchange; reply should stay in Ella's voice and can reference recent chat. In a project window, send an image; reply should follow that project's prompt and not leak main-chat history.
4. Backup: run Backup, confirm the zip contains `brain.json`; change Local/Cloud or model, Restore that zip, confirm brain prefs return.
5. Only then flip a row from **awaiting manual verify** to **manually verified**.