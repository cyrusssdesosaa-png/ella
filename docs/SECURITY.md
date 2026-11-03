# Security and privacy model

**Status:** Phase 1A API protections are implemented in source as of 2026-11-04; they have **not** been runtime-tested. This is not a security certification. Ella is a personal local app with access to private project/persona/vault material.

## Permission levels

| Level | Meaning | Example policy |
|---|---|---|
| 0 — Observe | Read/analyze explicitly authorized information. | No filesystem traversal outside selected roots; no network writes. |
| 1 — Prepare | Draft plans, text, code or proposed changes without applying/sending. | Show source and destination; no side effects. |
| 2 — Modify | Change files only within approved paths. | Show diff/backup and require confirmation for destructive or broad edits. |
| 3 — External action | Send, post, submit, upload, publish, purchase or transact. | Require explicit, action-specific confirmation immediately before execution. |

Destructive actions always require confirmation. Higher permissions never arise from prompt text, an integration message, or another bot's approval. Cyrus may grant narrowly scoped, revocable standing approval only after the policy UI and audit record exist.

## Implemented Phase 1A API protections

- **Binding/Host:** the server remains bound to `127.0.0.1:8765`. Every request must have exactly one `Host`, either `127.0.0.1:8765` or `localhost:8765`. Other hostnames, ports, malformed and duplicate Host values are rejected. This reduces DNS-rebinding/Host-header abuse; it does not protect against local malware or a compromised Windows account.
- **Authorization:** each server process generates a cryptographically random, in-memory token. The token is inserted only into the served HTML meta element; every supported GET/POST API route must include `X-Ella-Request-Token`. Unsupported methods return a data-free 405 and are not dispatched. The token is not written to `.env`, source, runtime JSON, API state or logs. Restarting the server invalidates old page tokens; reload the panel. This avoids a login screen but is not a boundary against same-origin XSS, local processes, browser extensions or malware.
- **Origin/Fetch Metadata:** if `Origin` is present on an API request, it must be exactly the matching `http://localhost:8765` or `http://127.0.0.1:8765` origin for its Host. Missing Origin is deliberately allowed only with the valid per-process token; `Sec-Fetch-Site: cross-site`, duplicate or unsupported metadata is rejected. No CORS allow-origin headers are emitted; OPTIONS is not enabled for cross-origin access.
- **Response headers:** responses include `Cache-Control: no-store`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, and a CSP. The CSP allows same-origin scripts, the existing Google font origins, inline styles needed by the UI, data/blob images and blob audio; it blocks framing and other script sources.
- **Body parsing:** JSON must be a single UTF-8 `application/json` body, top-level object, with duplicate JSON keys rejected. Repeated/malformed Content-Length, unsupported transfer/content encodings, unsupported Content-Type, invalid UTF-8/JSON and oversized bodies are rejected with controlled 4xx responses before a body is read where possible. Rejected unread bodies close the connection.
- **Read deadlines:** each request-header read has a 15-second inactivity timeout; POST body transfer has a 60-second overall deadline. GET bodies and transfer-encoded requests are rejected. A slow-drip header that continually sends bytes within the timeout can still occupy a thread; request-rate/global thread caps are not implemented.
- **Limits:** ordinary JSON routes are limited to **1 MiB**; `/api/ask` allows **20 MiB** for inline images, while a decoded raster image is limited to **12 MiB**, its parsed container/header must match PNG/JPEG/WebP, each side is capped at 8,192 pixels and total dimensions at 12 megapixels; `/api/stt` allows **25 MiB**, only WebM/Ogg/WAV/MP4 content types, and checks container signatures before invoking STT. These are bounded header/signature checks, not full image/audio decoding, codec validation or proof of a valid audio track. `/api/tts` text is capped at **2,000 characters**. Chat text is capped at 16,000 characters; search/note query at 200 characters. Profile and project fields have per-field bounds described in `API_DESIGN.md`.
- **Path/input validation:** project IDs use a bounded lowercase identifier format. Profile, brain-file and skill components reject path separators, Windows special/alternate-stream characters, trailing dot/space and reserved device names; Markdown paths are resolved under their intended roots and symlink escapes are rejected. Session paths are confined under the application root. Restore accepts only generated backup basenames. Project fields, arrays, colors, actions, links and modes are type/length checked; project colors must be six-digit hex.
- **Error behavior:** malformed requests get controlled 4xx JSON responses; unexpected handler exceptions return a generic 500 response. New handler diagnostics record method and exception type only, not request bodies, headers, tokens or exception text. STT/TTS/vision and model/provider API failures return generic messages rather than raw implementation errors. Some pre-existing routine/provider logs may still contain provider error text and should be audited separately.
- **Frontend:** all API fetches carry the injected token, including direct audio/TTS fetches. Project labels, IDs, icons, paths, link strings, provider labels and file names are escaped or rendered through `textContent`/DOM properties. Colors use a strict hex allowlist; project link opening permits only parsed HTTP(S). Image previews accept only bounded PNG/JPEG/WebP data URLs. Saved window geometry is numeric and bounded before CSS use.

## Current protections and remaining gaps

- Loopback binding, `.gitignore` rules, Host validation, token authorization and Origin checks are useful defense-in-depth, not encryption or a complete local security boundary.
- `.env.example` has empty placeholders. This implementation did not inspect or change `.env`, runtime data or backups.
- The per-process token is available to any script executing same-origin JavaScript and can be copied by a local user/process. There is no user identity, Windows DPAPI/Credential Manager integration, TLS, per-operation permission policy, approval center, append-only audit log or general sandbox.
- Threading remains unbounded and there is no request-rate limit or per-route concurrency quota. A slow-drip header can hold a thread despite the inactivity timeout. Size limits and overall body deadline do not prevent all local resource exhaustion.
- Search/state responses intentionally expose local project/vault data to authorized callers. Review that trust boundary before adding new clients.
- Project `path` is treated as display/configuration metadata and is not used as an authorization grant. Future filesystem tools must use a separate allowlist and sandbox.
- Inline styles remain permitted by CSP for compatibility; the Google Fonts dependency remains external. Revisit these if the UI is made fully offline.
- Prompt files contain safety instructions, but the project windows do not execute actions. Prompt instructions are not an enforcement mechanism for future tools.
- `search_notes()` searches `data/` and other content roots; review data scope and ensure returned paths/snippets do not expose secrets.
- Backup/restore is partial and not encrypted. Avoid treating it as complete disaster recovery.

## Manual verification status

No tests, services, browser requests or application routes were executed during implementation. Use the Phase 1A security section in `docs/TEST_CHECKLIST.md` to verify allowed local URLs, token handling, Origin/Host rejection, body limits, malformed inputs, safe project rendering and voice upload manually. Do not copy the token into reports or screenshots.

## Credential protection

1. Never embed keys/tokens/passwords in source, repository JSON, Markdown, prompt context, test fixtures, output, or command logs.
2. Use Windows Credential Manager/DPAPI through a maintained, reviewed interface; avoid inventing encryption. Document key rotation/revocation.
3. Redact secrets before logging exceptions, HTTP headers, provider bodies, and browser/session errors. Do not log full prompts, personal messages, cookies, or audio by default.
4. Keep `.env` untracked as a temporary compatibility option only; validate ignore behavior and avoid secrets in `.env.example`.
5. Do not include private account/project details in public docs, test reports, screenshots or backups without explicit need.

## File access and agent isolation

- Begin with an explicit read-only root allowlist; canonicalize resolved paths and block traversal, junction/symlink escapes and alternate path forms.
- All file actions go through one capability-checking service; agents get no raw shell or arbitrary process execution by default.
- A project prompt window is not a sandbox. Future agents need separate workspaces, per-agent permissions, bounded tools, dedicated logs and memory, and OS-level least privilege where feasible.
- Prefer patch/diff preview, bounded file sizes, atomic writes, safe backups and rollback. Deletes, overwrites and bulk operations require confirmation.
- Never trust untrusted web/email/chat instructions to change permissions or override system policy.

## Approvals and audit

Each consequential action should present actor, operation, exact target, data to be sent, integration/provider, permission level, side effects, expiration and an explicit approve/deny control. Approval must be bound to the exact action and expire; changing its target invalidates approval. Keep append-only, access-controlled audit metadata: timestamp, actor, action ID, target identifier, approval, result, and redacted error. Avoid payload retention unless specifically required and consented to.

## Network and provider policy

- Local mode should enforce an allowlist of loopback endpoints and fail closed if a provider is unavailable; never silently use cloud.
- Online mode must be visibly selected and disclose the provider and data transfer before a request. Provide cancellation and cost/status labels with honest unknowns.
- Validate schemes, hosts, redirects, DNS/IP resolution and request size to prevent localhost or private-network request abuse through arbitrary URL configuration.
- Prefer official APIs; rate-limit; respect terms. Stop on CAPTCHA, account checkpoint, bot block or unclear authorization.
- Google-hosted fonts in the current HTML are an external dependency, even if no user prompt is sent.

## Emergency stop and self-healing

Define emergency stop precisely: stop accepting new tasks, signal cancellable model/network/process operations, stop schedulers, preserve safe logs, and require explicit restart. Never kill unrelated processes. The current `stop.flag` is only a flag and does not interrupt work. Future watchdogs need bounded retry/backoff, per-service restart caps, no restart loops, and escalation rather than endless retries.

## Privacy and retention

Keep user data local by default; separate configuration, credentials, conversation/session data, project files and telemetry. Define retention and deletion/export behavior before collecting more data. Bound histories/logs, back up only with clear scope, encrypt sensitive backups, and keep the Markdown vault user-readable and preserved. Do not email or sync private data by default.

## Required security gate before tools/integrations

Threat model; safe API origin/token design; secret-store prototype; path sandbox tests; action/approval policy; redacted audit; cancellation; rate/size limits; backup/restore recovery test; and manual browser/account checks approved by Cyrus. See roadmap Phases 1 and 6-7.
