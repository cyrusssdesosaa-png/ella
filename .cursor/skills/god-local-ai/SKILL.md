---
name: god-local-ai
description: >-
  Works on GOD, the local Windows AI at D:\GOD, and on its Story Studio
  bridge. Use when Cyrus says GOD, Jarvis desktop, vision panel, HUD,
  ollama, or D:\GOD. Use the Jarvis cy profile only when he means the new
  app in cy projects.
---

# GOD

Read `profiles/god.md`. If he means the new free daily app, read `profiles/jarvis-cy.md` instead. They are different folders.

## Rules

- Product UI is `D:\GOD\desktop-shell\release\GOD.exe`. Do not send him to the browser on port 8787 as the product.
- Do not rebuild Phase 0 or merge `D:\AIStoryStudio` into the GOD repo.
- Vision already exists (`/api/vision`, screen capture, image upload). Extend that when he wants picture analysis inside GOD. Behavior for reading his shots is the screenshot-analysis skill.
- Unity MCP stays off until the Editor is running on port 8080.
- Keep model files and media on `D:\`.
- Do not print `.env`.

## Check before adding a feature

Read `D:\GOD\CHANGELOG.md`. Version 1.31 already runs action tasks without a "continue" prompt. Do not re-add that loop.
