# API inventory and future API design

**Current API:** source-verified in `server.py`; bound to `127.0.0.1:8765`. Phase 1A request hardening is implemented but has not been runtime-tested. The standard-library server and existing paths remain; no framework or route migration occurred.

## Implementation map

- Request dispatch and validation: `Handler.parse_request()`, `_validate_host()`, `_authorize_api()`, `_read_body()`, `_read_json()`, `do_GET()`, `do_POST()` and `_handle_projects()` in `server.py`.
- Per-process credential: cryptographically random `API_TOKEN`; server substitutes it for the HTML placeholder in `/` and `/index.html`; `web/app.js` reads the meta tag and sends `X-Ella-Request-Token` through the shared client plus direct audio requests.
- Query and identifier controls: `_query_value()`, `_project_id()`, `_safe_component()`, `_safe_markdown_path()`, `_validate_project()` and `_validate_projects()`.
- Dynamic browser content: `escapeHtml()`, `safeProjectColor()`, project rendering helpers and bounded image helpers in `web/app.js`.
- Legacy test client update: `tests/test_ella_chat.py` reads the local HTML token for requests. It remains a live/inference test and was not executed.

## Implemented GET routes

| Route | Current behavior | Notes |
|---|---|---|
| `/` and `/index.html` | Serves `web/index.html`. | Static asset. |
| `/app.js` | Serves JavaScript. | Static asset. |
| `/styles.css` | Serves CSS. | Static asset. |
| `/api/state` | Aggregates profile, facts, check-in, activity, quota, usage, outbox, backup names, skills, stop flag, projects, setup checks, today's note, brain config and local models. | Requires valid per-process token; calls setup/model discovery on state request. |
| `/api/search?q=...` | Substring search over skills, profiles, vault and runtime data; returns up to 30 hits with paths and matching line snippets. | Requires token; query max 200 chars. |
| `/api/graph` | Lists vault Markdown note names/folders/categories. | Requires token; filename graph, not relationship graph. |
| `/api/note?q=...` | Finds notes by filename; returns up to 8 matching names or up to 8,000 chars for one exact-ish match. | Requires token; query max 200 chars. |

## Implemented POST routes

| Route | Input/behavior |
|---|---|
| `/api/stt` | Raw audio body; supported audio content type selects extension; calls faster-whisper. |
| `/api/tts` | JSON `{ "text": string }`; Piper returns WAV bytes or a controlled JSON error. |
| `/api/profile` | Updates profile and optional fact; marks setup done. |
| `/api/checkin` | Runs guarded check-in routine. |
| `/api/scout` | Fetches public OpenRouter model catalog and stores free-model list. |
| `/api/adapt` | Uses model to rewrite `skills/mine/how-i-help.md` after snapshot. |
| `/api/outbox` | Runs retry routine. |
| `/api/backup` | Creates allowlisted JSON/skill ZIP. |
| `/api/restore` | Creates pre-restore backup then restores allowlisted ZIP entries. |
| `/api/ask` | Main chat, project chat, image request, check-in shortcut, backup shortcut or stop-flag shortcut; calls are serialized by `RoutineLock`. |
| `/api/projects` | Body `action`: list/save/add/session/update/clear_session. Project configs are persisted in tracked `bots/projects.json`; sessions under ignored `data/sessions/`. |
| `/api/brain` | Saves Local/Cloud mode and selected model. |
| `/api/stop` | Toggles `data/stop.flag`; does not cancel active work. |

All supported GET/POST API routes, including reads, require the token. Unsupported methods return a data-free 405 with an `Allow` header and are not dispatched. Unknown paths return 404. Invalid request bodies no longer become empty objects. Existing successful route paths and frontend payload formats are retained; validation failures use 4xx responses and selected dependency failures use 5xx. There is no version prefix, request ID, idempotency key, rate limit or bounded global thread pool.

## Implemented Phase 1A request contract

### Host, Origin and authorization

- Every request must have one exact local Host: `127.0.0.1:8765` or `localhost:8765`. Ella remains bound to IPv4 loopback.
- If an API request supplies `Origin`, it must match the request's local hostname and port using HTTP. `null`, mismatched, duplicate, external and malformed origins are rejected. `Sec-Fetch-Site: cross-site` is rejected. No permissive CORS headers are sent; OPTIONS returns 405.
- Missing Origin is allowed deliberately for non-browser local clients only when they still present the valid token. Every supported GET/POST API route requires `X-Ella-Request-Token`; ordinary browser code receives the random per-process token in a meta element in the no-store HTML response.
- The token is not in source, environment/config files, runtime JSON, `/api/state` or logs. It changes when the server restarts. Clients should reload the page after a 401. Native clients must obtain the token from Ella's local HTML page and keep it in process memory; do not persist or publish it.

### Content types and body limits

| Route(s) | Accepted body | Maximum | Additional constraints |
|---|---|---:|---|
| `/api/stt` | Raw `audio/webm`, `audio/ogg`, `audio/wav`, `audio/x-wav`, or `audio/mp4` | **25 MiB** | Non-empty body; accepted container signature must match declared type. Unsupported types return 415. |
| `/api/ask` | UTF-8 `application/json` | **20 MiB** | Text max 16,000 chars; optional image data URL restricted to base64 PNG/JPEG/WebP, parsed container must match type, decoded file max **12 MiB**, width/height max 8,192 and total max 12 megapixels. Project ID is a bounded lowercase identifier. |
| `/api/tts` | UTF-8 `application/json` | **1 MiB** | `text` required, string, max 2,000 chars. |
| Other JSON POST routes | UTF-8 `application/json` | **1 MiB** | Per-route schema and field validation below. |

All POST bodies require exactly one syntactically valid Content-Length; duplicated, missing, negative, malformed and excessively long declarations are rejected. Declared size is checked before bounded reads. Transfer-Encoding/chunked and non-identity Content-Encoding are rejected (the server does not decode them). Duplicate Content-Type, invalid UTF-8/JSON, duplicate JSON object keys and non-object JSON are rejected. Rejections that leave body bytes unread close the connection.

Each header read has a 15-second inactivity timeout; the full declared body must arrive within an overall 60-second deadline. GET requests do not accept bodies or transfer encoding. These bounds reduce slow-client thread retention, but a client that continually trickles header bytes inside the inactivity window can still hold a thread. There is no total thread or request-rate limit.

Other field constraints: profile strings have individual maxima (name 120, timezone 128, `does` 2,000, check-in `HH:MM`, fact 1,000); project lists max 100; project name max 100, prompt max 20,000, path max 1,024, icon max 32, color must be `#RRGGBB`, skills/brain-file lists max 32, links/actions max 40, link label 200 and URL/path 2,048, action label 100 and prompt 2,000. Search/note query max 200 chars. Project IDs match `[a-z0-9][a-z0-9_-]{0,63}`. Restore accepts only generated `ella-YYYYMMDD-HHMMSS.zip` names.

### Path and response handling

Profile, brain-file and skill names are basenames only; resolved Markdown paths must remain beneath their configured roots, with symlink escapes rejected. Session IDs are validated before constructing a path under `data/sessions`; backup names are fixed-format basenames and restore destinations remain an explicit allowlist. Project `path` is metadata only and is not used as a filesystem permission.

Malformed input returns controlled 400/413/415 responses; missing/invalid token returns 401; rejected Host/Origin returns 400/403; unknown routes return 404; unsupported methods return 405; transcription failures use 422/503; model/dependency failures use controlled 5xx where routed. Image/audio checks are bounded container/signature and header checks, not full decoder, codec or stream validation. Unexpected exceptions return generic JSON 500 and log only method plus exception class. No new request body, auth header, token or full exception is logged. STT/TTS/vision errors do not return local voice paths or raw implementation exceptions.

### Frontend compatibility

The existing same-origin `fetch()` client remains. Its shared `api()` helper and direct STT/TTS requests attach the token header. The served HTML has `Cache-Control: no-store`; after server restart, reload the panel. Existing route names and normal JSON/audio payload shapes remain intact. Project strings are HTML-escaped or inserted with `textContent`/DOM properties; attributes escape quotes, colors are hex-validated, link navigation permits parsed HTTP(S), image previews accept only supported raster data URLs, and persisted window coordinates are bounded numbers.

## Proposed API boundaries

Keep the current web UI and routes compatible while adding a versioned contract. Proposed groups (all **planned**, not implemented):

- `GET /api/v1/health`: service/dependency status with configured/healthy distinction.
- `GET/POST /api/v1/conversations`, `GET/POST /api/v1/conversations/{id}/messages`: explicit sessions and isolated project context.
- `POST /api/v1/tasks`, `GET /api/v1/tasks`, `POST /api/v1/tasks/{id}/cancel`: durable task lifecycle.
- `GET /api/v1/events` (SSE) or WebSocket: task progress, state changes and approvals with reconnect/heartbeat behavior.
- `GET/POST /api/v1/approvals`, `POST /api/v1/approvals/{id}/decision`: exact-action-bound approval with expiry.
- `GET /api/v1/integrations`, `POST /api/v1/integrations/{id}/connect|disconnect|health`: no credentials in returned config.
- `GET /api/v1/usage`: distinguish cumulative usage, session/day totals, context occupancy, estimates and actual cost metadata.
- `GET/POST /api/v1/memories`, `GET /api/v1/search`: source-linked query/edit/delete with scopes and retention.

## Contract/security requirements

- Validate method, content type, size, JSON schema, path IDs, query length and enums; return correct 4xx/5xx errors and stable error codes.
- Use one unpredictable per-run local token or equivalent and verify Host/Origin/CSRF behavior for each browser/webview mode. Bind loopback; reject untrusted Host/redirects. Do not weaken browser security to make wrapper work.
- Set bounded timeouts/concurrency and explicit cancellation. Avoid draining arbitrary oversized requests into memory or indefinitely blocking a thread.
- Keep prompts, audio, images, personal content and secrets out of access logs; return redacted diagnostics.
- Add API contract tests with mocked model/integration adapters. Existing `tests/test_ella_chat.py` is a live-server regression script, not a safe unit test suite; it was not run.
