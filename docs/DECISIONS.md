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

## 2026-11-04 — Hybrid assistant with permission-bounded autonomy

- **Decision:** Ella's target is hybrid local/cloud operation, with high autonomy only inside explicit, backend-enforced permissions. Suitable private/everyday work should use local models; sensitive connected-account content must not be forwarded to cloud silently.
- **Reason:** The owner confirmed hybrid operation and autonomous workflows, while retaining local-first privacy and human oversight.
- **Consequence:** Provider choice must consider task, privacy, capability, context and resources. Actual provider/model must be reported. No provider-policy or default-model changes are implied by this decision.
- **Status:** Target direction adopted; current routing remains as documented in `CURRENT_STATE.md`.

## 2026-11-04 — Ella coordinates, existing bots are preserved

- **Decision:** Ella is intended as the coordinating intelligence for specialized bots, but current project windows are not presumed autonomous. Preserve bot configs, prompts, personalities, projects and data.
- **Reason:** Existing bot assets are valuable; execution capabilities must be audited and added incrementally.
- **Consequence:** A shared capability registry, task lifecycle, permissions, approvals, cancellation and execution history precede autonomous delegation.
- **Status:** Target direction adopted; architecture not implemented.

## 2026-11-04 — Single Command Center frontend

- **Decision:** Expand the existing vanilla UI into one Command Center with a collapsible navigation shell and contextual panel; do not create a second frontend. Dashboard status must use actual backend evidence.
- **Reason:** The owner supplied a concrete interface blueprint and explicitly prioritized truthful status over decorative placeholders.
- **Consequence:** Build the shell/dashboard progressively after runtime/backend contracts are stable; preserve ring/chat/voice/token strip/project windows.
- **Status:** Target direction adopted; current UI remains partial.

## 2026-11-04 — Gmail is the first planned service integration

- **Decision:** Prioritize Gmail before Calendar, Drive, GitHub and Notion, using official OAuth/APIs and least-privilege scopes. Read/search/summarize/draft precede sending.
- **Reason:** This is the owner-confirmed initial integration order.
- **Consequence:** Any send requires backend approval showing recipient, subject, complete body and attachments. Secret storage, audit, disconnect/revoke and approval foundations must exist first.
- **Status:** Planned; no Gmail integration or authorization is implemented.

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
11. What specific resources/actions may any automation grant cover, and what expiry/rate limits should apply?
12. What exact Gmail OAuth scopes are sufficient for each initial read/draft/send milestone?
13. Which service is responsible for a single-instance Ella server lock and graceful shutdown on Windows?
