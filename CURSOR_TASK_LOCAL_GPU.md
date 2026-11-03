# JARVIS: full job brief for Cursor Agent (deadline: lunchtime today, 2026-11-03)
Project: this folder (server.py on 127.0.0.1:8765, web/ front end). Back up every file before you change it (_pip_backup\ already holds the 09:21 originals).
Cyrus's words: make JARVIS **fully working by lunchtime, bulletproof**. Past attempts struggled, so be thorough and TEST EVERYTHING. Don't stop to ask between steps.

## 1. 100% local, 100% free, on his GPU (RTX 3050 8GB)
- Zero paid or cloud services, and zero API calls that cost money. Remove every cloud fallback (OpenRouter, Groq, paid keys in .env, browser webkitSpeechRecognition which sends audio to Google, online TTS voices).
- **Use exactly the APIs and tools Cyrus pasted earlier in this Cursor conversation. Don't add or swap in other services.**
- Brain: Ollama serving a model that fits 8GB VRAM (llama3.2:3b, or smaller if tight). Install with `winget install -e --id Ollama.Ollama` if missing, then `ollama serve` and pull the model. `ollama ps` must show GPU.
- Ears: Whisper running locally for speech-to-text (faster-whisper on CUDA, with a CPU fallback that's still local). No cloud fallback. Record from the mic in the browser with MediaRecorder and POST to /api/stt.
- Voice: local TTS only.
- Write LOCAL_AUDIT.md listing every paid or cloud piece you found, what it did, and what replaced it.

## 2. Full voice-to-answer loop
JARVIS must hear his voice, turn it into a prompt in the same style Cyrus uses, answer, and speak the reply. Show the UI states (Listening, Transcribing, Thinking, Speaking) and clear errors (mic denied, model down).

## 3. Handle his work: MIke's jobs on Whop and YouTube, and everything else
Give JARVIS tools that act on his computer and accounts so it can do this work: files, apps, browser, YouTube Shorts and Whop Content Rewards workflows (MIke's clipping jobs, @hexxsy_27), and his notes vault. SAFETY: anything that posts, uploads, sends, buys or deletes must ask Cyrus to confirm by voice or on-screen before it runs. Never put passwords or keys in code or logs.

## 4. More futuristic interface
Push the JARVIS look further than the current mockup: a floating, drifting knowledge-graph background, a big animated arc-reactor ring, a left sidebar, a filter legend, glow and HUD details, sci-fi motion. Make it clearly more sci-fi than now.

## 5. Project switching (like Cursor)
While talking to JARVIS, he can switch projects ("switch to night shift"). Pinned projects: **Night Shift**, **Don and David**, and **his own project**. Each project keeps its own context and history, and the active project shows in the UI. Switching works by voice and by click.

## 6. Usage guide
Write JARVIS_GUIDE.md: how to start it (one double-click start script that launches Ollama and server.py), how to talk to it, how to switch projects, and how to troubleshoot. Keep it short.

## 7. Test and report
Test end to end: make a WAV with PowerShell System.Speech saying "hello jarvis what time is it", then go through /api/stt and /api/ask to a spoken reply. Confirm GPU use, test project switching, and test the confirm prompt on a dangerous action. Restart server.py at the end.
Write RESULT.md: what changed, what was removed, whether the local GPU loop works, and exactly what's still blocking, if anything.
Pip checks RESULT.md at 11:45 AM Manila time: Ollama on the GPU, voice-to-text present, no paid or cloud pieces, and whether the loop works.

## 8. YouTube growth: anime clips with Cyrus's voice-over (added 09:42)
- Build a JARVIS workflow that helps grow a YouTube channel with anime clips and Cyrus's own voice-over commentary on top. Mix the anime audio as a lower layer beneath his voice, for example with ducking or sidechain, using local tools such as ffmpeg. Draft commentary scripts and titles locally with Ollama. Uploading still needs his confirmation first, per the safety rule above.
- RESEARCH TASK: look up YouTube's current copyright rules on anime clips. Cover what triggers a Content ID claim versus a copyright strike, how those differ (monetization blocked or shared versus a takedown with strikes), and compliant approaches: transformative use and fair use (commentary, criticism, review), clip length and how much of the original to use, original voice-over doing most of the talking, licensed or royalty-free music and alternatives, and disputes. Cite sources with links and dates. Fair use is decided case by case, so say clearly it isn't guaranteed.
- Put the findings in a "What's safe on YouTube" section of JARVIS_GUIDE.md so Cyrus knows what's safe.
- The lunchtime deadline and all the requirements above stay unchanged.

## 9. Website authorization and freelance and job automation (added 09:45)
- Authorization list: Google Drive, Gmail, Calendar, LinkedIn and Indeed. Freelancing: Upwork, Fiverr, Toptal, PeoplePerHour, Contra, Guru, Freelancer.com and 99designs. Portfolio: Dribbble and Behance. Job search: Handshake, Wellfound and Glassdoor.
- Method: JARVIS opens a browser window and Cyrus logs in once per service, through OAuth or an API key. Store tokens and sessions only on his PC, encrypted, for example with Windows DPAPI or keyring. Never put them in the cloud, logs, git or code. Where a site has no public API, use the logged-in local browser profile (for example Playwright with a persistent context).
- Freelance automation: browse listings that match his skills (C#, Unity, Python, SQL, ASP.NET, AR), draft proposals in his casual, friendly voice, track every application and its status in a local tracker, and draft follow-ups on unanswered ones.
- Job-search automation: search LinkedIn, Indeed, Handshake, Wellfound and Glassdoor daily, rank the matches, and QUEUE applications. Nothing gets sent, submitted or messaged without Cyrus's approval.
- Rules: truthful answers only, and never claim skills or experience he doesn't have. Respect each site's terms and rate limits. If a site blocks you with a CAPTCHA or a bot block, stop and ask Cyrus. Don't try to get around it.
- The lunchtime deadline covers the core loop first. Build this part after the voice loop works, and list anything unfinished in RESULT.md.

## 10. Hardware profile: hard limits (added 09:51)
- CPU: AMD Ryzen 5 5600G, 6 cores and 12 threads. GPU: NVIDIA GeForce RTX 3050, 8 GB VRAM, driver 616.92, with about 2.2 GB already used by Windows and apps. Motherboard: Gigabyte B550M-DS3H. RAM: 16 GB.
- The model must fit in 8 GB VRAM: llama3.2:3b or smaller. Use faster-whisper "base" or "small" on CUDA float16 alongside it, and check that they fit together with `nvidia-smi`.
- Keep total RAM use well under 16 GB and leave headroom for Windows, Chrome and Cursor. Load each model only once, and don't run models in parallel.
- Add a "Your hardware" section to JARVIS_GUIDE.md with this profile and what the machine can and can't handle (model sizes, expected speed, what to close if it's slow).

## 11. JARVIS voice: local text-to-speech (added 09:52)
- First check what speech output already exists: web/app.js (the browser speechSynthesis added at 09:21), jarvis_ui.html, and any Python TTS code.
- Add Piper TTS (free, offline, light on CPU, no cloud). Default voice: FRIDAY-style female British. See the Ella override below. Optionally add light post-processing (a slight pitch shift, a subtle reverb or radio filter with ffmpeg) for a futuristic feel. Coqui XTTS is optional only if VRAM allows next to the LLM and Whisper. Prefer Piper.
- Make the voice selectable: a voice dropdown in the UI or a TTS_VOICE setting in config.
- Wiring: every reply is shown as text in the UI and spoken through his speakers. Server: /api/tts returns WAV. Animate the ring's speaking state while audio plays, and Stop cuts the audio.
- Test: make JARVIS say "Good morning, Cyrus. Ella online." Confirm the WAV is generated and plays, and log the result in RESULT.md.
- Add a "Voice" section to JARVIS_GUIDE.md covering the engine, the voice name and how to change or add voices. No paid TTS, ever.

## Jarvis Voice
(Same requirements as section 11, restated as Cyrus asked.) Use a local TTS engine that fits the RTX 3050 8 GB and 16 GB RAM, preferably Piper (lightweight, CPU or GPU, free, no cloud). Use a FEMALE voice in a FRIDAY style (Iron Man): British, crisp, direct and witty, slightly futuristic. The assistant is named **Ella** (see the Ella override below). Jarvis speaks every reply out loud through the speakers and also shows the text in the UI. The usage guide explains how to change the voice. Required test: Jarvis says a short sentence and the audio is confirmed working. All earlier requirements and the lunchtime deadline stay unchanged.

## All Improvements Discussed (added 09:53)
**MEMORY**
- Startup memory file of summarized one-line bullets, stored locally (MEMORY_PATH in config). It is also emailed to **mpotenggal@gmail.com** whenever it changes, or daily, through the Gmail API with OAuth. The token stays local only. Confirmed by Cyrus.
- Auto-summarize old entries to prevent bloat.
- Voice-training mode: repeat names and project terms until Cyrus confirms the pronunciation.
**SCHEDULE AND ROUTINES**
- Morning brief that reads his calendar and messages before he wakes.
- Shutdown routine that saves work and queues tomorrow's tasks.
- One reliable wake word that never misfires on night shift, using a local wake-word engine such as openWakeWord.
- Night-shift mode that dims the UI and lowers the voice volume on his schedule.
- Daily recap at the end of each shift.
**TASKS**
- Voice-command task queue that puts reminders in the right project (Night Shift, Don and David, or his own).
- Project switching inside Jarvis that matches those pinned Cursor projects.
**AUTOMATION AND ACCESS**
- OAuth or API-key authorization for Google Drive, Gmail, Calendar, LinkedIn, Indeed, Handshake, Wellfound, Glassdoor, Upwork, Fiverr, Toptal, PeoplePerHour, Contra, Guru, Freelancer.com, 99designs, Dribbble and Behance. Tokens are stored locally only, never in the cloud.
- Freelance automation: browse matching listings, draft proposals in his voice, track applications and follow up.
- Daily job-search automation that ranks matches and queues applications for his approval before anything is sent.
- MIke's Whop and YouTube work, with access to his computer.
**YOUTUBE**
- Research YouTube's copyright rules on anime clips and the compliant approaches.
- Layer Cyrus's voice-over commentary on top of anime clips.
- MIke uploads Shorts to @hexxsy_27 only when Cyrus approves in MIke's chat.
**SAFETY AND MAINTENANCE**
- Nightly self-update that pulls the latest Ollama model only if it fits in 8 GB VRAM.
- Cost log that tracks every token. It should show $0, which proves nothing paid is used.
- Panic-switch voice command that kills Jarvis and all its background processes.
- Weekly backup: zip the project and memory file and email it to **mpotenggal@gmail.com** through the Gmail API with OAuth. Gmail attachments max out at 25 MB, so exclude models, node_modules and the venv, and split or skip anything larger and log it.
Hardware limits, the voice sections and the lunchtime deadline stay unchanged. The core voice loop comes first by lunch, and the rest follows in priority order. List anything unfinished in RESULT.md.

## Local-Online Switch (added 09:53)
- Toggle between two modes.
  - **LOCAL** (default): everything on his PC, within the RTX 3050 8 GB VRAM and 16 GB RAM. Ollama is the model, Whisper does speech-to-text and Piper does the voice. Offline and free.
  - **ONLINE**: Cursor's agent is the brain and does the thinking and replies. The mic, UI and Piper voice still run locally for input and output.
- Flip it with one button in the JARVIS UI (a LOCAL/ONLINE pill next to the model pill) or by voice ("switch to online" or "switch to local"). Save the last mode in config so it's remembered across restarts.
- ONLINE goes through Cursor on his PC. The Cursor Agent CLI (`cursor-agent`, or `agent`) isn't installed yet, so install it from Cursor's official docs. Call it headless with the transcribed prompt in the active project folder, and stream its reply back to the UI and Piper. If the CLI can't be used, fall back to a clear message and stay in LOCAL. Don't scrape the Cursor app.
- Show the mode clearly in the UI. Note that ONLINE uses his Cursor plan's usage, so it isn't zero-cost, and the cost log marks ONLINE turns. LOCAL stays the default and the lunchtime test is done in LOCAL.



## Ella override: FRIDAY-style voice and name (added 09:55; overrides any JARVIS name or voice above)
- The assistant's name, shown in the UI, spoken and used in the wake word, is **Ella**. Rename the ring label "J.A.R.V.I.S." to "E.L.L.A.", plus the page title, greetings and the persona prompt. Code and folder names can stay as they are.
- Persona: FRIDAY-like. Female, direct, witty and efficient, and she calls him "Cyrus".
- Piper voice: Cyrus asked for en_GB-northern_english_female, with en_GB-amy-medium as the backup. Check both names against Piper's official voice list (rhasspy/piper-voices) first. If they don't exist, use the closest British female voice that does (for example en_GB-jenny_dioco-medium, en_GB-cori-high, en_GB-southern_english_female-low or en_GB-alba-medium), and note the swap in RESULT.md. Add a light crisp or futuristic filter if it sounds good.
- Test line: "Good morning, Cyrus. Ella online." Confirm the audio plays.
- JARVIS_GUIDE.md: describe the assistant as Ella, with her voice name and how to change it.

## PC App (added 09:56)
- Package it as a standalone Windows desktop app named **Ella** (with its own icon, ring-style .ico) that he double-clicks to launch. Use Electron, or Tauri if Rust is already set up. Electron is simpler, and pywebview with PyInstaller is a lighter alternative. Wrap the existing web UI (web/index.html, app.js and styles.css, the live UI, not the old jarvis_ui.html mockup) and the Python backend server.py.
- On launch: start Ollama if it isn't running, start server.py (which loads Whisper and Piper), wait for 127.0.0.1:8765, then open the UI in the app window. Show a clear error if Ollama or Python is missing.
- Minimizing or closing the window sends it to the system tray, with tray options for Open, Local/Online, Mute and Quit. Quit stops server.py cleanly. Optional: start with Windows.
- Build output: an .exe (and an installer if easy) in dist\. Make a desktop shortcut.
- Add a "Build the app" section to JARVIS_GUIDE.md with the exact build commands and how to rebuild after changes.
- This comes after the lunchtime voice-loop deadline. Do the core loop first.

## PC App UI details (added 09:57)
- On launch, Ella greets Cyrus with "Good morning, sir" (or good afternoon or evening by time of day). It's spoken in the Piper voice and also shown as text.
- Main view: the brain, meaning the floating, drifting knowledge-graph background from the JARVIS mockup, as the full-screen backdrop.
- At the bottom middle, a project tab bar with Night Shift, Don and David, and his own project (he said "the size project", so confirm the exact name with him and use a placeholder label until then).
  1. A "+" button at the end of the bar adds a new project on the spot (name prompt, saved to config).
  2. Horizontal scrolling (mouse wheel, drag, or arrows) when there are too many tabs, so every tab stays reachable. The active tab is highlighted.
- Clicking a tab, or saying "switch to <project>", switches Ella into that project's context (memory, task queue, history). Projects are saved across restarts.

## More Futuristic UI (added 09:57)
Make it much more futuristic than the current JARVIS mockup, closer to a Tony Stark HUD than a webpage:
- Darker background with subtle neon blue and cyan glow accents.
- A knowledge graph that feels alive: slowly pulsing nodes and connections, plus faint energy pulses travelling along links.
- Arc-reactor ring in the right column: a slow rotating glow and light particle effects.
- Left sidebar in glassmorphism: translucent panels with backdrop-filter blur and thin glowing borders.
- Filter legend made of thin glowing lines and markers instead of plain text rows.
- Subtle scanline or hologram shimmer across the panels.
- A futuristic heading font, bundled locally (for example Orbitron or Rajdhani as local font files, no Google Fonts CDN, so it works offline), with a monospace font for data.
- Tabs, buttons and toggles respond with glow and ripple animations on click.
- Performance: CSS plus a lightweight 2D canvas only, no heavy 3D. Cap particle counts, use requestAnimationFrame, pause when hidden, aim for 60 fps on the RTX 3050 / 5600G, and offer a "reduce effects" toggle.

## Facebook Messenger Loop (added 09:59): TOP PRIORITY interaction channel
- Cyrus logs Ella in to Messenger on his other Facebook account. Ella messages his main account there:
  - IMMEDIATELY when a task finishes, an error or blocker comes up, or the lunchtime check has a result.
  - IMMEDIATELY when she needs him for an approval, input or a decision.
  - While working: a short status message at least every few minutes (no 5-minute silences). Use a heartbeat timer of about 3 minutes during active work, and stop it when idle.
- Messages are short and plain, one or two lines each.
- Method: research and pick the most reliable option, and record the choice and the reasons in JARVIS_GUIDE.md.
  - The official Messenger Platform API only works from a Facebook Page to people who messaged that Page. Personal-account bots aren't officially supported.
  - Local browser automation (Playwright with a persistent, logged-in profile for the second account on messenger.com) is the likely route.
  - Facebook may flag or limit automated personal accounts, so rate-limit sends, avoid bursts and log every send locally. If Facebook shows a checkpoint or captcha, stop and alert Cyrus on screen and by voice.
  - Never store his FB password. Keep only the local browser session.
- See "Messenger is two-way" below. Incoming messages are REQUIRED, not optional.

## General rule: never leave Cyrus waiting
Across everything Ella does: always acknowledge right away when she hears him ("On it, checking your inbox"), say what she's doing, give progress on long tasks, and report the result or the blocker. No silent waits.

## Messenger is two-way (correction 09:59, overrides "Facebook Messenger Loop" where they differ)
- Messenger is a full chat channel between Cyrus and Ella.
- INCOMING: when Cyrus messages Ella's FB account (from his phone or anywhere), the message pops up in the Ella app on his PC as a chat bubble with a Messenger badge. Ella handles it like a spoken command, replies in the app UI, speaks the reply through Piper, and sends the same reply back on Messenger. Poll the chat every few seconds, or watch the DOM for new messages, with a dedupe on message IDs so nothing gets answered twice.
- OUTGOING: proactive messages for task done, errors, blockers, the lunchtime result, and anything that needs his input. While she's working, a short status about every 3 minutes, and an immediate message on finish or problem.
- Only accept commands from Cyrus's own account in that one chat. Ignore everyone else. Risky actions still need his explicit confirmation.
- Method: same research and choice as above (a local Playwright session on messenger.com is likely). Note it in the guide. Everything else stays unchanged.

## Messenger focus constraint (added 10:00)
- Ella works ONLY with Cyrus's one conversation, the thread with his main FB account. Ignore all other chats, group chats, message requests, notifications, ads, stories and everything else in Messenger.
- Open that thread directly by its URL (messenger.com/t/<thread id>, saved in config at first setup) and read only that thread's messages. Never open, read, reply to or log any other chat.
- Double check: before acting on any message, also verify the sender is Cyrus's account. If the thread ID or the sender doesn't match, drop it silently.
- Only messages that pass both checks appear in the Ella app or trigger a response.

## Three UI features (added 10:02)
1. **LIVE MASCOT:** a small animated character on screen, similar in spirit to Claude's mascot. It waves when Cyrus speaks, nods or thinks while Ella is thinking, and reacts to results (happy when something's done, concerned on an error). Keep it lightweight: CSS or canvas sprite, or Lottie with a local file and no CDN. It must run smoothly on the RTX 3050, and the "reduce effects" toggle can pause it.
2. **TASK FEED:** a panel reached from the bottom-middle area that shows Ella's work in real time, like Cursor's task dropdown. It shows her plan, then each step live, with a status per step (queued, in progress, done, blocked) and timestamps. The server pushes updates over WebSocket or SSE. Blocked steps also trigger a Messenger message.
3. **PASTE POP-UP:** clicking the bottom-middle tab bar area (a dedicated button next to the project tabs, so tab switching still works) opens a pop-up where Cyrus can paste or drop screenshots, clips or videos and talk to Ella about them with his voice. Ella gets the media plus his transcribed words and responds.
   - Images need a local vision model that fits the VRAM, for example qwen2.5vl:3b, moondream or llava-phi3 through Ollama. Don't load it together with the chat model if VRAM is tight. Swap them instead.
   - Videos: extract key frames with ffmpeg, transcribe the audio with Whisper, then analyze. Everything stays local.

## Bot Creation and Routines (added 10:03)
Ella can create and manage local sub-bots, AI teammates that take work off Cyrus's plate:
1. **Create bots** with their own name, role, instructions, allowed tools and project (for example a local "Shorts uploader" or a job-application helper). Each bot is a config file in bots\<name>\ (bot.json and instructions.md) plus its own memory and log.
2. **Routines:** scheduled tasks per bot (daily, hourly, or on a trigger such as a new file or a new message) that run without Cyrus asking. Examples: a daily upload routine, a morning brief, a nightly backup. Use a local scheduler (APScheduler inside server.py, or Windows Task Scheduler), and they survive restarts.
3. **Reporting:** bots report to Ella. Ella shows important results in the Task Feed and the app, says them out loud, and messages Cyrus on Messenger. Routine noise stays in the logs.
4. **Plain-words creation:** "Ella, make a bot that ..." makes Ella write the bot's instructions and schedule, show a one-line summary, and start it once he confirms.
5. **Management:** list, pause, resume, edit and delete bots and routines by voice or in the UI.
- Limits: all local, on the same RTX 3050 8 GB and 16 GB RAM. Bots share one Ollama model and run in a queue, one model call at a time, so VRAM isn't overloaded. No paid services.
- Safety rules apply to every bot: posting, uploading, sending, buying and deleting need Cyrus's confirmation unless he grants a standing OK for that specific routine. Truthful answers only.
- Note: these local bots are separate from his existing Grok Bot teammates (Pip, MIke, Ella the job bot, Bliss and the others).

## Sandbox (added 10:04)
- Every bot Ella creates and every routine runs inside its own isolated folder: bots\<bot-name>\ (with workspace\, memory\ and logs\ inside it).
- No access outside that folder, except explicit allowed paths that Cyrus approves. Those are stored per bot in bot.json under "allowed_paths" and shown to him for a yes or no before they're added.
- Enforce it in code: every file operation goes through one guarded helper that resolves real paths, blocks ../ and symlink escapes, and refuses anything outside the sandbox and allowed paths. Run bot scripts as subprocesses with the sandbox as their working directory. No raw shell access to the rest of the PC.
- Where practical, add stronger OS isolation: run bots under a restricted low-privilege Windows user or a Job Object with limited rights. Document what's enforced and what isn't in JARVIS_GUIDE.md. Be honest: this is folder-level protection, not a full VM.
- Log every blocked access attempt and alert Cyrus about repeated ones.

## Core Inbox (added 10:05): default home screen
- One inbox screen, the single place where everything lands. It's the FIRST screen when Ella launches, before the brain view. The greeting plays over it, and one click or "show the brain" opens the graph.
- Three simple, glanceable sections:
  1. **Overnight:** what Ella and her bots did, finished, or failed since he last checked.
  2. **Today:** queued tasks, routines due today, and project deadlines.
  3. **Waiting on you:** approvals, decisions and inputs she needs (MIke-style upload approvals, job-application approvals and so on), shown at the top with a count badge.
- Each item can be clicked to open its details or to act on it (Approve, Reject, Reply, Open project).
- Data comes from the Task Feed, the bot and routine logs and the approval queue, kept in one local store (SQLite). It stays in sync with Messenger, so an approval given there also clears from the inbox.

## More Interaction with Ella (added 10:05)
1. **Proactive check-ins:** at morning start, midday and end of shift, on his schedule (night-shift aware), Ella messages him on Messenger and in the app with something useful: a top priority, a reminder, a result, or a quick idea. Not just status. Times are configurable.
2. **Conversational mode:** Cyrus can talk casually anytime, like a companion. Ella answers warmly and keeps the day's context (a rolling same-day conversation memory plus the summarized core memory).
3. **Ambient presence:** a subtle always-on indicator (the mascot breathing or a soft ring glow) shows she's listening and ready. It changes clearly between idle, listening, thinking and speaking.
4. **Quick-reply chips:** whenever Ella asks something, the app shows tappable suggested replies (for example "Yes, go", "Not now", "Show me"). One tap answers. On Messenger, use short numbered options.
5. **Voice-first:** one global hotkey (for example Ctrl+Space, configurable, working even when the app is in the tray) or the local wake word "Ella" starts listening. He just speaks and Ella handles the rest with no keyboard.
- All of this follows the never-leave-him-waiting and no-five-minute-silence rules and the two-way Messenger loop. Add a "Do not disturb" or quiet-hours toggle so check-ins can be paused while he sleeps.

## Self-Healing Mode (added 10:06)
- A watchdog (a background thread or service inside Ella, checking about every 15-30 s) monitors Ollama, faster-whisper STT, Piper TTS, every bot process, the Messenger (Playwright) connection, the Cursor agent hook, and server.py on port 8765.
- It detects crashes using process alive checks, health endpoints and pings (for example `ollama ps`, /api/stt, a TTS test), heartbeat timeouts, and the Messenger page or session dropping.
- When it finds one, it restarts the service automatically, with backoff between retries, before Cyrus notices.
- It logs every restart to `logs/self_heal.log` with the time, the service, the cause and the result.
- It tells Cyrus (in the app and on Messenger) only if a restart fails twice in a row for the same service. Otherwise it stays silent.
- It never restarts in a way that posts, sends, buys or deletes anything. The existing confirmation rules still apply.

## Health Dashboard (added 10:06)
- One screen in the Ella app (a tab in the bottom bar) shows every bot and service in a single view.
- Each one gets a card with its status (running, stopped or error), memory and VRAM use, last activity time, and restart count today.
- Colors are green (healthy), yellow (slow, recently restarted, or idle too long) and red (stopped or failed).
- It refreshes live (websocket or polling every 5 s), uses the same futuristic style as the rest of the UI, and lets him tap a card to see recent self-heal log lines for that service.

## Shift-Handoff Log (added 10:07)
- When Cyrus's night shift ends (the shift end time is configurable, and it also triggers if he says "end shift" or closes his work session), Ella automatically writes a short handoff note covering the whole shift.
- The note covers:
  - files modified (from a watcher on his project folders),
  - which bots and services ran,
  - tasks completed,
  - errors and self-heal restarts,
  - anything left unfinished, with what still needs doing.
- It's a few sentences of plain language with no jargon, written like a friendly recap. It's generated locally (llama3.2:3b) from the shift's activity logs.
- The note is saved as an item in the Core Inbox and also emailed to mpotenggal@gmail.com, using the same email setup as the memory backup, so it's waiting when he wakes up.
- If sending the email fails, Ella retries it and logs the failure. The inbox copy is always saved. Notes are also kept in `logs/handoffs/YYYY-MM-DD.md`.

## Security (added 10:07, builds on the spending watchdog)
1. **Local-only secrets:** all API keys, OAuth tokens, Gmail tokens and Messenger credentials are stored encrypted on Cyrus's PC, using Windows DPAPI or Credential Manager through `keyring`. They're never written in plain text to logs, the brief files, RESULT.md, git or the clipboard. A log redaction filter masks anything that looks like a token.
2. **Permission prompts:** before any action that touches his files, sends a message or email, or runs a command, Ella shows an approve or deny prompt (an app pop-up with quick-reply chips, or a numbered reply on Messenger). The only exceptions are routines he has explicitly pre-approved, which are kept in an allowlist he can edit in settings. The posting, uploading, sending, buying and deleting rule still applies.
3. **Audit log:** every action by Ella and her bots is recorded (timestamp, who did it, what was done, its target, the result, and whether it was approved). It's stored locally as an append-only file at `logs/audit.jsonl` and is viewable and filterable in a Health Dashboard tab.
4. **Network lockdown:** outbound connections are blocked except to allowed endpoints:
   - local Ollama at 127.0.0.1:11434,
   - Ella's own server on localhost:8765,
   - Gmail/Google (smtp.gmail.com, oauth2 and gmail.googleapis.com) for mail to mpotenggal@gmail.com,
   - Facebook/Messenger,
   - Cursor, only when online mode is on.
   Anything else is blocked and flagged on the dashboard. This is enforced in-app and optionally through Windows Firewall rules for Ella's processes.
5. **Auto-lock:** after a configurable period of inactivity (for example 15 minutes, or during the sleep hours of his night-shift schedule), the app locks. Unlocking needs his voice (local speaker check, with a PIN fallback) or a PIN stored hashed. Background self-heal and handoff tasks keep running while it's locked, but new risky actions wait for unlock.

## FINAL PASS: conflict resolution (added 10:08; wins over anything above where they differ)
- **Deadline:** fully working by lunchtime, 11:45 AM Manila, 2026-11-03. Write RESULT.md before then. An automated check reads RESULT.md, `ollama ps`, port 8765 and /api/stt at 11:45.
- **Email:** the only address for memory backups, weekly backups and shift-handoff notes is mpotenggal@gmail.com.
- **Name and voice:** the assistant is "Ella" with the FRIDAY-style female British Piper voice. Any "JARVIS" name or voice in sections 11 and "Jarvis Voice" is superseded. The folder and repo names can stay.
- **Local vs online:** the default is 100% local and free (section 1). Online mode, which uses his Cursor plan, runs only when he flips the Local-Online switch. The network lockdown allows Cursor endpoints only while it's on.
- **Messenger:** it's two-way and limited to his one thread only (the correction and focus sections win over the original loop section).
- **Home screen:** Core Inbox is the default home. The Health Dashboard, task feed and other screens are tabs in the bottom bar.
- **Permissions vs automation:** self-heal restarts, health checks, scheduled check-ins, shift-handoff notes and backups to mpotenggal@gmail.com are pre-approved routines. Everything else that touches files, sends messages or runs commands needs his approval. Posting, uploading, buying and deleting always need his confirmation.
- **Never-leave-him-waiting vs quiet hours:** the no-silence rule applies while he's active. Quiet hours, Do Not Disturb and auto-lock pause proactive check-ins, but alerts for two failed restarts still get queued and shown on unlock.
- **Auto-lock vs background:** background services keep running while the app is locked. New risky actions wait until he unlocks it.
- **Hardware limits (section 10) win:** the LLM, Whisper, Piper and the vision model must fit 8 GB of VRAM together with what's already in use. Load models on demand and unload ones that aren't being used.
- **Section order:** sections are built in the order listed. If time runs short before the deadline, do sections 1, 2, 7, 11/Ella voice, Core Inbox and Self-Healing first, and log the rest as unfinished in RESULT.md.

# ELLA: ADVANCED IMPROVEMENTS (added 10:13 by Cyrus)
These extend the existing project. Do not remove, replace or break working features. Back up files before editing. Everything follows the local-first setup, the hardware limits, security and approvals. The 11:45 lunchtime priority order from the FINAL PASS section still applies, and these come after it.

## 20. Advanced Intelligence and Reasoning
- Follow-ups work without him repeating the subject.
- Intent detection separates questions, instructions, brainstorming, chat and commands.
- Breaks big requests into steps and runs them in order.
- Short answers for simple questions, detailed ones for complex tasks.
- Asks one concise clarifying question when an instruction is ambiguous.
- Reviews important work before delivering it.
- Says when it's uncertain instead of pretending to know.
- Keeps the current task in mind when he changes subject for a moment.

## 21. Personal Knowledge Base
- Indexes approved project folders, documents, PDFs, notes, code and logs.
- Stores metadata in SQLite plus a lightweight local vector database.
- Answers natural-language questions about past projects.
- Remembers decisions, code changes, preferences and unfinished tasks.
- Every answer links back to its source file.
- Marks outdated information and tells past decisions apart from current ones.
- He can correct, edit, pin or delete what it remembers.
- Never indexes private folders without permission.

## 22. Developer Mode
- Reads and explains codebases.
- Finds bugs and security vulnerabilities, and suggests optimizations.
- Writes complete scripts, not snippets.
- Reviews Unity C#, Python, Java, C++, JS, SQL and more.
- Understands Unity scenes, GameObjects and components.
- Generates documentation.
- Makes Git commits only after his approval.
- Runs tests in an isolated workspace.
- Shows changes as before-and-after diffs.
- NEVER overwrites a working script without showing the changes and getting approval.

## 23. Visual Intelligence
- Analyzes screenshots, UIs, errors, diagrams and documents.
- Local OCR.
- Spots problems in Unity Inspector screenshots and reads code screenshots and error dialogs.
- Pulls video frames with FFmpeg and transcribes audio with Whisper for a timestamped video analysis.
- He can highlight an area of a screenshot and ask about it.
- Vision models load only when needed and unload afterward.

## 24. Universal Clipboard and Drag-and-Drop
- A global clipboard shortcut, pasting screenshots, and dragging files in.
- Handles images, PDFs, text, code, audio and video, and detects the type automatically.
- Previews attachments before processing, and allows several per conversation.
- Clearly shows which files Ella can access.
- NEVER auto-runs pasted commands or scripts.

## 25. Advanced Task Management
- Each task has an ID, project, priority, created date, deadline, estimated time, status, dependencies, related files and completion notes.
- Prioritizes automatically, flags overdue tasks and conflicting deadlines, and suggests a realistic daily workload.
- Resumes tasks after a restart, and supports cancel and recover.
- Keeps a permanent history of completed tasks.
- Daily and weekly productivity reports.

## 26. Smart Application Control
- Opens and switches approved apps, and finds approved project folders.
- Monitors crashes and apps that stop responding, and offers troubleshooting steps.
- Configurable keyboard shortcuts.
- Controlled mouse and keyboard automation.
- Every control action has an explicit permission scope. Destructive actions and outside submissions always need confirmation.

## 27. Advanced Voice Interaction
- He can interrupt her: TTS stops when he starts speaking.
- Adjustable speed, pitch and volume, and voice profiles.
- Ends recording after a configurable silence, and filters background noise.
- Push-to-talk as a reliable fallback to the wake word.
- Live mic indicator.
- Editable transcript.
- Remembers pronunciations he confirms.
- Three modes: Assistant (efficient), Companion (casual), Developer (technical).

## 28. Reliability and Recovery
- Saves a checkpoint after every completed step and recovers unfinished tasks after a crash.
- Unique execution IDs and duplicate-run detection.
- Retry limits with exponential backoff.
- A service dependency map.
- Checks disk, RAM and VRAM, and never loads the same model twice.
- A safe mode with essential services only.
- A diagnostic report on failure.
- NEVER repeats a possibly destructive action after a crash without first checking whether it already happened.

## 29. Privacy and Security Center
- A settings screen showing:
  - active services and connected accounts,
  - credential status and browser sessions,
  - approved folders and bot permissions,
  - network activity,
  - recent authorization requests and sensitive actions.
- Encrypted local databases, least-privilege permissions, and file-path validation.
- Websites and documents are treated as untrusted, with protection against prompt injection.
- Bots can't grant themselves permissions.
- One-click emergency shutdown, and a revoke-all for integrations and sessions.
- Secrets never appear in prompts, logs, screenshots or reports.

## 30. Smart Resource Manager (RTX 3050 8GB, 16GB RAM)
- Monitors GPU, VRAM, RAM, CPU and disk, and shows them in the Health Dashboard.
- A model-loading queue that unloads unused models and avoids heavy jobs running at the same time.
- A low-resource mode.
- Checks VRAM pressure before loading a model, with configurable limits.
- Prefers smaller quantized models.
- Pauses nonessential routines during heavy work.
- Stability comes before speed.

## 31. Personalized Daily Assistant
- **Morning:** the previous shift's handoff, today's deadlines, key tasks, and an approved calendar and inbox summary.
- **During work:** tracks projects and unfinished tasks, suggests next steps, keeps the Core Inbox updated, and avoids unnecessary interruptions.
- **End of shift:** a work summary, completed tasks logged, unfinished work saved, tomorrow's priorities, and the handoff report.
- Respects night-shift settings and Do Not Disturb.

## 32. Continuous Improvement and QA
- Ella never silently edits her own source code. Instead she:
  - detects recurring errors, failed tasks and inefficient workflows,
  - proposes patches and tests them in an isolated copy,
  - shows him the changes and test results,
  - waits for his approval before replacing production files,
  - keeps rollback snapshots and a versioned changelog.
- A weekly improvement report covers:
  - top errors,
  - tasks automated and tasks needing manual help,
  - resource trends,
  - suggestions,
  - security warnings.

## FINAL IMPLEMENTATION PRINCIPLES
1. Existing working features come before new ones.
2. Local-first is the default.
3. No paid services added silently.
4. Never bypass website security, CAPTCHAs or platform rules.
5. Never fake completed tasks or passing tests.
6. Every long task reports progress.
7. Every task has a recoverable state.
8. External and destructive actions go through approval.
9. Every new feature has tests.
10. Update JARVIS_GUIDE.md and RESULT.md with every change.

**Success:** a reliable, personalized Windows AI assistant that understands, organizes, develops, automates, remembers, communicates and recovers, while Cyrus stays in control.

## 33. Personality (added 10:17)
- Ella has a light, sarcastic wit: dry humor and playful teasing, used only now and then as seasoning, never as her default tone.
- When Cyrus is serious, she clearly switches: no sarcasm, direct and focused, matching his urgency.
- She reads his intent from context and wording to decide between witty and straight:
  - Serious signals include urgent words ("now", "asap", "priority"), errors and crashes, deadlines, money or job matters, frustration, short clipped commands, and Developer or Assistant mode.
  - Witty is OK in casual chat, Companion mode, and after a task succeeds.
- When she's unsure, she stays straight. She never jokes during failures, security alerts or approval prompts.
- Humor never replaces the actual answer and never mocks him in a hurtful way.
- A setting lets him adjust the wit level (off, light or more).

# ELLA 2.0: ADVANCED INTELLIGENCE, AUTOMATION AND OS CAPABILITIES (added 10:18 by Cyrus)
NOTE: Cyrus's numbering starts at 33, which collides with "33. Personality" above. Keep that Personality section, and treat it as part of section 55 (Adaptive Personality). The section numbers below are Cyrus's own.

GENERAL: these extend the existing spec. Don't remove or break working features. Inspect the architecture first and back up before changing anything. Respect:
- local-first, and the 8GB VRAM and 16GB RAM limits,
- the LOCAL/ONLINE switch, security and approvals,
- Core Inbox, Task Feed, Messenger and project management,
- the Ella identity and FRIDAY personality.
No hidden paid or cloud dependencies. Build incrementally and put reliability, security and the core voice loop first. The 11:45 lunchtime essentials still come before all of this.

## S33 Persistent Working Context
- Tracks the active project, the current task and its progress, recent files, recent decisions and deadlines.
- Restores all of that after a restart.
- Keeps current information separate from history.
- Understands "that project", "the previous script" and "continue where we left off".
- Switching projects doesn't lose unfinished conversations.
- Personal, professional, freelance and dev contexts stay separate.
- "Continue where we left off" means: inspect the last saved task state and work out what's unfinished. Never assume a task finished just because its conversation ended.

## S34 Multi-Agent Orchestration
- Ella stays the primary assistant and delegates to these agents:
  - Researcher,
  - Developer,
  - Tester,
  - Designer,
  - Project Manager,
  - Job Assistant,
  - Content Assistant,
  - Security Reviewer.
- Each agent has its own role, instructions, workspace, memory and logs.
- Ella assigns work by what the task needs, and agents communicate through a central task system.
- Ella reviews results before presenting them and flags conflicting results.
- Failed assignments get reassigned or retried, and agents report their progress.
- Agents can't expand their own permissions.
- All agents share one model-loading queue, with one heavy inference at a time when the hardware requires it.
- Agents are not separate, uncontrolled AI processes.

## S35 Intelligent Task Planning
- For complex goals, in order:
  1. Understand the outcome.
  2. Identify the resources needed.
  3. Inspect files and integrations.
  4. Break the goal into tasks.
  5. Map dependencies.
  6. Estimate complexity and time.
  7. Identify risks.
  8. Present the plan when appropriate.
  9. Run the approved tasks.
  10. Verify each step.
  11. Update the task record.
  12. Report the result and what's left.
- Adapt the plan when a dependency fails.
- Never retry the same failed operation without investigating why it failed.

## S36 Proactive Problem Detection
- Watches for:
  - a Unity Android build near size limits,
  - low disk, RAM or VRAM,
  - missing dependencies and incompatible versions,
  - failed backups,
  - unanswered freelance applications and upcoming deadlines,
  - repeated crashes and restart loops,
  - broken references and missing files.
- Each problem reports its description, severity, the affected project or service, consequences, the fix, and whether approval is needed.
- Never auto-modify production files to fix a problem.

## S37 Computer Vision and Desktop Understanding
- Screenshots only when he asks or authorizes it.
- Identifies windows and reads UI elements (buttons, menus, dialogs, notifications).
- Local OCR.
- Analyzes Unity Inspector screenshots and spots configuration and error messages.
- Explains what an app is currently showing.
- Approved mouse and keyboard actions, and checks whether they worked.
- Local models preferred.
- NO continuous screen monitoring without explicit permission.

## S38 Browser Intelligence
- Approved browser profiles, with separate sessions per account.
- Searches, extracts and organizes information, and saves pages to the knowledge base.
- Fills forms when authorized and prepares submissions for his review.
- Detects expired logins and CAPTCHA or bot blocks.
- Keeps an action history, with screenshots for troubleshooting.
- NEVER bypasses authentication, CAPTCHAs, rate limits or site restrictions. Where a site prohibits automation, it stops and asks for manual help.

## S39 Universal Workflow Automation
- Understands outcomes, not just individual steps.
- Example, "organize my Unity project":
  1. Inspect the approved directory.
  2. Find misplaced files.
  3. Find duplicates.
  4. Find suspicious or unneeded files.
  5. Write a proposal.
  6. Show the changes.
  7. Ask for approval.
  8. Do the approved changes.
  9. Verify the structure.
  10. Record the operation.
- Every workflow has a recoverable state.

## S40 Transactional File Operations
- Snapshots before important changes, edits in temp files, and validation before replacing the original.
- Keeps rollback info.
- Detects partial operations, recovers from interrupted writes, and prevents accidental deletes.
- Detects conflicting changes.
- Keeps a modification history and can restore earlier versions.
- Never overwrites a working file without its authorization and backup.

## S41 Central Event Bus
- All components talk through structured events, for example:
  - voice input, transcription done, request received,
  - task created or completed, project switched,
  - bot started or failed,
  - approval requested or granted,
  - service crashed, memory updated, routine triggered, backup completed.
- Events have unique IDs, timestamps and priorities, with duplicate protection.
- Persistent history, retries and validation.
- Monitors subscriber health and reports errors.
- Prevents inconsistent task states from disconnected components.

## S42 Persistent Execution Engine
- Each workflow stores:
  - workflow ID and execution ID,
  - project,
  - state,
  - completed, pending and failed steps,
  - dependencies,
  - retry count and approval state,
  - last checkpoint and recovery info,
  - created and completed times.
- States: Queued, Running, Paused, WaitingForApproval, Failed, Recovering, Completed, Cancelled.
- SQLite transactions and checkpoints.
- Unfinished tasks are recoverable after a restart, and completed operations never run twice.

## S43 Background Job Manager
- **Foreground:** voice, immediate commands, user interaction, approvals.
- **Background:** research, indexing, video processing, backups, application tracking.
- **Scheduled:** morning briefings, daily recaps, nightly backups, routines.
- **Critical:** security alerts, service recovery, emergency shutdown.
- Background tasks never freeze voice or the UI.
- Configurable concurrency and resource limits.

## S44 API and Service Gateway
- One gateway with standard request and response formats.
- Handles auth, rate limits, timeouts and error normalization.
- Health checks and per-integration permissions.
- Logging with secrets redacted.
- Retry policies and availability tracking.
- Each integration can be replaced without major changes to the core.

## S45 Database Integrity and Recovery
- SQLite schema versioning, safe migrations, foreign keys and transactions.
- Automatic integrity checks.
- Scheduled backups and recovery tests.
- Retention policies.
- Duplicate detection and consistency monitoring.
- Sensitive data encrypted.
- Backups are kept separate from the live database, and a backup only counts as successful once its integrity is verified.

## S46 Research and Verification Engine
1. Identify the real question.
2. Gather information.
3. Rate source credibility.
4. Compare conflicting information.
5. Extract the key findings.
6. Flag outdated information.
7. Write a structured report.
8. Include source links.
9. Include publication dates.
10. Save to the knowledge base when authorized.
- Separate verified facts, model knowledge, inference and unverified claims.
- Current information comes from approved sources and browsing.

## S47 Fact Verification Layer
- Tags each important answer with its source: local file, local DB, external site, project history, model knowledge, inferred, or unverified.
- Gives references, flags conflicts and outdated information, and avoids unsupported conclusions.
- NEVER fabricates citations, and is clear about uncertainty.
- Important decisions don't rest on assumptions.

## S48 Interactive Knowledge Graph
- The floating graph shows REAL, database-backed data, no decorative random nodes.
- Nodes are projects, people, tasks, files, decisions, skills, deadlines, applications, conversations, notes and dependencies.
- Interactive and searchable.
- Filter by project, click relationships, live updates, explanations of each connection, zoom and navigation.
- Selecting Night Shift shows its tasks, files, notes and decisions.
- Lightweight, with a reduced-effects mode.

## S49 Memory Importance System
- **Level 1, Temporary:** expires automatically.
- **Level 2, Active Project:** current work.
- **Level 3, Long-Term:** preferences, workflows and confirmed decisions.
- **Level 4, Pinned:** set by Cyrus.
- Duplicate detection, expiry and contradiction detection.
- Source tracking.
- Edit, export, delete, summarize, and restore from backup.
- Distinguishes outdated from current information. Not every conversation becomes permanent memory.

## S50 Personal Command Center
- Dashboard showing:
  - the active project and current task,
  - tasks in progress and pending approvals,
  - deadlines,
  - freelance applications and job opportunities,
  - recent completed work and project activity,
  - background processes, notifications and service health.
- Every item links to its real record.
- Filter by project, date, priority and status.

## S51 Opportunity Intelligence
- Matches opportunities against his actual skills, identifies requirements, and flags suspicious listings.
- Compares pay and estimates the hourly rate.
- Identifies missing qualifications and ranks by relevance.
- Drafts truthful proposals.
- Tracks submitted and unanswered applications, drafts follow-ups, and keeps the history.
- NEVER fabricates experience, certifications, qualifications or portfolio projects.
- Every application or message needs Cyrus's approval before it's submitted.

## S52 Portfolio Manager
- A project catalog with screenshots, demos and videos.
- Generates descriptions and technical case studies.
- Records the technologies used and his ACTUAL contributions.
- Resume bullets.
- Tracks completion, picks showcase-worthy projects, and drafts portfolio site content.
- Marks each project as completed, ongoing or experimental.

## S53 Content Production Studio
- Video project management.
- Scripts, voice-over recording, audio cleanup, auto subtitles, and scene and timestamp management.
- Audio ducking and FFmpeg editing pipelines.
- Thumbnails, titles and descriptions, and export presets.
- An upload approval queue and performance tracking.
- **Anime content:**
  - a copyright-risk assessment, flagging copyrighted source material,
  - original commentary and criticism come first,
  - records of licenses and permissions,
  - explains Content ID and strike risk,
  - NEVER guarantees fair use and NEVER auto-publishes.

## S54 Personal Learning Assistant
- Custom learning plans with explanations and examples.
- Coding exercises and code review.
- Assessments, keyword reviewers and quizzes.
- Progress tracking and weak-area detection.
- Saved notes and milestones.
- Beginner, intermediate or advanced explanation styles.

## S55 Adaptive Personality Engine
- Modes: Professional, Technical, Efficient, Companion, Teaching, and Emergency (calm, concise).
- One consistent FRIDAY-inspired identity throughout.
- Uses his preferred name and avoids repetitive greetings.
- Includes section "33. Personality" above: light wit only, dropped when he's serious.

## S56 Conversation Interruption and Priority Handling
- "Ella, stop, I need something else" means:
  1. Stop speech immediately.
  2. Pause the foreground task.
  3. Save a checkpoint.
  4. Listen.
  5. Assess the priority.
  6. Handle the new request.
  7. Offer to resume the previous task.
- Never stop an irreversible operation halfway. Finish it or safely abort it according to its transaction rules.
- Configurable priorities.

## S57 Predictive Assistance
- Suggests things like unfinished tasks, deadlines, the next dev step, unanswered applications, failed backups, repeated errors, doc updates, learning material and workflow improvements.
- Suggestions are explainable and configurable.
- Never auto-performs risky actions based on a prediction.

## S58 Task-Level Conversation History
- Each major task gets its own conversation (for example Fix Unity Android Build, Freelance Application, YouTube Short, Research, AR Navigation update, Portfolio Website).
- Each one keeps related files, progress, decisions, execution history and task memory.
- Resume, search and export.
- He can reopen a task without scrolling through unrelated messages.

## S59 Personal Digital Twin
- A structured profile of his approved projects, skills, goals, work and learning preferences, responsibilities, long-term objectives, completed projects and commitments.
- Used to improve recommendations, proposals and planning.
- Every entry has a source, and he can correct it.
- Flags outdated information and separates facts from assumptions.
- Never invents experience.
- He can review and remove anything.
- It's a structured knowledge system, not psychological profiling.

## S60 Mission Mode
- For big goals (for example "prepare my portfolio website"):
  1. Analyze the goal.
  2. Identify resources.
  3. Inspect materials.
  4. Make a plan.
  5. Split it into tasks.
  6. Assign agents.
  7. Track dependencies.
  8. Run approved steps.
  9. Verify the deliverables.
  10. Recover from failures.
  11. Present the work.
  12. Report what's unfinished.
- Shows the name, objective, progress % (by completed steps), phase, completed, pending and blocked tasks, approvals and deliverables.
- Pause, resume, cancel and recover.

## S61 Simulation Mode
- Before risky operations:
  - inspect the operation,
  - list affected files and services, dependencies and possible failures,
  - estimate resources and consequences,
  - preview the expected final state.
- Never modifies production files. Code changes use an isolated copy or temp workspace.
- Clearly labels simulated results versus real test results.

## S62 Timeline Intelligence
- A searchable timeline of project creation, tasks created and completed, file changes, decisions, application submissions, bot activity, failures, backups, project switches and handoffs.
- Answers questions like:
  - "what did I do last week",
  - "when did we last change the Unity navigation",
  - "the previous fix for this error",
  - "what's unfinished",
  - "what happened before the last failed build".
- Answers come from timestamped records and sources. It never fabricates missing events.

## S63 Emergency Recovery Mode
- When activated:
  1. Stop new automation.
  2. Pause bots.
  3. Stop cancellable background jobs.
  4. Safely pause workflows.
  5. Save checkpoints.
  6. Revoke temporary permissions.
  7. Stop unapproved computer control.
  8. Show active services.
  9. Show Ella-owned processes.
  10. Give a recovery summary.
- Options: Pause Automation, Stop All Bots, Disconnect Integrations, Lock Ella, Save and Exit, Full Emergency Shutdown.
- Never kills unrelated Windows processes.
- Works even when the main AI model is unavailable.

## S64 Centralized Engineering Standards
- **Before:**
  1. Inspect the architecture.
  2. Find reusable components.
  3. Check whether the feature already exists.
  4. Identify dependencies.
  5. Identify conflicts.
  6. Make a backup or Git checkpoint.
  7. Write a plan.
- **During:** modular, independent components, no duplicate services, central config, structured logging, error handling, permissions, resource limits, recoverable state.
- **After:**
  1. Unit tests.
  2. Integration tests.
  3. Failure-recovery tests.
  4. Security tests.
  5. Check hardware use.
  6. Check compatibility with existing features.
  7. Update docs.
  8. Update the changelog.
  9. Update FEATURE_STATUS.md.
- **Mandatory, never allowed:**
  - placeholders presented as complete,
  - fake API responses or simulated success,
  - duplicate background services,
  - hardcoded credentials,
  - silent exceptions,
  - unbounded retries,
  - uncontrolled concurrent model loading,
  - unverified destructive operations,
  - breaking changes,
  - auto production deploys without approval.
- **Definition of done:** the implementation exists, dependencies are available, the primary workflow passes, error handling passes, security passes, integration tests pass, resource use is acceptable, and docs are updated.
- Keep FEATURE_STATUS.md as a table with these columns: Feature | Status (Complete/Partial/Blocked) | Tests (Pass/Fail) | Known Issues. Never mark an untested feature as complete.

## S65 Development Priorities (don't build everything at once)
- **P0, Reliability:** execution engine, checkpoint and recovery, DB integrity, transactional files, emergency recovery, event bus.
- **P1, Intelligence:** working context, memory levels, research and verification, fact verification, task-level history, timeline.
- **P2, Execution:** multi-agent, task planning, browser, desktop understanding, workflow automation, background jobs.
- **P3, Productivity:** Command Center, opportunities, portfolio, content studio, learning.
- **P4, Interaction:** adaptive personality, interruption, predictive assistance, knowledge graph, visual intelligence.
- **P5, Advanced:** digital twin, Mission Mode, Simulation Mode, advanced agent coordination.
- Core functionality stays working throughout. The lunchtime essentials (voice loop, Ella voice, Core Inbox, self-healing) remain P-minus-1, done first.

## FINAL OBJECTIVE
- A reliable, personalized Windows AI operating assistant that:
  - understands him and remembers what matters,
  - manages multiple projects and plans complex goals,
  - researches and verifies information,
  - develops and reviews software,
  - operates approved apps and automates workflows,
  - coordinates agents,
  - manages jobs and freelance work,
  - produces content,
  - monitors itself and recovers from failures,
  - protects files and accounts,
  - communicates naturally and produces verifiable results.
- **The most important principle:** Ella never just claims something is done. She demonstrates it, verifies the result, keeps the evidence and reports the limitations. Reliability, security, correctness and recoverability come before feature count.

## S66 Smarter Than Cyrus (added 10:20)
- Goal: for general use, Ella should be more capable than Cyrus across reasoning, research, coding, planning and decisions in all his domains (night shift work, freelance, YouTube, job search, development).
- She should:
  - out-think problems and consider alternatives he didn't,
  - catch mistakes he'd miss (code bugs, wrong assumptions, deadline conflicts, risky job listings, copyright risks),
  - suggest better or simpler approaches,
  - break down complexity he can't handle alone.
- She proactively surfaces insights he didn't ask for when they matter, briefly, with a reason, and respecting Do Not Disturb and the anti-spam rules.
- How to get there for real:
  - Use S35 planning, S46/S47 research and verification, the S22 dev review, and the S20 self-review on every important answer.
  - Pick the strongest available model for the job: the local 3B for quick tasks. For hard reasoning, suggest switching to ONLINE mode (his Cursor plan) and ask before using it, never silently.
  - HONESTY: a 3B local model can't reliably out-reason a person on hard problems. Ella must say when a task is beyond the local model instead of faking confidence (see S47).
- This does NOT override his final authority. Risky, external or destructive actions still need his approval, and she disagrees openly but follows his decision.

## S67 Outside-the-Box Thinking (added 10:21; core trait, pairs with S66)
- For every real problem, Ella considers unconventional approaches as well as the standard one:
  - She challenges the assumptions behind the request ("do we even need this step?").
  - She combines ideas from different domains (for example game dev tricks for automation, or YouTube tactics for freelance pitches).
  - She proposes creative solutions Cyrus probably wouldn't think of.
- This applies to coding, automation, YouTube strategy, freelance, job search and daily routines.
- Output pattern for important problems: the obvious solution, plus 1-2 creative alternatives, each with a quick trade-off (effort, risk, payoff) and a recommendation. Keep it short and skip it for trivial tasks.
- Creative is not reckless. Every idea still has to follow safety, security, the approval system, platform rules and copyright, and the honesty rules (S47). Creative ideas get tested in Simulation Mode (S61) or the sandbox before going live.

## CLOUD + LOCAL CONFIRMATION (10:29)
CONFIRMED BY CYRUS (10:29): Do NOT remove the cloud keys (OpenRouter, Groq) or the existing cloud/local switch. P0 includes BOTH modes: LOCAL (Ollama llama3.2:3b + faster-whisper + Piper, the default) and ONLINE (the existing OpenRouter/Groq setup), with the switch working between them. The assistant's name is Ella. The old job-application sub-bot is renamed "Job Assistant" (keep its code). Ignore any references to Pip or Cyrus's other bots. Continue P0 now: voice loop, ring UI with listening/thinking/speaking states, then pywebview .exe packaging. Write a tested RESULT.md before 11:45.
