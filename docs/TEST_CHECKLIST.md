# Manual test checklist

Prepared 2026-11-04. **This live checklist has not been executed.** Ella/Ollama were not started for it, and no model prompt or integration request was sent. A later offline Phase 2 unit test (`tests/test_phase2_offline.py`) does not replace these checks.

## Before testing

- [ ] Review `git status` and the complete diff; distinguish Phase 1A changes from preserved, previously uncommitted README, audit report and takeover documentation.
- [ ] Confirm intended Python environment and installed dependency versions without exposing credentials.
- [ ] Check whether local runtime `data/`, `.env`, model weights, and Piper voice files exist; do not print their secret contents.
- [ ] Confirm Ollama model inventory, free VRAM and desired Local/Cloud mode. Do not infer the active model from historical docs.
- [ ] Back up runtime data to a private, approved location before any persistence/restore test.

## Browser panel baseline

- [ ] Start Ollama manually only if intentionally testing local inference; confirm expected model is available.
- [ ] Start Ella using the intended script and verify it binds only to `127.0.0.1:8765`.
- [ ] Open the panel; check ring, chat, navigation, console errors, layout and reduced-motion behavior.
- [ ] Confirm startup failure is visible and stop the process normally; verify no repeated restart loop on intentional failure.

## Local chat, provider mode and token UI

- [ ] In Local mode, send a harmless prompt and verify the selected Ollama model/provider; temporarily block/disable cloud keys if validating no-cloud behavior.
- [ ] With Ollama unavailable, verify Local mode returns a clear error and makes no cloud call.
- [ ] Review Cloud-mode behavior and explicitly note whether fallback to Ollama is acceptable; avoid prompts containing private data.
- [ ] Confirm provider/model labels reflect actual response source.
- [ ] Verify prompt/completion values, context/cumulative distinction, and that displayed `$0` is not represented as a proven cost.
- [ ] Check main history retention across server restart and decide expected behavior.

## Project contexts

- [ ] Use harmless distinct marker phrases in main chat and two project windows.
- [ ] Verify each project uses only explicitly allowed project history and does not receive main/other project markers.
- [ ] Restart server and verify project session save/clear behavior.
- [ ] Click Add Project and verify it responds; test invalid IDs/names and hostile HTML-looking labels in a disposable config.
- [ ] Confirm no personal project-path or prompt content is exposed in a shared screen recording.

## Voice and image paths

- [ ] Deny microphone permission and verify clear UI explanation.
- [ ] If authorized, capture a brief harmless English audio clip; verify bounded upload, transcript, chat response and cleanup of temporary file.
- [ ] Test empty/silent/unsupported/oversized audio handling; verify error appears and indicators match actual health.
- [ ] Test TTS with a short harmless phrase; verify WAV response, audio playback, stop behavior and surfaced missing-voice error.
- [ ] Test image analysis only with a non-sensitive image and confirm local model/provider, resource use and clear failure if model missing.

## API and security (use an isolated test profile)

- [ ] Validate malformed JSON, missing fields, wrong content type, huge declared body, slow body, invalid path IDs and unsupported methods return bounded 4xx errors.
- [ ] Verify unauthorized cross-origin web pages cannot read state or trigger mutation in supported browsers.
- [ ] Confirm no CORS wildcard, secret in response/log, or arbitrary outbound URL behavior.
- [ ] Verify stop/cancel precisely interrupts or clearly does not interrupt each supported work type.
- [ ] Do not probe production accounts or unrelated processes.

## Persistence, backup and recovery

- [ ] Exercise simultaneous harmless profile/activity writes in disposable runtime data; confirm no lost updates/corruption.
- [ ] Review backup manifest before creating archive; verify it contains only documented allowed data and excludes `.env`/secrets.
- [ ] Restore an archive only into a disposable test copy; verify malformed, oversized and path-traversal ZIP entries are rejected.
- [ ] Confirm recovery process and privacy/retention before relying on backups.

## Regression and hardware

- [ ] Inspect `tests/test_ella_chat.py` before deciding to run it: it contacts the live server, sends prompts, runs STT/TTS and mutates chat/check-in state. Run only with explicit authorization and disposable data.
- [ ] Measure one model at a time and record model, provider, prompt length, first-token/generation time, RAM and VRAM using trusted local tools.
- [ ] Confirm no unintended concurrent model load; repeat after image/voice paths.
- [ ] Check browser/UI idle resource use and verify timers/audio contexts clean up.

## Integration safety

- [ ] Do not log into accounts or send/post/submit/upload/buy during baseline testing.
- [ ] Use mocks for adapter contract tests. Any live integration requires separate approval, official API/terms review and a test account or safe draft-only scope.
- [ ] Stop immediately at CAPTCHA, checkpoint, platform block or unclear permission.

## Phase 1A security foundation (manual verification pending)

Perform these checks on Cyrus's PC after reviewing the diff. Keep Ella bound to loopback. Do not share the per-process token from DevTools or network captures.

### Normal access and frontend compatibility

- [ ] Open `http://127.0.0.1:8765` and, separately, `http://localhost:8765`; both should load the existing panel without a login screen.
- [ ] Verify chat, navigation, project windows, model switch, brain graph, and audio controls still work as before.
- [ ] In DevTools Network, confirm legitimate `/api/*` calls include `X-Ella-Request-Token` and receive successful responses. Do not copy the header value into notes/screenshots.
- [ ] Restart Ella manually, then reload the page. A stale page token should fail with 401 and the refreshed page should work.
- [ ] Check the console for CSP violations, JS errors, failed assets and audio errors. The existing Google Fonts request is intentionally still allowed.

### Host, Origin and authorization

- [ ] Navigate to `/api/state` directly in a fresh tab without the token; expect JSON 401, not state data.
- [ ] From a separate origin (for example a local `file://` page), attempt a harmless API GET and a state-changing POST without a valid token. The browser may report a CORS/preflight rejection; verify no action occurs and no `Access-Control-Allow-Origin: *` header is returned.
- [ ] If using an HTTP inspection client, send an API request with a mismatched `Origin` and a dummy token; expect 403. Do not put the real token in shell history.
- [ ] Send a request using an unexpected `Host` hostname or port; expect 400 and no page/API data. Do not expose the service beyond loopback to conduct this check.
- [ ] Confirm missing `Origin` with no token is rejected. Missing Origin with a valid token is intentionally supported for local non-browser clients.
- [ ] Send OPTIONS/cross-origin preflight; expect 405 and no CORS allow-origin response.

### Body limits, schemas and errors

- [ ] With DevTools on Ella's page, send malformed JSON to a safe route using the current page token; expect 400 and no settings change.
- [ ] Send an ordinary JSON body larger than 1 MiB to a non-mutating validation attempt; expect 413 before route logic. Do not use `/api/ask` for this check because that route has a larger image allowance.
- [ ] Verify `/api/ask` accepts a normal text request and supported raster images, rejects SVG/unknown types, and rejects decoded images over 12 MiB. The full request limit is 20 MiB.
- [ ] Verify `/api/stt` accepts a normal browser recording and rejects an unsupported content type or body over 25 MiB.
- [ ] Try duplicate/malformed Content-Length, missing Content-Type, invalid UTF-8/JSON, duplicate JSON keys, and unsupported transfer/content encodings with an HTTP inspection client; expect controlled 4xx responses and a closed rejected connection where the body was unread.
- [ ] In an isolated local test, verify an incomplete request header receives a controlled timeout/connection close after about 15 seconds and a slow body exceeding the 60-second overall deadline is rejected/closed even if it sends occasional bytes; verify GET with a body or transfer encoding is rejected.
- [ ] Try a small file whose MIME label lies about its container, an image with excessive dimensions, and audio with a mismatched container; expect a controlled 4xx before inference/transcription.
- [ ] Try invalid project IDs (including separators/traversal), profile/brain/skill filenames with traversal, Windows alternate-stream characters or reserved device names, malformed colors, overlong fields and unknown project actions; expect 400/404 without file access or mutation.
- [ ] Trigger a controlled backend failure and confirm the response is generic JSON without stack traces, absolute paths, credentials, or request contents.

### Safe rendering and project behavior

- [ ] In a disposable copy of the repository, use an inert test project name such as `<img src=x onerror=alert(1)>`, plus quotes in the icon/link label. Confirm it displays as text and creates no image/script/event handler; then discard the disposable copy.
- [ ] In the same disposable copy, test colors outside `#RRGGBB`, `javascript:` links, and malformed project IDs. Confirm CSS falls back/rejects and only HTTP(S) links open in a new tab with opener isolation.
- [ ] Confirm real project names/icons/colors/links and existing project window layout still display correctly.
- [ ] Confirm image paste/attach previews work for PNG/JPEG/WebP up to 12 MiB and reject SVG/oversized files before sending.

### Audio and existing regression script

- [ ] Use the browser microphone once with a short recording; verify the tokenized `/api/stt` request, transcript, and existing chat flow. Do not test by sending personal audio.
- [ ] Verify TTS still returns/plays WAV and missing voice/model errors do not display a local absolute path.
- [ ] `tests/test_ella_chat.py` now fetches the token from Ella's local HTML, but it still contacts the live server, sends inference prompts, exercises STT/TTS and mutates check-in/chat state. Do not run it as part of this checklist unless Cyrus separately chooses to run it with disposable data.

## Phase 2 engines (not executed here)

Offline `python -m unittest tests.test_phase2_offline` does not start Ella or Ollama and does not replace the checks below.

- [ ] With Ella running from this branch, `GET /api/state` includes `phase2`. In Local mode, `phase2.context.allow_cloud` is false and `phase2.model_capabilities.vision_model` is `moondream:latest`.
- [ ] Flip the existing Local/Cloud control to Cloud and back. The context flag follows that switch. Local mode does not start a cloud request for an ordinary chat.
- [ ] `POST /api/tasks` with a normal request returns a completed local plan (observe + prepare) and no network send.
- [ ] `POST /api/tasks` with a step at level 4 returns `awaiting_approval`, leaves the task incomplete, and does not send, post, or spend.
- [ ] Restart Ella and `GET /api/tasks`. The same unfinished level-4 step is still unfinished.
- [ ] Backup contains `tasks.json` after a task exists. Restore of an older zip that has no `tasks.json` does not delete the current task file.
- [ ] Send an image. The vision call is still local `moondream:latest`. Cloud mode does not move that image to OpenRouter or Groq.
