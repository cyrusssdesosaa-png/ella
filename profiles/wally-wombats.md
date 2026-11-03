# Wally Wombats (Don and David)

## What it is

Client work for David Gilbert. Rebuild of wallywombats.com for the North Rainbow, Henderson, and Bullhead City locations, on the existing SmarterASP.net account. A public site, an admin site, a rehab-directives draft, and a MoreMe monitor agent used for the job.

Cyrus is the builder. John was the design contact. David is the client. Bullhead City opening was the launch reason in the October 2026 plan.

## Paths

| Piece | Path |
| --- | --- |
| Planning workspace | `D:\don and david projects` |
| Public site | `D:\final website` |
| Admin site | `D:\final admin website` |
| Rehab directives draft | `D:\don and david projects\rehab-directives-draft` |
| Older desktop copies | `C:\Users\USER\Desktop\wallywombats`, `wallywombats_v3`, `wally wombats automatic emaill` |
| MoreMe agent (installed app) | `C:\Users\USER\AppData\Local\Programs\moreme-monitor-agent` |

Read first, in this order:

1. `00-intake/project-brief-from-chat.md`
2. `00-intake/meeting-summary-2026-09-28.md`
3. `03-plan/plan-v2.md`
4. `03-plan/feature-matrix.md`
5. `02-research/smarterasp/smarterasp-notes.md`

`00-intake/credentials.local.txt` and `appsettings.Production.json` hold secrets. Never quote them, never commit them.

## Stack

- Public site and admin are ASP.NET. Admin project file is `WallyWombatsAdmin.csproj`, target `net8.0`, Entity Framework Core SQL Server, out-of-process hosting for SmarterASP.
- Rehab draft is a static site (`index.html`, `css`, `photos`) with a Wrangler config, so it can sit on Cloudflare.
- Host playbook for the main site is SmarterASP.net (deploy, database, errors), documented under `02-research/smarterasp/`.
- Inquiry mail target named in the public README is support@wallywombats.com. The mailbox password stays in production settings only.

## What was built

The October plan folder is a full job system: intake, recordings index, research, plan v2, feature matrix, deliverables, code, assets, and an Oct 6 test folder.

Recordings were not copied into the repo because they are huge. Meeting video was `C:\Users\USER\Videos\Screen Recordings\Screen Recording 2026-09-28 122839.mp4`. Chat video was `Screen Recording 2026-10-03 235050.mp4`. Transcripts and chat frames live in `01-recordings/transcripts/`. Use those, not the raw videos, unless he asks.

Plan dates that were written down: Oct 6 preview on the UAT sub-site, Oct 10 live for the Bullhead opening. The README checklist still had open items on 2026-10-04 (SmarterASP login, .NET scaffold, John assets, first UAT deploy). Later folders `D:\final website` and `D:\final admin website` show the sites moved forward after that checklist. Read `plan-v2.md` and the site projects before telling him a step is still undone.

Rehab directives draft was still being edited on 2026-11-02.

MoreMe Monitor Agent is a Desktop shortcut to an installed Electron app. Chats about it were account setup and undoing changes. Treat it as a client ops tool. Do not rebuild it from scratch unless he asks.

## How Cyrus works on it

He sends Teams chat frames, meeting frames, and website screenshots. Those images are the source of truth for what David said and what the page should look like. Write findings into `00-intake` or `01-recordings/transcripts` when he wants them saved. Match the existing site's jobs: parties, passes, locations, birthday packages, inquiry mail.

He works this around a night schedule. Do not invent a deploy to production. UAT first, then the go-live runbook in `04-deliverables`.

## Pictures

A crop of the live site or of David's chat means: read the visible text, list what is wrong or what he asked, then change the matching page. If a number, date, or price is unreadable, say so. Do not guess a price.

## Do not

- Commit credentials or paste the mailbox password into chat.
- Email David or John unless Cyrus asked for a draft he can send himself.
- Overwrite `wallywombats-original` or the Desktop v3 archive. Those are backups.
