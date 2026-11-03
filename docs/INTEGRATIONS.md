# Integration plan

**Audit date:** 2026-11-04. Status refers to repository implementation, not live service availability. No accounts were accessed and no integration was tested.

## Owner-confirmed priority order

Target sequence is **Gmail → Google Calendar → Google Drive → GitHub → Notion**, followed by additional services only after API, scope, privacy, security and maintenance review. This is a roadmap priority, not an installed or authorized service list. Gmail begins with read/search/summarize and draft capabilities; sending requires an approval screen with recipient, subject, complete message and attachments. Do not expose send as available before backend permission enforcement and audit are in place.

## Required adapter contract

Each integration should define: stable ID/display name/category; adapter boundary; validated config schema; auth mechanism and scopes; capabilities; required permission level; health check; connect/disconnect/revoke lifecycle; timeout/retry/rate-limit policy; typed errors; redacted audit events; and mockable tests. Secrets belong in Windows Credential Manager/DPAPI-backed storage (or a reviewed keyring implementation), never source, config JSON, logs, prompts, reports, or Git. Approval is evaluated by the central policy layer, not by an agent prompt.

## Inventory

| Integration | Current status | Proposed path and auth | Capabilities/approval | Risk and questions |
|---|---|---|---|---|
| Ollama | **Implemented, unverified live** in `router.py`; vision calls hard-code localhost separately. | Local HTTP adapter; configurable base URL; no account auth assumed. | Local inference / vision; Observe/Prepare initially. | Validate host allowlist, timeouts, model existence, model lifecycle and GPU memory; do not call arbitrary configured URLs without policy. |
| OpenRouter | **Implemented, unverified live**; `.env` key read by `router.py`; model list public fetch in `scout.py`. | Official API and scoped key in OS secret store; explicit Online mode. | Cloud chat and model metadata; disclose external data transfer and provider billing/pricing. | “Free” is not guaranteed by `$0`; model pricing/rate limits vary; require provider/model identity and cost provenance. |
| Groq | **Implemented, unverified live**; `.env` key; used for routines/cloud fallback. | Official API/key, explicit Online policy. | Chat/routine inference; prompt contents leave device. | Cloud call from routine path can happen when mode is cloud; clarify policy and prevent silent fallback if desired. |
| Cursor | **Not implemented** | Investigate supported official CLI/API and user auth; do not scrape the desktop app. | Explicit online coding assistance only with visible disclosure. | Product/CLI availability, billing, workspace scope and streaming contract are unresolved. Do not assume CLI exists. |
| Gmail | **Not implemented** | Official Google OAuth API; minimum scopes. | Draft/read metadata first; send requires explicit approval. | PII, scope review, OAuth token encryption, account testing and draft-vs-send boundaries. |
| Google Drive | **Not implemented** | Official Google OAuth API, file-picker/scoped access. | List/read selected files first; modify/upload requires approval. | Avoid broad drive access; define per-file scope and retention. |
| Google Calendar | **Not implemented** | Official Google OAuth API, read-only first. | Read events; create/update/delete only with approval. | Sensitive schedule data, timezone and recurrence semantics. |
| Messenger | **Not implemented** | Evaluate official Meta APIs and eligibility first. Personal-account automation is not assumed supported. | Read/send only within an explicitly authorized thread if supported; every send approved. | Browser automation can trigger account restrictions and expose private messages. No CAPTCHA evasion, no reading unrelated threads. Human decision required before implementation. |
| Browser automation | **Not implemented** | Prefer official APIs; if a site allows automation, isolated persistent local browser profile with narrow origin allowlist. | Observe/prepare first; external submissions always approval-gated. | Session cookies are credentials; terms, rate limits, CAPTCHA/bot blocks mean stop. Browser is not a security sandbox. |
| Job platforms | **Not implemented**: LinkedIn, Indeed, Handshake, Wellfound, Glassdoor. | Prefer official API/authorized feeds; no assumed API. | Search/rank/draft/queue; never submit/message without explicit approval; truthful resume claims only. | Each site's API/access rules differ; scraping and automated application may violate terms. Stop at CAPTCHA/block. |
| Freelance platforms | **Not implemented**: Upwork, Fiverr, Toptal, PeoplePerHour, Contra, Guru, Freelancer.com, 99designs. | Per-platform API and terms review; authorized access only. | Research/draft proposals/tracker; proposals and client messages require approval. | Terms, fees, bids, financial and identity data. Never make purchases/pay fees. |
| Portfolio platforms | **Not implemented**: Dribbble, Behance. | Official APIs or user-approved manual workflow; verify API availability. | Draft/update portfolio; publication requires approval. | No assumption of API support or license for reused work/assets. |
| YouTube | **Not implemented** | Official YouTube Data API/OAuth if eligible. | Metadata/draft/video upload only after explicit approval; preserve source rights and ad disclosures. | Copyright/Content ID and channel policy; fair use is case-specific, not guaranteed. No claim that a short clip is automatically safe. |
| Desktop applications | **Not implemented** | Narrow OS-specific adapters with explicit executable/path allowlist. | Observe/prepare first; modifications/actions require approval. | Global mouse/keyboard/shell access has broad impact; avoid until threat model and isolation are implemented. |

## Local provider-mode contract

A future provider registry should make the selected mode authoritative for every route, including vision and routines. Local means network-denied except explicit loopback Ollama and required local components; no cloud fallback on failure. Online requires a deliberate UI/voice-confirmed switch, clear badge, provider/model, transfer notice and cost status. The current model router has a Local-only branch but a hybrid Cloud cascade; vision bypasses it and the scout has a public network fetch.

## Integration lifecycle proposal

1. Show integration purpose, data requested, provider, permissions, retention and disconnect behavior.
2. Authorize with official OAuth/API mechanisms; request only minimum scopes and store tokens via OS secret storage.
3. Test health with non-sensitive calls; report “configured” separately from “healthy”.
4. Route each operation through capability policy, rate limiting, timeouts and user approval.
5. Redact logs, store action/audit metadata without payloads or credentials, and surface failures.
6. Disconnect by revoking token where supported and deleting local secret/session state after confirmation.

## Gmail milestone gates

1. Document official OAuth/API feasibility and the least-privilege scope for each read, label, draft and send operation.
2. Implement Windows-appropriate secret storage, token revocation/disconnect, health state and redacted audit before account authorization.
3. Begin with read/search/summarize and draft only; do not make real account calls during development without Cyrus's explicit instruction.
4. Before sending, bind approval to the exact recipient, subject, body and attachment set; display all of them and reject execution if any value changes after approval.
5. Test using mocks/fixtures first. Live account testing is a separate opt-in step and remains unapproved until Cyrus authorizes it.

## Unresolved design decisions

- Which integrations are actually desired first, and which are not worth the privacy/maintenance cost?
- What data may leave device in Online mode, and is prompt redaction required?
- Is Messenger strictly prohibited unless a supported official API becomes available?
- What qualifies as pre-approved recurring behavior, and how are grants scoped/expired/revoked?
- Which OS secret-store package is supportable on Cyrus's Windows environment?
- Can the UI show current provider, region, model, usage and approval evidence before every external action?
