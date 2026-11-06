# Ella roadmap

This roadmap reflects the owner-confirmed autonomous/hybrid Command Center blueprint. It is a plan, not an implementation claim. Security and truthful capability reporting are cross-cutting gates. Current status is source-based; no phase is considered manually accepted without Cyrus's review.

## Runtime reliability gate (immediate)

Before adding new intelligence, tools, or dashboard claims:

1. Establish which Ella process owns port 8765 and ensure there is one intentional server owner.
2. Define predictable startup/shutdown and process ownership.
3. Check Ollama and configured-model availability without changing model defaults.
4. Report actual provider/model per response and truthful dependency health.
5. Verify graceful failures when local/cloud providers are unavailable.
6. Preserve Phase 1A API protections and complete its manual acceptance checklist.

**Status:** Implemented in source as Phase 1J on `phase1-reliability` (`server.py` exclusive `data/server.lock`, exit code 3 for a second copy, exclusive port bind). Awaiting manual verify on Cyrus's PC. This is not an open "not started" item. See [FEATURE_STATUS.md](../FEATURE_STATUS.md).

## Phased plan

Rows 1B–1E keep their original audit wording. On `phase1-reliability` those slices were continued as Phase 1B–1J and are implemented in source, awaiting manual verify. [FEATURE_STATUS.md](../FEATURE_STATUS.md) is the status board for that branch.

| Phase | Focus | Deliverables / exit criteria | Status |
|---|---|---|---|
| 0 | Repository takeover and architecture audit | Source-backed architecture, current state, risks and preservation baseline. | **Complete**; docs committed. |
| 1A | Security foundation | Local API Host/Origin/token checks, validation/body limits, safe inputs/rendering, documented manual checks. | **Implemented in committed source; manual verification pending.** |
| 1B | Conversation isolation | Separate main/project conversations and context; explicit session IDs and no accidental cross-context prompts. | Planned; known defect BUG-001. |
| 1C | Reliable JSON persistence | Serialized writes, unique atomic temp files, corruption recovery and backup/restore strategy without premature migration. | Planned; known risk BUG-010. |
| 1D | Cancellation and task lifecycle | Honest cancellation semantics, task states, progress/results/failures; no false completion claims. | Planned; current stop flag does not cancel. |
| 1E | Accurate model/provider/token reporting | Actual provider/model, usage provenance, honest context/cost and dependency health. | Planned; current UI/accounting limitations remain. |
| 1J (listed here earlier as Phase 2) | Runtime reliability and startup manager | One owned server, predictable start/stop, Ollama/model/dependency checks, graceful provider failures and real health status. | **Implemented in source as Phase 1J; awaiting manual verify.** Health/dependency checks beyond the owner gate are still partial. |
| 2 | Core permission, task, context, and model registry | Backend engines for later Command Center, memory, and agents: L1–L4 permissions, durable task plans, local-first context policy, truthful model capabilities. | **Implemented in source; awaiting manual verify.** No L4 execution, no new cloud vendor, no token prices, no Approvals UI. |
| 3 | AI behavior and capability registry | Registered capabilities declare implementation, availability, authorization and current operation; shared execution/result/error contracts. | Phase 2 registers configured chat/vision roles and permission levels. Availability-now, authorization-in-operation, and a shared execution contract are still planned. |
| 4 | Agent execution and bot management foundation | Preserve bots; controlled registration/delegation, isolated permissions/memory, execution records and cancellation. | Prompt windows exist; autonomous execution not implemented. |
| 5 | Hybrid AI routing | Task/privacy/resource-aware local/cloud policy; actual provider metadata; explicit disclosure and no silent sensitive-data forwarding. | Basic routes exist. Phase 2 adds a local-first context gate for the existing providers. Resource-aware routing is still planned. |
| 6 | Permission and approval center | Backend-enforced Observe/Prepare/Modify/External permissions; action-bound approvals and revocable scoped automation grants. | Phase 2 engine enforces L1–L4 and refuses to run L4. Approval Center UI, expiry, and revocable grants are not implemented. |
| 7 | Integration framework and OAuth | Reusable adapter lifecycle, secure token storage, least privilege, health, revoke/disconnect, audit and mocks. | Not implemented beyond model APIs. |
| 8 | Gmail integration | Search/read/summarize, authorized labels, drafts; send only after full-content action-specific approval. | Not implemented. |
| 9 | Calendar and Drive | Official API/OAuth and explicit scopes; truthful connection/health and approval for mutations. | Not implemented. |
| 10 | GitHub and project workspace | Authorized repo/project context, source-backed tasks and project-specific isolation. | Not implemented as an integration/workspace service. |
| 11 | Automation engine | Schedules/triggers, conditions, assigned bot, scope, run history, retry/cancel and immediate revoke/override. | Not implemented beyond selected synchronous routines. |
| 12 | Expanded Command Center interface | Extend the existing vanilla app with real dashboard, nav shell, collapsible context panel, bots/tasks/automations/inbox/integrations/memory/approvals/activity/system/settings. | UI-1 Command Center shell/navigation implemented in frontend (committed `753225f` on `main`); backend-dependent views remain future work. |
| 13 | Advanced bot coordination | Delegation, result evaluation, consolidated response and permission-preserving bot-to-bot coordination through Ella. | Planned; depends on Phases 3, 4 and 6. |
| 14 | Maintenance, recovery and optimization | Bounded watchdog, backups/recovery drills, dependency/security upkeep, measurable resource baselines and release discipline. | Planned. |

## Interface delivery order

Build incrementally in the single existing frontend: (1) application shell and navigation; (2) Dashboard from verified current backend data; (3) chat/task status and project contracts; (4) bot/task/automation management when those backends exist; (5) Inbox and Gmail only after OAuth/approval foundations; (6) Integration, Memory, Approvals, Activity and System Monitor views as their data contracts become real. Unimplemented items must be visibly planned/unavailable, not decorative fake controls.

## Phase 2 core engines (2026-11-06)

Phase 1A–1J are already on `phase1-reliability`. The next core slice is in source and **awaiting manual verify**:

- `permissions.py` — L1 observe, L2 prepare, L3 modify owned local state, L4 external. L4 never auto-executes.
- `tasks.py` — plan, per-step permission check, `data/tasks.json` via `locked_update`, progress and unfinished steps. L4 stays unfinished.
- `context_manager.py` — local by default. Cloud only when the existing brain mode is `cloud`, and only through OpenRouter, Groq, and Ollama.
- `model_registry.py` — vision is `moondream:latest`. No prices. No extra resident model.

This does not finish later roadmap rows (agent autonomy, Gmail, the Approvals UI, or a model scheduler). Offline unittest coverage is `tests/test_phase2_offline.py`. That run does not start Ella or Ollama and is not manual acceptance.

## Next milestone

Cyrus manually verifies Phase 1A–1J and these Phase 2 engines on his PC, then accepts or rejects each row. Do not treat them as accepted before that. Do not add external integrations until L4 stays approval-gated. Live Ella, Ollama, and inference runs stay his call.

For each implementation, list affected files, risk, data impact, rollback, and a manual checklist. Preserve the existing bots, projects, profiles, skills, memory, vault and working interface. Details are in [BUG_AUDIT.md](BUG_AUDIT.md), [SECURITY.md](SECURITY.md), and [DEVELOPMENT_RULES.md](DEVELOPMENT_RULES.md).
