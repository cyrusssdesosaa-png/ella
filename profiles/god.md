# GOD

## What it is

Generic Omniscient Digital Intelligence. A local-first personal AI for this Windows PC. It is the finished desktop app. Jarvis in `cy projects` is the later free-model idea and is a different folder.

## Path

`D:\GOD`

Desktop shortcut **GOD** opens `D:\GOD\desktop-shell\release\GOD.exe` with working directory `D:\GOD`.

An older shortcut named **JARVIS** points at `D:\god\GOD.exe` and `app\window.py`. On Windows that is the same `D:\GOD` folder. `app\window.py` was not present when this profile was written. Use the desktop-shell exe, not the old window script.

Empty folder `D:\JAVIS` is not the app. Do not put new work there.

## Stack

Python 3.11+, pip package in this folder, pytest. Electron desktop shell (Node). Optional Ollama models `llama3.2:3b` and `moondream`. Optional FFmpeg and NVIDIA. Local API was `127.0.0.1:8787` during development. The product UI is the desktop window, not the browser on that port.

SQLite for chat sessions. Vision, voice, tools, memory, model routing, MCP center, a Unity bridge, and a Story Studio bridge.

## What was built

Versions in `CHANGELOG.md` run up through 1.31.0. The README status line is **GOD v1.31**: action tasks run and verify without the user having to say "continue".

Pieces that matter:

- Chat sessions persist, can be renamed, searched, deleted, and exported to markdown.
- Large prompts become a multi-step plan. The agent loop is inspect, act, verify.
- JARVIS-style HUD: frameless window, dashboard gauges, tasks, model, voice, memory, tools.
- Vision API: screenshot, describe-screen, analyze, upload. Sidebar can capture the screen or take an image path plus a prompt. This matches how Cyrus works. A picture is input, not a side note.
- System monitor reads real CPU, disk, network, and GPU temperature.
- Unity MCP can be enabled with `GOD_ENABLE_UNITY_MCP=true` and a bridge on port 8080. It stays disabled in the HUD until Unity is actually running.
- Story Studio is not inside this repo. GOD talks to `D:\AIStoryStudio` through `studio.bridge`.
- Tray, autostart, watchdog, notifications, backup and restore, update check. Docs for each are under `docs/`.

Install for daily use:

```powershell
cd D:\GOD
.\install.ps1 -Desktop
```

Dev launch is `.\start.ps1` plus `npm start` inside `desktop-shell`. Health check: `python -m scripts.health_check`.

## Important files

- `README.md`, `CHANGELOG.md`, `ARCHITECTURE.md`, `pyproject.toml`, `requirements.txt`
- `docs/RELEASE.md`, `docs/UI.md`, `docs/AGENTS.md`, `docs/MEMORY.md`, `docs/UNITY_MCP.md`, `docs/TOOLS.md`
- `agents/` for agent behavior
- `desktop-shell/` for the window
- `.env` for local flags and keys. Never copy `.env` into a profile or a commit.

## How Cyrus works on it

He talks to it like an operator: "status", "inspect this project", "fix this", "build this". He wants it to adopt and finish the job. Earlier names for the same effort were Hardwire and Jarvis. Hardwire's folder is gone. GOD is the one that stayed on disk.

When he sends a picture while GOD is the subject, use the vision path if GOD is running. In Cursor, read the image yourself and then change GOD's code only if he asked for a code change.

## Status

Installed, shortcut on the Desktop, last changelog entry 1.31.0 (agent execution loop). Folder timestamps cluster on 2026-08-26. Treat later uncommitted edits as possible. Read `CHANGELOG.md` before adding a feature that already shipped.

## Known limits

- Free local models on an 8 GB VRAM budget need truncated tool results. Do not dump a whole repo into one prompt.
- Unity connection fails when the Editor is closed. Say that plainly.
- Do not point him back at the browser UI as the product.

## Do not

- Rebuild Phase 0. It already exists.
- Merge AI Story Studio into this git repo.
- Store models or media caches on `C:`.
