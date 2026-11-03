---
name: aura-unity
description: >-
  Works on the Aura AR campus navigation capstone in Unity. Use when Cyrus
  mentions Aura, capstone, finalapp, floorplan, minimap, AR anchor, campus
  navigation, or D:\capstone, including screenshots of that app.
---

# Aura Unity

Read `profiles/aura-capstone.md` before editing.

## Rules that already cost days

- Scene is `finalapp 2` at `D:\capstone`. Do not rescale `Building_Floorplan` (authored scale 280). Tune walk speed instead.
- Do not rename `Nodes`, `Player`, `Mesh1`, `Mesh2`, `AR_XRHost`, `ViewCamera`, or `NavigationSystems`.
- Anchoring is Start / Confirm onto `WorldAnchor`. QR anchoring stays deleted.
- Path lines and arrows must not cut through wall colliders.
- Input System only. No legacy `UnityEngine.Input`.
- Editor Play Mode is not device AR. Say so when a bug only exists on the phone.
- Append a dated line to `D:\capstone\STATUS.md` when the change is real.
- Unity `6000.3.11f1`. If the Editor already has the project open, use Unity MCP. Do not launch a second instance.
- If MCP is down, read the scripts and say you could not see the live console.

## Picture path

A pink floor, missing arrows, a fallen player, or empty search is a scene bug. Name the view in the shot, then patch the script listed in the profile.
