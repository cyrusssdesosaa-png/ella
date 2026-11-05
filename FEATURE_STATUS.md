# Ella FEATURE_STATUS — phase1-reliability

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
| 1E | Real Stop — cancel in-flight model/vision | Implemented, awaiting manual verify | `7ee823a` | `/api/cancel` + `cancel.py` epoch; main Stop visible while thinking; skips outbox/history on stop. Offline smoke OK on box for `7ee823a`. |
| 1F | Lock `brain.json` RMW + backup/restore snapshots | Implemented, awaiting manual verify | `0263e9d` | `save_brain` via `locked_update`; backup/restore under `multi_file_transaction`; startup brain create under `file_transaction`. |
| 1G | Lock profile/memory RMW + quota/free-models/missed overwrites | Implemented, awaiting manual verify | *(this commit)* | `save_profile` holds profile+memory locks; missed-day claim via `locked_update`; quota/free-models writers via `locked_update`; startup profile/memory init under `file_transaction`. |

## Known issues still open (not claimed fixed this turn)

- **Vision personality skip** — vision/`moondream` path does not apply the configured chat personality/router policy (related to BUG-017). Do not treat as done.
- **Paste-to-wrong-window** — clipboard image paste can still target the wrong chat surface when main + project windows compete for focus.
- **Project Stop button UI** — main chat has real Stop (`7ee823a`); project windows still lack an equivalent Stop control wired to `/api/cancel`.
- **BUG-009 — `brain.json` not in backup allowlist** — `make_backup` / `restore_backup` still omit `brain.json` (and other runtime files). 1F locked the snapshot; it did not widen the allowlist.
- **Single-server owner gate** — runtime reliability gate (one intentional owner of port 8765 / predictable start-stop) remains outstanding; see `docs/ROADMAP.md`.
- **BUG-001 remnants / broader isolation** — 1B addresses concurrent session isolation in source; full project-history-in-prompt and related isolation defects still need Cyrus live verification before closing.
- **BUG-010 residual** — JSON concurrency risk reduced for locked paths above; any future RMW must use the same helpers. Not a claim that every JSON file is covered.

## Explicitly not started this turn

- Vision personality work
- Paste-to-correct-window UI fix
- Project-window Stop button UI
- Widening backup allowlist / BUG-009 content fix
- Starting Ella, Ollama, or live tests on Cyrus's PC

## How to verify (owner)

1. Restart Ella from this branch tip and hard-refresh the panel.
2. Walk `docs/TEST_CHECKLIST.md` items for security, chat isolation, Stop during think, profile/fact save, brain mode switch, backup/restore.
3. Only then flip a row from **awaiting manual verify** to **manually verified**.
