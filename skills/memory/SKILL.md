---
name: memory
description: Save a short fact and keep only the newest 30 with the profile.
---

# Memory

The vault at `vault/` is the long memory. Start at `vault/VAULT-INDEX.md`, then open the one note the step needs.

The profile lives in `data/profile.json`. Facts live in `data/memory.json`.

Keep the profile plus the newest 30 facts. When a 31st fact arrives, drop the oldest fact. A fact that should still be there next week also gets a home in the vault.

A fact is one sentence about a preference, a project, or a routine. Do not store passwords, API keys, phone numbers, home addresses, or resume files.

Search reads these files. It does not rewrite them.
