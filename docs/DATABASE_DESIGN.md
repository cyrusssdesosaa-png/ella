# Storage and database design

**No storage migration is approved.** This document describes the current implementation and a staged proposal; JSON files and the Markdown vault remain authoritative until a separate reviewed migration plan exists.

## Current storage inventory

| Data | Current location/format | Lifecycle and limitations |
|---|---|---|
| User profile | `data/profile.json` | Created with defaults on first server start; editable through profile route. |
| Short facts | `data/memory.json` | JSON array; profile-save path retains most recent 30 facts. Not source-linked or searchable by semantics. |
| Provider/mode/model | `data/brain.json` | Runtime Local/Cloud and model selection; fresh default is `llama3.2:3b`. |
| Main chat history | Process memory in `routines.py` | Last 10 turns; lost when server restarts; shared process-global context. |
| Project chat sessions | `data/sessions/project-<id>.json` | Up to 100 messages saved by project route; currently not fed back into model context. |
| Usage | `data/usage.json` | 80 recent calls and cumulative prompt/completion/call counters; no daily/session/cost/context-capacity ledger. |
| Quota | `data/quota.json` | Latest provider-reported remaining field if available. |
| Activity | `data/activity.json` | 80 latest activity entries. Concurrent updates can race. |
| Check-in/missed check-in | `data/checkin.json`, `data/missed.json` | JSON caches/guard values; date currently uses host-local time. |
| Outbox | `data/outbox.json` | Bounded retry records for failed routines/model calls. |
| Backups | `data/backups/*.zip` | Fixed allowlist from `server.py`; partial backup only and not encrypted by application. |
| Logs | `data/jarvis.log` | Append-only text with no rotation/size cap. |
| Skill snapshots | `data/skill-history/` | Keeps recent snapshots for one skill path. |
| Projects | `bots/projects.json` | Tracked configuration with prompts, links, actions and local paths; may contain personal context. |
| Knowledge vault | `vault/**/*.md` | Human-readable Markdown, project notes, daily logs and index. Not a database; preserve attribution in `vault/NOTICE.md`. |

`store.py` uses JSON and `os.replace` with a predictable `.tmp` path. Atomic replacement reduces partial writes but does not make concurrent read-modify-write sequences safe or multi-file updates transactional. `data/` is Git-ignored and was absent in this checkout. No SQLite/vector database, migration mechanism or encryption abstraction exists.

## Proposed future design (subject to approval)

Use SQLite for structured, transactional, queryable runtime entities, while retaining Markdown as the human-readable knowledge source and approved project files as their own source of truth. Suggested initial entities:

- `schema_migrations(version, applied_at)`
- `conversations(id, scope, project_id, created_at, updated_at, retention_policy)`
- `messages(id, conversation_id, role, content_ref_or_redacted_text, provider, model, created_at, token_metadata_json)`
- `projects(id, display_name, config_ref, created_at, updated_at)`
- `tasks(id, project_id, state, priority, scheduled_at, dependencies_json, cancellation_state, created_at, updated_at)`
- `events(id, timestamp, type, actor, project_id, task_id, redacted_payload_json)`
- `approvals(id, action_hash, actor, target, scope, expires_at, decision, decided_at)`
- `usage_calls(id, timestamp, provider, model, mode, prompt_tokens, completion_tokens, cached_tokens, duration_ms, ttft_ms, tps, cost_amount, cost_currency, cost_source)`
- `integrations(id, type, config_json_without_secrets, state, last_health_at)`

Avoid storing credentials in SQLite. Avoid duplicating entire vault content without source references and retention controls. Add FTS for explicit text search only after privacy/retention design; vector retrieval is a separate optional decision, not a prerequisite.

## Migration and recovery requirements

1. Inventory data files on Cyrus's actual machine and ask what must be preserved; do not infer from a clean clone.
2. Define stable IDs, schema and migration versioning; migration must be idempotent and leave originals untouched until verified.
3. Make an encrypted, dated backup with explicit inclusion/exclusion manifest; test restore to a separate location first.
4. Provide export to readable JSON/Markdown and a rollback path.
5. Add per-user data directory configuration, file permissions, size/retention policy and corruption recovery.
6. Migrate one entity at a time; dual-read/write only for a bounded, documented transition.
7. Validate counts and selected content without printing sensitive values; require Cyrus's acceptance before deleting legacy data.

## Open decisions

- Is `data/` intentionally repository-relative or should it use Windows user application-data storage?
- Which runtime state needs durable chat/session persistence and what retention period is desired?
- What exactly should a backup contain, and should the vault be included or separately backed up?
- Should usage events survive provider failures and include estimated versus actual pricing provenance?
- Is SQLite sufficient for expected single-user concurrency, and is any vector store justified by measured search needs?
