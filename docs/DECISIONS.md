# Architecture decision log

Dates are in ISO format. This log records decisions for this repository takeover; unresolved questions remain open rather than being guessed.

## 2026-11-04 — Preserve the existing application

- **Decision:** Keep the existing Python backend, vanilla web UI, project windows, bots, profiles, skills and vault as the baseline. Do not replace the frontend or migrate storage during the audit.
- **Reason:** The user explicitly requires preservation; the code has working, bounded capabilities and valuable personal knowledge assets.
- **Consequence:** Introduce future architecture behind incremental service/adapter seams; no broad rewrite.
- **Status:** Adopted for this documentation task.

## 2026-11-04 — Document implementation separately from vision

- **Decision:** `docs/CURRENT_STATE.md` describes code-backed behavior; `docs/ELLA_MASTER_PLAN.md` and `docs/ROADMAP.md` describe future intent.
- **Reason:** Existing docs include historical and aspirational statements that do not consistently match a clean checkout.
- **Consequence:** Historical `RESULT.md`, `MEMORY.md`, `CLAUDE.md` and vault content are preserved and not treated as live verification.
- **Status:** Adopted.

## 2026-11-04 — No storage migration now

- **Decision:** Keep JSON runtime persistence and Markdown vault unchanged until backup scope, data ownership, migration/recovery and schema are approved.
- **Reason:** Runtime `data/` is absent from checkout; migration would be speculative and could endanger private state.
- **Consequence:** Document present JSON/vault boundaries and propose SQLite as a future option, not a commitment.
- **Status:** Adopted.

## 2026-11-04 — Local means no silent cloud fallback (target policy)

- **Decision:** Target local mode must fail closed to local Ollama; Online mode must be explicit and visible.
- **Reason:** Current router's Cloud cascade can fall back to Ollama, which makes the current Cloud mode hybrid; policy should be unambiguous in both directions.
- **Consequence:** Provider changes require mode-bound tests, privacy disclosure and visible provider identity.
- **Status:** Target decision; implementation is pending.

## 2026-11-04 — Keep current UI and add incrementally

- **Decision:** Retain existing ring/chat/voice/token strip/project windows; do not redesign during repository foundation work.
- **Reason:** Avoid destroying interface work or creating competing frontends.
- **Consequence:** Future inbox, command center and approval surfaces should extend `web/` and its navigation.
- **Status:** Adopted.

## Open decisions

1. Is Cloud mode intended as cloud-only or current hybrid fallback behavior? Should routine requests ever leave device?
2. Which Ollama model should be the default on Cyrus's actual machine? The runtime file is absent; the code fallback and historical notes differ.
3. What is the preferred persistent chat/session retention policy?
4. What data should backups cover, and should vault/user content be encrypted in backups?
5. Which integration is valuable enough to prioritize, and which APIs/terms permit it?
6. Should project chat context be completely isolated or explicitly share a selected subset?
7. Is a local API token/Origin policy compatible with the intended browser and pywebview access pattern?
8. What should the “stop” action cancel, and which tasks can safely be interrupted?
9. Is SQLite sufficient, and is vector search justified by measured needs?
10. What are acceptable verified resource/latency targets for the actual Windows hardware?
