# Ella roadmap

This roadmap follows the requested phase order. Security work begins in Phase 0 and gates any tool, automation or external integration capability. Status is based on source inspection on 2026-11-04, not live testing.

| Phase | Goal | Initial deliverables / exit criteria | Status |
|---|---|---|---|
| 0. Repository takeover and audit | Establish facts and docs without replacing app. | Architecture/source map, current-state and security/bug audit; data/assets preserved; decisions and manual checklist. | **Documentation completed** in this change; no runtime validation. |
| 1. Core reliability and session persistence | Fix high-risk correctness/availability issues. | Project-session isolation; defined conversation persistence; robust JSON writes; bounded requests; clear errors/cancellation; model/dependency defaults reconciled; manual acceptance. | Planned; first implementation milestone. |
| 2. Token accuracy and systems monitoring | Make measurement trustworthy. | Separate cumulative/session/day counters, actual context capacity/use, timing, provider/model, cost provenance; health probes for backend/Ollama/STT/TTS; resource metrics only where verified. | Planned. |
| 3. Interface improvements and Command Center | Extend existing UI without second frontend. | Core inbox/command center, current task/mode/model/project/status, reduced motion, responsive states, accessible errors, lightweight rendering. | Partial UI exists; target center not implemented. |
| 4. Memory and knowledge system | Improve source-linked recall without losing vault. | Session/short/long/project/procedural boundaries; retrieval/index policy; source citations; correction/delete/export; Memory Explorer. | Markdown vault and facts exist; advanced system planned. |
| 5. Task engine and automation | Durable bounded work lifecycle. | Queue, decomposition, priority/dependencies, schedule, progress events, cancellation, retry limits, reports and safe persistence. | Not implemented beyond selected synchronous routines. |
| 6. Security and permission framework | Enforce least privilege before actions. | Local API protection, permission capabilities, exact-action approvals, audit, secret store, path allowlist/sandbox, redaction, stop semantics, threat-model review. | Partial basics only; critical gaps remain. Must gate later phases. |
| 7. Integration framework | Consistent connection/auth/health lifecycle. | Adapter contract, official-API review, secrets, scopes, rate limits, disconnect, tests/mocks, provider mode guarantees. | Basic model adapters only; broad framework planned. |
| 8. Agents and specialized bots | Evolve existing prompt windows carefully. | Preserve bots; per-agent workspace/memory/tools/permissions, schedules, event history and supervision. | Prompt-configured windows exist; execution/isolation do not. |
| 9. Voice and communication | Reliable accessible local voice and selected communication adapters. | STT/TTS health/error UX, language/voice configuration, wake/hotkey only after permission/privacy review, local-first input/output. | Partial STT/TTS loop in code; not run in this audit. |
| 10. Career, content and productivity | Research/draft/track without fabricated claims. | Source-backed job/content research, truthful drafts, approval-gated submission/publishing, per-platform terms and rate limits. | Personas/plans exist; external workflows not implemented. |
| 11. Self-healing and recovery | Bounded supervised recovery. | Health-based checks, exponential backoff, restart caps, safe restart boundaries, recovery log and escalation; no unrelated process termination. | Startup retry loop exists but is not a watchdog. |
| 12. Windows desktop application | Reliable package around current UI/backend. | Dependency/preflight checks, process ownership, clean shutdown, install/update/rollback; retain browser dev mode. | pywebview launcher exists; package/installer not verified or built. |
| 13. Advanced intelligence | Improve intent, planning, vision and multimodal reasoning. | Explicit uncertainty, clarifying questions, sourced knowledge, local vision/media queue and review step. | Partial image route; remainder planned. |
| 14. Continuous maintenance | Sustainable operations. | Dependency/security updates, backup/restore drills, issue triage, regression checks, documented release process and periodic privacy review. | Planned. |

## Recommended first implementation milestone

**Phase 1 reliability slice**, with security fixes from Phase 6 treated as prerequisites:

1. Confirm with Cyrus current desired default model, mode semantics, and how project contexts should be scoped.
2. Add a project-session-scoped prompt/history boundary; do not leak main chat context.
3. Make the local API reject malformed/oversized requests and protect state-changing routes.
4. Add per-file write serialization/unique temp files and bounded startup retry behavior.
5. Make stop/cancel semantics honest; do not label a flag as cancellation.
6. Correct UI/provider accounting labels and expose STT/TTS failures.
7. Define backup manifest and verify restore separately before expanding backup behavior.

Acceptance is manual and reviewable; no service/test run is implied. For each change, produce a diff and Cyrus's test checklist. Details and risks are in `docs/BUG_AUDIT.md`, `docs/SECURITY.md`, and `docs/DEVELOPMENT_RULES.md`.
