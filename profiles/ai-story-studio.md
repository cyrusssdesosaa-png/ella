# AI Story Studio

## What it is

A storytelling and video module that GOD calls. It is not part of the GOD git repository.

## Path

`D:\AIStoryStudio`

Bridge file: `god.studio.json`. GOD reaches it through `studio.bridge`.

## Layout

- `projects/` holds story projects
- `exports/` holds rendered output
- `assets/` holds source media
- `ollama-models/` holds local model files. Leave them on `D:`.
- `README.md` is the short contract with GOD

## How to work

New story work goes under `projects/`. Finished video goes under `exports/`. Do not copy this tree into `D:\GOD`. Do not put these media files on `C:`.

If Cyrus sends a frame or a storyboard image, describe the shot, then place notes or generated files in the matching story folder under `projects/`.

## Status

Scaffold is on disk as of 2026-08-26. `README.md` was touched again on 2026-10-29. Check `projects/` before assuming a story is empty.
