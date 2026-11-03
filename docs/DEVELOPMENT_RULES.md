# Development rules

These rules apply to future changes to Ella and its user data. Preserve existing behavior/assets unless an approved change explicitly replaces them.

## Workflow

1. Verify repository root, branch, status, diff, and target files. Do not reset, clean, force-push, or overwrite backups.
2. Read current implementation and relevant docs/skills/profiles. Separate confirmed facts from assumptions.
3. State problem, proposed smallest change, affected files, dependencies, data impact, risk, rollback and manual acceptance criteria.
4. Avoid unrelated refactors and full-file rewrites. Preserve API/data compatibility where practical.
5. Make the focused change; review the resulting diff for secrets, unrelated edits and user data.
6. Update the source-of-truth documentation and changelog without rewriting historical memory to fit new conclusions.
7. Provide a manual test checklist. Cyrus performs manual acceptance. Do not run tests, start/stop Ella or Ollama, perform inference, use browser automation, or test integrations/accounts on the user's behalf.
8. Never commit, push, reset, checkout, or discard changes without Cyrus's explicit authorization. Do not install dependencies without direction.

## Python

- Keep modules focused and use type annotations for new public service boundaries.
- Use `pathlib`, explicit timeouts, bounded reads, structured errors, and validated configuration.
- Prefer dependency injection/adapters over direct network calls hidden in route handlers.
- Protect read-modify-write and multi-step state with appropriate locks/transactions; use unique temp files for atomic replacement.
- Avoid logging prompt bodies, secrets, audio, account data or full exception payloads. Bound and rotate logs.
- Use timezone-aware datetimes with configured timezone; test day boundaries and DST where applicable.
- Keep concurrency/model loading bounded and provide cancellation.
- Do not use prompt instructions as a substitute for authorization or sandbox enforcement.

## JavaScript and frontend

- Preserve the existing single `web/` frontend, ring, chat, voice, token strip, project windows and visual identity.
- Use DOM APIs/textContent for untrusted text; never interpolate config/user/provider values into `innerHTML` or CSS without strict validation.
- Handle pending/loading/error/cancelled states accessibly; distinguish configured from healthy.
- Respect reduced motion, keyboard navigation, focus management and responsive layouts.
- Avoid polling loops/DOM churn; clean up audio contexts, media tracks, listeners and timers.
- Keep external resources out of local-first paths; bundle licensed assets when appropriate.

## CSS/UI

- Use existing tokens/components first; maintain contrast and semantic states independent of color.
- Keep animations lightweight, bounded and disabled/reduced when requested or tab hidden.
- Do not introduce a second UI framework or replace current identity during foundation work.

## Documentation and personal data

- Cite implementation, not aspirations. Use labels such as Implemented, Partial, Planned, Unknown, and Not runtime-verified.
- Keep plans and current-state facts separate. Do not fabricate historical changes, tests or hardware/provider measurements.
- Never include secrets or unnecessary personal chat/project details. Preserve `vault/NOTICE.md` attribution and do not rewrite historical vault notes for convenience.

## Git, dependencies and configuration

- Review `.gitignore` before adding files. Never commit `.env`, tokens/cookies, private chat logs, runtime data, backups, model weights, voice files or generated media.
- Pin/add dependencies only when required; explain maintenance, license, platform and offline implications. Keep optional desktop dependencies separate from server requirements.
- Prefer documented env/config schema with safe defaults; validate provider URLs and paths. Keep secrets separate from ordinary config.
- Do not commit/push without Cyrus's explicit approval.

## Tests and verification

- Use isolated unit/contract tests with mocked providers for routine code; keep account/live integration tests opt-in.
- Identify whether a test starts a server, loads a model, calls a provider, changes persistent data or emits messages before running it.
- Do not claim test success, GPU use, offline behavior, or live integration status without direct evidence.
