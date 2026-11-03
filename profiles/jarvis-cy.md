# Jarvis in cy projects

## What it is

The AI Cyrus asked for on 2026-11-03: his own daily assistant, Grok-like chat, able to code, with skills, memory, and routines. Not Claude Code, because that needs a paid plan. Not a fork of a GitHub Jarvis repo.

The chat app is built. It is Ella, the side panel. The written map of what is on screen is `vault/02 - Jarvis/panel.md`.

## Path

`C:\Users\USER\fckkk\cy projects`

Plan notes from that design chat (not built yet):

- Dark Grok-style window. Chats on the left, thread in the center, one main assistant.
- Free cloud models first (Groq for daily use, OpenRouter for a monthly list of official free models). Local Ollama only as backup.
- Keys come from his own accounts, pasted into `.env`. No search for leaked keys.
- Starts when Windows logs in. A short profile plus the newest 30 facts. Check-in at a time he sets. Timezone Asia/Manila.
- Each extra bot gets its own folder and may only edit that folder.
- Skills are text files. Each message loads the one skill that fits.
- He wants the assistant to adapt when he corrects it, and he wants to undo a bad change.
- Messenger reach and a coder that calls tools were pushed to later, after chat works.
- Coding tools stay off until a free model that actually calls tools is connected.

GOD at `D:\GOD` is the earlier, already built desktop AI. Jarvis here is the free, skill-based daily app. Do not delete GOD to "replace" it. Do not pretend Jarvis is already installed.

## What exists now

- `README.md` explains this pack
- `profiles/` is the project memory
- `skills/` is the skill library
- `vault/` is the long memory, with `VAULT-INDEX.md` as the map
- `CLAUDE.md` is the boot file
- `server.py` and `web/` are the side panel
- `.cursor/skills/` lets Cursor load those skills while this folder is open

## How to continue the build

When he says to build Jarvis, start here. Do not reopen the model debate unless a free endpoint is dead. Scaffold a local Python server, a data folder for chats, and the window. Point the assistant at `profiles/INDEX.md` and `skills/`.

## Pictures

He will send shots of Grok, Cursor, and other assistants as the look he wants. Copy the layout idea (sidebar, thread, composer). Do not copy their logos, trademarks, or proprietary assets.

## Status

Ella is running as the side panel, updated 2026-11-04. Panel: `http://127.0.0.1:8765`. What it has: `vault/02 - Jarvis/panel.md`. Boot file: `CLAUDE.md`. Map: `vault/VAULT-INDEX.md`. Default brain is local `qwen2.5:7b`. Project windows are in `bots/projects.json`.

## Do not

- Install Claude Code as the engine.
- Hunt GitHub for API keys.
- Load every skill into one prompt.
