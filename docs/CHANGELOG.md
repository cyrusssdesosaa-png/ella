# Changelog

This log starts with the repository takeover documentation on 2026-11-04. It does not retroactively convert historical `RESULT.md` assertions into verified releases.
## 2026-11-04 — UI-1 Command Center shell and navigation (committed, published)

- Commit: `753225f` (`Complete Ella Command Center UI-1 foundation`) on `main`, pushed to `origin/main`.
- Added a grouped 13-destination Command Center navigation rail to `web/index.html`: Dashboard, Ella Chat, Projects, Bots, Tasks, Automations, Inbox, Integrations, Memory, Approvals, Activity, System Monitor, and Settings.
- Added placeholder views for Bots, Tasks, Automations, Integrations, and Approvals. Existing views are reused for Dashboard/Ella Chat, Projects, Memory, Inbox/Activity, System Monitor, and Settings.
- Added UI-1 styling in `web/styles.css` for rail grouping/labels, expand/collapse, page headers, placeholder panels, status badges, responsive breakpoints, and topbar height adjustment.
- Added view-alias handling and rail toggle behavior in `web/app.js`; no backend routes, authentication, or security behavior changed.
- No runtime data, bot configurations, profiles, skills, vault contents, dependencies, or backend source were changed. No tests, services, or model inference were run.
- Bot execution, task management, automation, integrations, approvals, hardware monitoring, and full Command Center data integration remain future work.



## 2026-11-04 — Local startup, smoke checks, and runtime investigation

- Started the committed Ella server for browser access after the owner requested it. The first page inspection showed an older server instance; after explicit approval, that identified instance was stopped and the committed server was launched.
- After the restart, read-only browser/API smoke checks observed: page HTTP 200, unauthenticated `/api/state` HTTP 401, token-authorized state HTTP 200 with Local mode, and malformed JSON HTTP 400. These are narrow smoke checks, not a full regression/security acceptance.
- The existing `tests/test_ella_chat.py` command was invoked after the owner said “test it,” but the command returned no captured result. **No pass/fail result is known; this is not recorded as a successful test run.**
- A later read-only runtime inspection found two Python `server.py` processes and inconsistent/ambiguous port-8765 socket evidence. No process was stopped, restarted, or modified during that inspection. Correct single-instance ownership remains unresolved and is an immediate roadmap gate.

## 2026-11-04 — Owner-confirmed Command Center blueprint

- Aligned the master plan and roadmap with the confirmed hybrid/local-first, permission-bounded autonomy, preserved-bot coordination, Gmail-first integration and unified Command Center direction.
- Added the Phase 1A–1E through Phase 14 sequence, the outstanding runtime-reliability gate, and progressive interface delivery order.
- Reaffirmed that Cyrus performs manual acceptance and explicitly authorizes testing, service control, commits and pushes.
- Clarified that these are product plans, not implemented capabilities; no application code, runtime data, tests, services or integrations were changed or run for this planning update.

## 2026-11-04 — Ella check-in note

- Appended a check-in session entry to the November 4 daily vault note. No application source or configuration changed in that commit.
- Published as commit `d5f013e` (`Record Ella check-in session`).

## 2026-11-04 — Phase 1A local API security foundation

- Added in-memory per-server API token delivery through the served HTML and token checks on all `/api/*` requests.
- Enforced loopback Host validation, matching Origin checks, Fetch Metadata rejection for cross-site requests, no CORS allow-origin response, and security response headers/CSP.
- Added strict body length/type/encoding/JSON validation, route-specific size limits, bounded string/list schemas, controlled 4xx/5xx errors and method rejection.
- Constrained project/profile/brain/skill identifiers and resolved local paths; rejected backup path-like names.
- Added raster container-signature and image-dimension checks, and audio container-signature checks before local decoders are invoked.
- Added per-request header inactivity timeouts with controlled 408 handling, an overall bounded body-read deadline, and rejection of GET bodies to reduce slow-client thread retention and request desynchronization.
- Hardened project UI rendering, image preview validation and external link protocols while preserving the existing frontend.
- Updated the existing live-server test client to obtain the per-run token from the local HTML page. A later test invocation had no captured result; it remains a live/inference test and is not considered passed.
- Updated security/API/current-state/bug/known-issue/manual-checklist documentation. No dependencies or runtime data changed.
- **Implementation validation:** static diagnostics, Python syntax validation, project-config shape inspection and diff checks were completed. No full test result is claimed. Cyrus must complete the manual checklist before Phase 1B.

## 2026-11-04 — Local model and hardware audit

- Added `MODEL_HARDWARE_AUDIT.md` with read-only hardware inspection and installed Ollama model metadata/recommendations.
- Recommended installed `llama3.2:3b` as the everyday/default candidate and `qwen2.5:7b` as the higher-capability installed option; no model/configuration was changed or downloaded.
- Published with the documentation and Phase 1A work in commit `fb8e2c5` (`Harden Ella local API and document system audits`).

## 2026-11-04 — Repository takeover documentation

- Verified repository root, `main` branch, GitHub origin, baseline commits and clean pre-edit worktree.
- Added source-based current-state, architecture, bug/security, storage, API, integrations, development rules, decisions, roadmap and manual test documentation.
- Updated `README.md` to reflect checked-in behavior and known configuration discrepancies.
- Added `docs/ELLA_MASTER_PLAN.md`, `CURRENT_STATE.md`, `ARCHITECTURE.md`, `BUG_AUDIT.md`, `INTEGRATIONS.md`, `SECURITY.md`, `DATABASE_DESIGN.md`, `API_DESIGN.md`, `DEVELOPMENT_RULES.md`, `DECISIONS.md`, `ROADMAP.md`, `CHANGELOG.md`, `KNOWN_ISSUES.md` and `TEST_CHECKLIST.md`.
- Preserved application code, UI, bots, profiles, skills, project config, vault and existing historical docs.
- No application features, dependencies, runtime data or tests changed/run. Ella, Ollama and live integrations were not started or contacted.
- Published with commit `fb8e2c5` (`Harden Ella local API and document system audits`).

## Historical notes (not release verification)

- `RESULT.md` contains a dated report claiming an Ella P0 build, voice loop, packaging setup and 12/12 live regression tests. Those statements describe the report author's historical session; they were not reproduced in this audit. In particular, the current tree has an un-packaged pywebview wrapper and `pywebview` is not in `requirements.txt`.
- `vault/Active Priorities.md` and `vault/02 - Jarvis/panel.md` contain project status notes. They are preserved and should be checked against the actual machine before acting on them.
- Git history at takeover contains two commits: `a0cb05d` (“Add Ella and the files it needs to run.”) and `6fcc105` (“Note the private GitHub home in the panel inventory.”). No additional historical changes are inferred here.
