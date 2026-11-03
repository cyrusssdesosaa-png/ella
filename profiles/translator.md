# Portable translator

## What it is

A small local web page Cyrus uses to translate, with extra polish for German, English, and Dutch creator-chat wording.

## Path

`C:\Users\USER\fckkk\translator`

Open with `open.bat`. That starts a local Python server with no leftover command window and opens `http://127.0.0.1:8787`. Do not open `index.html` by itself. Needs Python and internet.

Copy the whole folder to another PC. Instructions are in `COPY-TO-OTHER-PC.txt`.

## Files

- `server.py` local server
- `index.html`, `app.js`, `styles.css`
- `languages.js` language list
- `slang.js` slang polish for German, English, and Dutch
- `silent-open.vbs`, `open.bat`

## Behavior

Translation calls Google and MyMemory. It is not an offline model.

Languages wired in the notes: English, German, Dutch, French, Spanish, Italian, Polish, Portuguese, Turkish, Russian, Czech, Danish, Swedish, Norwegian, Finnish, Romanian, Hungarian, Greek, Japanese, Korean, Chinese, Arabic, Filipino.

Quick pairs: German and English, Dutch and English, German and Dutch.

Slang mode is for creator-chat tone on German, English, and Dutch output. It is a translator, not the chatter brain. If he pastes a fan line and wants a reply, use the chatter profile. If he wants words moved between languages, use this app.

## Pictures

If he screenshots the translator page, read the language pair, the slang toggle, and the error text before changing code.

## Status

Working portable app. Last folder write seen 2026-09-25.

## Do not

- Replace the page with a paid API that needs a key unless he asks.
- Bind the server to anything except localhost.
