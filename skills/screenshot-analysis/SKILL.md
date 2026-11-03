---
name: screenshot-analysis
description: >-
  Reads Cyrus's screenshots as the actual request before any edit or reply.
  Use when he attaches a picture, a phone shot, a Unity view, a chat
  screenshot, an error dialog, or says look at this, what is this, or fix this
  from an image.
---

# Screenshot analysis

Cyrus sends pictures instead of long explanations. The image is the spec. Read `profiles/operator.md` for the full habit.

## Steps

1. Look at the image before answering or editing. If text is too small, zoom, then read it.
2. In a few sentences, say what is on screen: which app, which view, and the exact error or label you can read.
3. Do the job the picture implies. A description alone is not the finish, unless he only asked what it is.
4. If one region is cut off or blurry, name that single gap and continue with everything else you can see.
5. After a visual change, check the real window when Unity or a browser is available.

## What the picture usually means

- Unity Game, Scene, Console, or Inspector: a bug in `D:\capstone` unless he named another Unity project. Read the console text. Then use the Aura skill.
- Phone shot of someone else's app: rebuild the flow in an original UI. Do not copy their logo, name, or exact skin. The loan-tracker chat was this case.
- Fan chat screenshot: the latest fan bubble is the message. Switch to the night-shift skill and output only the reply.
- Website or Teams frame for Wally Wombats: treat the visible words as client evidence. Use the Wally skill.
- Cursor, Windows, or browser error: quote the visible error, then fix the cause. Do not blame the project if the dialog is a Cursor outage.
- A look he wants for Jarvis or GOD: copy layout ideas only. Do not copy logos or brand assets.

## Do not

- Ask a stack of questions when the picture already shows the bug.
- Guess a price, a date, or an error code that is not readable.
- Store the image's private chat text into `profiles/`.
