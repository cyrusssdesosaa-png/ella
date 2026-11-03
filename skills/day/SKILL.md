---
name: day
description: Morning check-in, the activity list, and a missed check-in that runs once.
---

# Day

The check-in is four short lines: what matters today, the job to start, what is waiting on Cyrus, and the Manila time basis.

The side panel shows the latest check-in, today's daily note, and the activity list. A Windows toast uses the first line. A successful check-in appends a session to `vault/01 - Daily Notes/`.

If the check-in time has passed and today has no check-in, run it once. A failed routine retries once, then it goes to `data/outbox.json`.

Routines use Groq, then Ollama. They do not spend the OpenRouter chat cap.
