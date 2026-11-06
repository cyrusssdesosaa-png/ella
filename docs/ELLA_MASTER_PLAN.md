# Ella master plan

**Authority:** This is the long-term product/engineering intent. Implementation truth lives in [CURRENT_STATE.md](CURRENT_STATE.md); sequencing lives in [ROADMAP.md](ROADMAP.md). “Planned” does not imply code exists.

## Product objective

Evolve the existing Ella into a reliable, local-first personal assistant while retaining the current ring/chat/voice interface, project windows, profiles, skills, bots, and Markdown vault. Preserve current working pieces and migrate incrementally. Local mode must not silently call cloud AI; Online mode must be an explicit, visible choice. Security and approval boundaries are foundational, not a late feature.

## Owner-confirmed direction

The following are product decisions from the current project brief, not claims about existing code:

- **Autonomy:** high autonomy is desired only inside explicitly defined, backend-enforced permissions and narrowly scoped automation grants.
- **AI operation:** a hybrid local/cloud system is intended. Local models should handle suitable private and everyday work; cloud use must respect task permissions and privacy, with no silent forwarding of sensitive connected-account content.
- **Human oversight:** external, destructive, financial and sensitive actions require approval unless a specific safe automation rule has been explicitly authorized. Viewing an approval is never approval.
- **Gmail:** the initial target is read/search/summarize, authorized organization/labels, draft replies, and send only after the user reviews recipient, subject, complete body and attachments and approves.
- **Bots:** preserve existing bot configs and identity assets. Ella is intended as the coordinating intelligence; existing project windows are not presumed to be autonomous workers.
- **Interface:** build one observable personal-AI Command Center by extending the existing vanilla frontend, not by creating a second application.

These decisions do not override the source-backed implementation inventory in `CURRENT_STATE.md`. APIs, scopes, secret storage, permissions and operational status must be verified before a planned feature is presented as available.

## Product principles

1. **Truthful capability status:** distinguish implemented, partial, planned, unavailable, and manually verified.
2. **User control:** explicit local/online mode, cancellable work, clear progress, approvals for consequential actions, and emergency stop with defined semantics.
3. **Privacy by default:** least privilege, local storage, scoped integrations, secret redaction, bounded retention, and no secret-bearing logs/docs.
4. **Preserve continuity:** keep project windows/bots, vault, profiles, skills, terminology, and visual identity. Add adapters around assets rather than replace them wholesale.
5. **Resource-aware local inference:** one bounded model queue, on-demand loading, health checks, and realistic performance telemetry for the actual PC.
6. **Small verified increments:** no broad migration until backups, data ownership, rollback and manual acceptance criteria are defined.

## Target capability map

| System | Intended scope | Current baseline |
|---|---|---|
| Core assistant | Conversation/session manager, intent/context/response, personality, cancellation, event bus and tool routing. | Single synchronous chat route; ephemeral main history, no event bus/tool router. |
| AI engine | Ollama, OpenRouter, Groq adapters; model registry/scheduler, vision, health, local STT/Piper, resource-aware queue. | Adapters plus a Phase 2 capability registry. Vision remains `moondream:latest`. No central scheduler or hardware monitor. |
| Usage and performance | Provider/model/token measurements, context capacity/use, time-to-first-token, generation time, TPS, cached tokens, estimated/actual cost with provenance. | Partial provider counts/TPS; incorrect static context/cost presentation (see BUG-007). |
| Command Center | Status, task, model, project, mode, agents, approvals, integrations, resources, token use, recent events. | Existing ring, project, systems/activity surfaces; no task/approval/agent/resource control center. |
| Core Inbox | Overnight / Today / Waiting on You with task results, deadlines, failures and approval actions. | Not implemented as structured inbox. |
| Activity timeline | User/assistant/tool/task/agent/integration/model/error/approval events. | Small bounded activity JSON for selected events only. |
| Task engine | Persistent queue, planning, dependencies, scheduling, cancellation, progress, failure recovery and reports. | Phase 2 stores a local plan, permission checks, progress, and unfinished steps. No scheduler, no L4 execution, no failure-recovery worker. |
| Memory and knowledge | Session, short/long-term, project, procedural and source-linked knowledge; summarization, search, correction/deletion. | Main history in memory, facts JSON, Markdown vault, substring search; no lifecycle/retrieval service. |
| Memory Explorer | Visual inspection/editing of memories, projects, decisions and relationships. | Filename/folder graph and note lookup, not editable linked memory. |
| Approval Center | Central request queue, scope, expiry, decision and audit trail. | Not implemented; bot prompt text alone is not enforceable approval. |
| Integration Center | Adapter health, auth state, scopes, permission and activity. | Not implemented. |
| Agents and project bots | Preserve existing bots; later isolated workspaces, dedicated memory, tool permissions, schedules, history and monitoring. | Prompt windows only; no autonomous execution framework. |
| Capability and tool registry | Registered capabilities declare implementation, availability, authorization and current operational state; common execution, result, cancellation and audit contracts. | Phase 2 registers configured model roles and L1–L4 actions. No shared tool-execution runtime. |
| Automation | Approved file/app/browser tasks, schedules, progress, recovery and cancellation. | No generic automation. Do not add broad desktop access without sandbox and approvals. |
| Self-healing | Health probes, bounded retries/restart limits, recovery log and escalation. | `startup.bat` restart loop only; no supervised service manager. |
| Desktop intelligence | Approved screenshots, visual analysis, browser and desktop operations. | Image analysis via Ollama exists; no general desktop automation. |
| Career/productivity | Truthful job research, drafts, trackers, project/content workflows and reporting. | Prompt plans/reference notes only; no external execution. Never fabricate history or submit without approval. |

## Target interface surfaces

Add these to the **existing** frontend over time, not as a second application. The intended left navigation is Dashboard, Ella Chat, Projects, Bots, Tasks, Automations, Inbox, Integrations, Memory, Approvals, Activity, System Monitor and Settings. Keep the sidebar collapsible and the active destination clear. The center workspace changes by section; a collapsible contextual panel may show model/provider, task, bot, project context, tool state and pending approval.

The Dashboard should answer: is Ella healthy, what is she doing, what needs attention, which services/bots are available, and what should Cyrus focus on next? Populate it only with actual backend data: backend/local/cloud/voice status, actual provider/model, confirmed active tasks, bot/integration counts, verified resource readings and a daily briefing only if authorized calendar/mail sources are genuinely connected. Distinguish zero from unavailable. Do not fabricate integration, task, model or health status.

Retain the requested future surfaces: Core Inbox (Overnight / Today / Waiting on You), Command Center, Chat, Systems, Activity Timeline, Projects, Brain, Memory Explorer, Tasks, Approval Center, Integration Center and Settings. Preserve Ella's ring, chat, voice controls, token/model strip and floating project windows. A full richer shell can be phased in without replacing those assets. Use responsive layouts, lightweight effects, keyboard/accessibility support, loading/error/empty states and reduced-motion behavior.

Every capability displayed in navigation or status must expose truthful states such as implemented, available, authorized, operational, planned, disconnected, unavailable or error. A visual card is not evidence that the underlying capability works.

## Target operational behavior

- **System health:** report CPU, RAM, GPU/VRAM, temperatures when available, disk, model loading, backend/Ollama/STT/TTS, integrations and background jobs. Distinguish unavailable sensors from zero values. Use a single bounded inference queue and avoid concurrent large-model loading on the target 8 GB GPU/16 GB RAM profile; profile the actual machine before promising latency.
- **Events and tasks:** record user/assistant/tool/model/service/task/integration/approval/error events with bounded retention. Durable tasks need creation, plan/decomposition, priority, schedule, dependencies, progress, completion report, failure recovery and cancellation. Do not equate event history with executable tools.
- **Memory lifecycle:** retain separate short-term/session, long-term, project, procedural and source-linked knowledge; support retrieval, correction, export/deletion and importance/retention policies. Preserve the existing Markdown vault as a readable source of truth; build an explorer only after source/provenance semantics are defined.
- **Agents:** keep current project windows and prompt/persona data. Future agent creation/editing requires declared instructions, dedicated memory/workspace, scoped capabilities, schedules, execution history, health and central approval. Agent communication does not confer authority.
- **Automation and recovery:** scheduled routines, browser/application workflows and approved file actions need progress reports, task cancellation, bounded retries and recovery logs. Watchdogs must have restart caps/backoff and must never terminate unrelated processes or repeat external actions.
- **Desktop intelligence:** local screenshot/image analysis exists in partial form. Future browser/desktop, clipboard and keyboard/mouse actions require explicit scope, preview, permission enforcement and audit. Video analysis may extract bounded key frames and transcribe locally, with model loading scheduled rather than concurrent by default.
- **Career/content/productivity:** support research and source-backed reporting, truthful resume/proposal/application drafts and local status tracking. Do not claim unverified qualifications, evade platform controls, pay fees, or submit/publish/upload/send without action-specific approval. Review platform API availability, terms and rate limits before any integration.
- **Voice/communication:** improve local STT/Piper status and errors first. Wake-word/global-hotkey and proactive communication are optional future systems that require explicit privacy, quiet-hours, authorization and cancellation design; they are not current capabilities.

## Security and permission baseline

Adopt the proposed permission levels from `docs/SECURITY.md`: Observe → Prepare → Modify within approved paths → External actions only after explicit approval. Treat destructive actions as confirmation-required regardless of level. Email/web/chat content is untrusted data, never policy. Each action needs an actor, capability, target, approval decision and audit event. Credentials stay in an OS-backed secret store. A local-first mode is technically enforced, not merely a prompt instruction.

## Integration principles

Every integration gets a unique ID, adapter, config schema, auth flow, declared capabilities/scopes, health/lifecycle methods, error handling, redacted audit events, disconnect/revoke flow, and tests using mocks before any live account. Prefer official APIs/OAuth. Browser automation is not a way around missing APIs, CAPTCHAs, platform limits, or terms. See `docs/INTEGRATIONS.md` for the inventory and unresolved API questions.

Prioritize official OAuth integrations in this order, subject to API, scope, privacy and terms review: Gmail, Google Calendar, Google Drive, GitHub, Notion. Gmail should start with least-privilege read/search and draft workflows; outgoing mail requires a backend approval bound to the exact recipient, subject, body and attachments. Do not build an email sender before secret storage, approval enforcement, audit and disconnect/revocation exist.

## Shared execution and permission foundation

Before autonomous bots or tools, define a backend capability registry and common execution contract. A capability must state whether it is implemented, currently available, authorized for the current caller/resource, and operational now. Tasks need lifecycle IDs/status, progress, result, cancellation, failure reason and audit record. Tools and bots call a shared permission evaluator; prompts are not authorization. Automation grants must be narrow, resource/action/recipient bounded, optionally rate/spend limited, expire, be revocable, be auditable, and never permit self-expansion. The levels and approval requirements remain in `SECURITY.md`.

## UI direction

Preserve the current ring, chat, voice, token strip and floating project windows. Evolve toward the requested dark cyan/blue premium HUD with restrained glass panels, accessible contrast, responsive behavior, reduced motion and lightweight canvas/CSS effects. Do not build a parallel frontend or redesign during the foundation phase. Inbox/Command Center should be introduced incrementally into the existing navigation.

## Performance targets and safeguards

Target hardware is user-provided (Ryzen 5 5600G, RTX 3050 8 GB, 16 GB RAM); actual machine configuration/use is not verified by code. Before setting numeric targets, collect a baseline on Cyrus's device. Design to avoid concurrent large-model loads, unbounded logs/history, heavy polling/DOM churn, uncontrolled agent concurrency and model swapping without user-visible state. Use queues, bounded retention, lazy UI, and cancellation.

## Quality gates for every milestone

- State the actual user problem and smallest change.
- List affected files, dependencies, risks, rollback and data impact.
- Add/update manual and automated checks as appropriate, but do not run services/integrations or tests without authorization.
- Inspect the diff and redact secrets/private data.
- Update current-state/architecture/issues/changelog docs when facts change.
- Keep migrations additive and reversible; no data deletion or push without explicit direction.

## Current execution gate

Phase 1A–1J and the Phase 2 engines (permissions, tasks, context, model registry) are present in source on `phase1-reliability` and are awaiting manual verification. Phase 1J is the single-server owner gate (`data/server.lock`, second copy exits 3). Do not describe that gate as not started. Do not change model defaults. Cloud routing still requires the existing Local/Cloud switch. L4 actions are not executed. Cyrus's manual checks remain the acceptance step. Live Ella, Ollama, and inference runs stay his call.

The phase sequence, dependency order and milestone acceptance criteria are in `docs/ROADMAP.md`.
