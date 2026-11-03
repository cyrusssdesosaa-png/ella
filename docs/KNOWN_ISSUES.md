# Known issues and technical debt

Static audit inventory as of 2026-11-04. No issues here were reproduced by running Ella; source-confirmed facts are labeled accordingly. See `BUG_AUDIT.md` for evidence, severity, fixes and regression risk.

## Highest priority

- **Project context isolation is incorrect (BUG-001):** project history is saved but not supplied back to the model; global main-chat history can be added to project requests.
- **Local API protections need manual verification (BUG-003/005/006/015/018):** Phase 1A adds token, Host/Origin, bounded parsing, path checks and safe rendering in source; no runtime/manual checks have been performed yet.
- **Residual resource controls:** body sizes and total body time are bounded, but request-rate limiting and a global thread/concurrency cap are not implemented; a slow-drip request header can still hold a thread inside the inactivity timeout.
- **Concurrent JSON updates may be lost/collide (BUG-010):** threaded server plus read-modify-write and shared temp filenames.
- **Stop control is not cancellation (BUG-004).**

## Correctness and UX

- Add-project card appears unbound (BUG-002).
- Token cost is hard-coded to zero; context usage/capacity is a misleading static approximation (BUG-007).
- STT/Piper health indicators are unconditional; TTS errors can be hidden (BUG-008).
- Backup scope is partial and restore input handling needs stricter bounds (BUG-009).
- Check-in/time formatting uses host local time in some paths rather than configured timezone (BUG-011).
- Startup wrapper retries forever with fixed delay on nonzero exit (BUG-013).
- Skill map references may not resolve; loaders fail quietly and truncate prompt material (BUG-014).

## Setup and architectural debt

- Fresh checkout defaults to `llama3.2:3b`, while historical project docs say `qwen2.5:7b`; ignored `data/brain.json` was absent, so live configuration is unknown.
- `pywebview` is imported by `ella.py` but is not in `requirements.txt` (BUG-016).
- Vision model is hard-coded to `moondream:latest` and bypasses configured router/scheduler (BUG-017).
- Main chat history is volatile; no explicit conversation/session API.
- No system/hardware resource monitoring, task queue, approval center, integration framework, append-only audit log or general tool sandbox.
- JSON storage has no schema/version migrations; backups omit multiple runtime and user-data categories.
- The UI depends on externally hosted Google Fonts, so the panel is not fully offline (BUG-012).
- `projects.py` scans fixed personal Windows paths and may show incomplete/stale results on other machines.
- Some docs refer to historical installation paths and runtime facts unavailable in the clean clone.

## Phase 1A source mitigations (manual verification pending)

- **BUG-003:** project/user-controlled strings are escaped or rendered as text; style colors are restricted; external project links are limited to parsed HTTP(S).
- **BUG-005:** request bodies have route-specific bounded reads; STT is capped at 25 MiB and restricts audio types.
- **BUG-006:** every API route requires a random per-process token; exact loopback Host and same-host Origin/Fetch Metadata checks are enforced; CORS is not enabled.
- **BUG-015:** malformed/duplicate JSON and suspicious lengths/encodings return controlled errors; unsupported methods are rejected.
- **BUG-018:** project IDs and file-loader names are constrained and resolved beneath approved roots.

These are source-level changes only. Browser/WebView compatibility, rejection behavior, normal voice/project flows, and hostile-but-inert display values still require Cyrus's manual checklist.

## Needs runtime/manual confirmation

- Installed Python version/packages, GPU driver/VRAM, Ollama/model inventory, Piper assets, `.env`, and actual Local/Cloud mode.
- Browser/webview CORS/Origin behavior and any CSRF exploitability.
- Whether historical test cases pass with the actual expected model and audio assets.
- Whether historical backup manifest matches Cyrus's recovery expectations.
- Actual latency, model co-residency, thermal use and concurrent request behavior on target hardware.
