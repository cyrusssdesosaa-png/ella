# Read Aloud

## What it is

A browser page that speaks text he pastes. Built because a Unity text-to-speech setup was not available in that session.

## Path

`C:\Users\USER\fckkk\read-aloud`

Files: `index.html`, `app.js`, `styles.css`, `open.bat`.

## Behavior

The page title is Read Aloud. He pastes or types, then hits Play. The UI shows a word count and a rough time. Theme toggle is in the header. Fonts are Fraunces and Outfit. This uses the browser speech engine, not a paid voice API.

There is a separate Android TTS path inside the Aura capstone (`FinalAppAndroidTtsSpeaker.cs`) for navigation prompts. Do not mix the two. Campus voice cues stay in `D:\capstone`. This page is for reading arbitrary text on the PC.

## Pictures

If he sends a shot of the page, check whether Play produced no sound, the wrong voice, or a layout break, then change `app.js` or `styles.css` only.

## Status

Small finished page. Folder last written 2026-08-13.

## Do not

- Pull this into the Unity capstone.
- Add an account or a cloud voice unless he asks.
