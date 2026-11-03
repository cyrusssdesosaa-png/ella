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

**Status:** Outstanding. A read-only process snapshot found two `server.py` processes and ambiguous/transient TCP table evidence. No process cleanup or restart is authorized here. See [CURRENT_STATE.md](CURRENT_STATE.md) and [SECURITY.md](SECURITY.md).

## Phased plan

| Phase | Focus | Deliverables / exit criteria | Status |
|---|---|---|---|
| 0 | Repository takeover and architecture audit | Source-backed architecture, current state, risks and preservation baseline. | **Complete**; docs committed. |
| 1A | Security foundation | Local API Host/Origin/token checks, validation/body limits, safe inputs/rendering, documented manual checks. | **Implemented in committed source; manual verification pending.** |
| 1B | Conversation isolation | Separate main/project conversations and context; explicit session IDs and no accidental cross-context prompts. | Planned; known defect BUG-001. |
| 1C | Reliable JSON persistence | Serialized writes, unique atomic temp files, corruption recovery and backup/restore strategy without premature migration. | Planned; known risk BUG-010. |
| 1D | Cancellation and task lifecycle | Honest cancellation semantics, task states, progress/results/failures; no false completion claims. | Planned; current stop flag does not cancel. |
| 1E | Accurate model/provider/token reporting | Actual provider/model, usage provenance, honest context/cost and dependency health. | Planned; current UI/accounting limitations remain. |
| 2 | Runtime reliability and startup manager | One owned server, predictable start/stop, Ollama/model/dependency checks, graceful provider failures and real health status. | **Immediate gate outstanding.** |
| 3 | AI behavior and capability registry | Registered capabilities declare implementation, availability, authorization and current operation; shared execution/result/error contracts. | Planned. |
| 4 | Agent execution and bot management foundation | Preserve bots; controlled registration/delegation, isolated permissions/memory, execution records and cancellation. | Prompt windows exist; autonomous execution not implemented. |
| 5 | Hybrid AI routing | Task/privacy/resource-aware local/cloud policy; actual provider metadata; explicit disclosure and no silent sensitive-data forwarding. | Basic routes exist; policy/routing framework planned. |
| 6 | Permission and approval center | Backend-enforced Observe/Prepare/Modify/External permissions; action-bound approvals and revocable scoped automation grants. | Phase 1A API controls are not this action-approval system; planned. |
| 7 | Integration framework and OAuth | Reusable adapter lifecycle, secure token storage, least privilege, health, revoke/disconnect, audit and mocks. | Not implemented beyond model APIs. |
| 8 | Gmail integration | Search/read/summarize, authorized labels, drafts; send only after full-content action-specific approval. | Not implemented. |
| 9 | Calendar and Drive | Official API/OAuth and explicit scopes; truthful connection/health and approval for mutations. | Not implemented. |
| 10 | GitHub and project workspace | Authorized repo/project context, source-backed tasks and project-specific isolation. | Not implemented as an integration/workspace service. |
| 11 | Automation engine | Schedules/triggers, conditions, assigned bot, scope, run history, retry/cancel and immediate revoke/override. | Not implemented beyond selected synchronous routines. |
| 12 | Expanded Command Center interface | Extend the existing vanilla app with real dashboard, nav shell, collapsible context panel, bots/tasks/automations/inbox/integrations/memory/approvals/activity/system/settings. | Partial existing panel only; future UI depends on backend contracts. |
| 13 | Advanced bot coordination | Delegation, result evaluation, consolidated response and permission-preserving bot-to-bot coordination through Ella. | Planned; depends on Phases 3, 4 and 6. |
| 14 | Maintenance, recovery and optimization | Bounded watchdog, backups/recovery drills, dependency/security upkeep, measurable resource baselines and release discipline. | Planned. |

## Interface delivery order

Build incrementally in the single existing frontend: (1) application shell and navigation; (2) Dashboard from verified current backend data; (3) chat/task status and project contracts; (4) bot/task/automation management when those backends exist; (5) Inbox and Gmail only after OAuth/approval foundations; (6) Integration, Memory, Approvals, Activity and System Monitor views as their data contracts become real. Unimplemented items must be visibly planned/unavailable, not decorative fake controls.

## Next milestone

**Resolve and manually verify the runtime reliability gate**, then proceed to Phase 1B conversation isolation. Do not start Phase 1B until Cyrus identifies the intended server process and approves any restart/cleanup. Do not run tests, start Ella/Ollama, perform inference, or contact integrations without the owner's explicit instruction.

For each implementation, list affected files, risk, data impact, rollback, and a manual checklist. Preserve the existing bots, projects, profiles, skills, memory, vault and working interface. Details are in [BUG_AUDIT.md](BUG_AUDIT.md), [SECURITY.md](SECURITY.md), and [DEVELOPMENT_RULES.md](DEVELOPMENT_RULES.md).
