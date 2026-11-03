# Changelog

This log starts with the repository takeover documentation on 2026-11-04. It does not retroactively convert historical `RESULT.md` assertions into verified releases.

## 2026-11-04 — Phase 1A local API security foundation

- Added in-memory per-server API token delivery through the served HTML and token checks on all `/api/*` requests.
- Enforced loopback Host validation, matching Origin checks, Fetch Metadata rejection for cross-site requests, no CORS allow-origin response, and security response headers/CSP.
- Added strict body length/type/encoding/JSON validation, route-specific size limits, bounded string/list schemas, controlled 4xx/5xx errors and method rejection.
- Constrained project/profile/brain/skill identifiers and resolved local paths; rejected backup path-like names.
- Added raster container-signature and image-dimension checks, and audio container-signature checks before local decoders are invoked.
- Added per-request header inactivity timeouts with controlled 408 handling, an overall bounded body-read deadline, and rejection of GET bodies to reduce slow-client thread retention and request desynchronization.
- Hardened project UI rendering, image preview validation and external link protocols while preserving the existing frontend.
- Updated the existing live-server test client to obtain the per-run token from the local HTML page; it was not executed and still performs inference/STT/TTS when Cyrus chooses to run it.
- Updated security/API/current-state/bug/known-issue/manual-checklist documentation. No dependencies or runtime data changed.
- **Not tested:** no tests, Ella/Ollama, browser flows, integrations, or inference were run. Cyrus must complete the manual checklist before Phase 1B.

## 2026-11-04 — Repository takeover documentation

- Verified repository root, `main` branch, GitHub origin, baseline commits and clean pre-edit worktree.
- Added source-based current-state, architecture, bug/security, storage, API, integrations, development rules, decisions, roadmap and manual test documentation.
- Updated `README.md` to reflect checked-in behavior and known configuration discrepancies.
- Preserved application code, UI, bots, profiles, skills, project config, vault and existing historical docs.
- No application features, dependencies, runtime data or tests changed/run. Ella, Ollama and live integrations were not started or contacted.

## Historical notes (not release verification)

- `RESULT.md` contains a dated report claiming an Ella P0 build, voice loop, packaging setup and 12/12 live regression tests. Those statements describe the report author's historical session; they were not reproduced in this audit. In particular, the current tree has an un-packaged pywebview wrapper and `pywebview` is not in `requirements.txt`.
- `vault/Active Priorities.md` and `vault/02 - Jarvis/panel.md` contain project status notes. They are preserved and should be checked against the actual machine before acting on them.
- Git history at takeover contains two commits: `a0cb05d` (“Add Ella and the files it needs to run.”) and `6fcc105` (“Note the private GitHub home in the panel inventory.”). No additional historical changes are inferred here.
