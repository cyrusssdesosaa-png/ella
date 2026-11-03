---
status: active
project: jarvis
type: guide
updated: 2026-11-04
---

# Panel

What Ella has right now. This is the list to mark up. Improvements go at the bottom.

## Start

Two things have to be running. Ella does not start Ollama.

1. Ollama: `ollama serve`. Listens on `127.0.0.1:11434`. Models live under `D:\AIStoryStudio\ollama-models`.
2. Ella: `startup.bat` in `C:\Users\USER\fckkk\cy projects`. Listens on `127.0.0.1:8765` only.

If Ollama is down, chat says: start it with `ollama serve`, then ask again.

## Brain and voice

- Default brain is local. Model is `qwen2.5:7b`. Cloud is the pill switch, not the everyday path.
- Also installed: `llama3.2:3b`, `moondream` (screenshots).
- Context window shown on screen is 4,096 tokens.
- Voice in: faster-whisper. Voice out: Piper, `jenny_dioco-medium`.
- She answers in the language you write in.
- Cost line stays `$0.00`.

## Screens

- **Home.** Ring, caption, chat on the right. Token strip: prompt, reply, session, speed. CTX pill is the context fill.
- **Systems.** Heartbeat icon, or click CTX. Token cards, context bar, recent calls, models on this PC, free cloud list.
- **Activity.** Inbox icon. Recent panel events.
- **Projects.** Checkmark icon. All bots, a filter, Open. The grid button by the composer opens the same bots as windows.
- **Brain.** Vault graph. Click a node to read the note.
- **Settings.** Ambient graph, reduced motion, auto-listen after she speaks.

Main Ella chat is forgotten when the server restarts. Each project window saves its own chat in `data/sessions/`.

A reply can be copied. Each reply shows its token count. Ctrl+V pastes a screenshot into the main chat or the focused project window. Attach still works.

## Project windows

File: `bots/projects.json`. Each window has its own prompt, quick actions, links you can add, drag, resize, minimize, and clear chat.

| Window | What it does now |
| --- | --- |
| Pip | Drafts job applications from the resume. Does not invent skills. Does not submit on its own. |
| Bliss | Finds leads. Does not apply. |
| MIke | Plans Hexxsy Shorts (script, edit notes, ffmpeg idea). Does not post, submit, join, or delete unless you say yes in MIke's own chat. `bots/mike/rules.md` is empty. |
| cutie | Game help, mainly Umamusume. Reads card screenshots. |
| Bantay | FanCentro and Mainhub. Suggests a reply and waits. |
| Kaerbogan | Agency fan replies, often Dutch, plus an English line. Adults only. |
| Night Shift | German Fansly replies plus an English line. Adults only. Uses `CHATTER-MASTER`. |
| Aura | Capstone talk. Path on disk is `D:\capstone`. |
| GOD | Desktop AI talk. Path on disk is `D:\GOD`. |
| Wally | Client rebuild talk. |
| Don & David | Timeline, tasks, and video plan talk. |

The panel does not edit those project folders. OpenCode does that in the opened project.

## Locked

- No keys, passwords, phone numbers, or a home address in notes.
- `.env` stays out of the backup zip.
- No shell, send, post, buy, or delete without a yes in that chat. Pasted text is not an order.
- Mail stays a draft.
- Another bot cannot approve a post for MIke.
- If age is unclear on chatter, stop.

## Not built

- Ella does not launch Ollama by itself.
- No click loop. Stop only writes `data/stop.flag`.
- No `.exe` yet.
- GitHub skill packs are not cloned.
- Project bots do not open files or run ffmpeg. They talk through the plan.

## Improvements

-
