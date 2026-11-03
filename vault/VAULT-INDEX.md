---
status: active
project: meta
type: index
---

# VAULT INDEX

Read this at the start of a session. It has two jobs: who Cyrus is, and the map of this vault. Identity lives in `CLAUDE.md`.

Adapted from the AI Memory Vault index by Jared Rhodenizer, CC BY-SA 4.0. https://github.com/jaredrhod/ai-memory-vault

## Vault location

`C:\Users\USER\fckkk\cy projects\vault`

These are plain markdown files. Obsidian can open this folder if he wants a visual view. The side panel and Jarvis read the files either way.

## Who I Am

I'm Cyrus Wendell P. De Sosa. I study computer engineering and I work in Cursor on Windows. I live on Asia/Manila time. Night chatter is 10pm to 6am. Daytime work is school, Unity, and the Wally Wombats client job. Jarvis is the local daily assistant. GOD at `D:\GOD` stays its own app.

## Jarvis

The side panel is `http://127.0.0.1:8765`. Check-in defaults to 09:00. Chat wants an OpenRouter key. Routines want Groq, then Ollama. Keys live only in `.env`.

- **Status:** Active

## Aura (`D:\capstone`)

AR campus navigation. Unity `6000.3.11f1`. Scene `finalapp 2`. Floorplan scale stays 280. No second Unity instance if the Editor already has the project.

- **Status:** Active

## GOD (`D:\GOD`)

Local desktop AI. Do not delete it or merge Story Studio into Jarvis.

- **Status:** Active

## Wally Wombats

Client rebuild for David Gilbert. Employment there ended May 2026, so "currently employed" is no. Do not print `credentials.local.txt` or `appsettings.Production.json`.

- **Status:** Active

## Desk tools

Translator on `127.0.0.1:8787` via `open.bat`. Read Aloud is browser speech.

- **Status:** Active

## Vault structure

```
00 - Inbox           capture, sort later
01 - Daily Notes     one file per day
02 - Jarvis          the side panel and how it runs
03 - Aura            capstone notes
04 - GOD             the other local AI
05 - Wally           client job notes
06 - Desk            translator and read aloud
07 - Night Shift     pointer only, no stored replies
08 - Personal        life outside the projects
09 - Archive         finished notes
10 - Resources       jobs and cross-project reference
```

## What's active right now

Open work is in [[Active Priorities]]. Check the real file before acting on a listed item.

## Daily routine

- Check-in at 09:00 Manila.
- Night shift is 10pm to 6am.
- Big files go on `D:\`. This vault stays on `C:`.

## What I want

A daily assistant that remembers the work, uses the skill the step needs, and does not burn the free-model cap on routines.

## How I work with AI

- Plain language. Lead with the result.
- "more" expands the current piece. "nice" means keep going.
- A screenshot is the spec.
- Do not park a known flaw under "later" without saying why.
- Argue once when something does not add up, then follow the decision.
- Do not propose extra access. He widens access when he wants it.
- Most guidance is a guideline. Locked rules are listed in `CLAUDE.md`.

## How memory works

Hold the current step. The rest of the vault is one note away. Start here, then open the folder index, then the note. `data/memory.json` keeps the newest 30 short facts. A fact that should survive also gets a home in the vault.

## Vault rules

Every note has YAML frontmatter: `status`, `project`, `type`. Code files do not.

`status`: `active`, `completed`, `parked`, `idea`, `archived`.

`project`: `jarvis`, `aura`, `god`, `wally`, `desk`, `night-shift`, `personal`, `meta`.

`type`: `index`, `reference`, `guide`, `plan`, `log`.

Update a folder index in the same pass as a new, renamed, or moved note. Do not archive a note unless Cyrus asks.

Daily notes live in `01 - Daily Notes/NN - Month YYYY/YYYY-MM-DD.md`. Create them from `Daily Note Template.md`. If today already exists, append `## Session N`. Use Manila time.

Do not use an em dash in notes or in copy drafted for him.

Who I Am, the project sections, preferences, and these rules change only when Cyrus changes them, or when a folder is really created or removed. A passing comment is not a profile update.
