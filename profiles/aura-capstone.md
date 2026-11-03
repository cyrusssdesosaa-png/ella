# Aura AR campus navigation

## What it is

Capstone prototype. A phone AR app that places a SketchUp model of the school building in the room, then walks the user to a room with a minimap, arrows, and search. Product name in the docs is Aura. Scene that matters is `finalapp 2`.

## Path

`D:\capstone`

User manual: `Docs/users-manual.md`. Living change log: `STATUS.md`. Contributor line in that manual is Cyrus Wendell P. De Sosa.

## Stack

- Unity `6000.3.11f1`, URP, AR Foundation, ARCore on Android
- Input System package (do not call legacy `UnityEngine.Input` in new UI)
- Navigation graph of pre-placed nodes under `Building_Floorplan`, A* in `FinalUserNavigationController`
- YOLO / segmentation experiments under `Tools/ml_pipeline` and `v2m_video_pipeline`. Label Studio was used for frames. Current kept set is `yolo_hybrid`, `dataset_seg_hybrid`, latest YOLO run, `segformer`
- Unity MCP package `com.ivanmurzak.unity.mcp` for the Editor bridge
- Android APKs were built from this folder (`dev app.apk` and later test builds)

## What was built

The app flow is welcome, then "at the entrance" or "already inside", then floor choice, then a bird's-eye map tap, then Start / Confirm to drop an `ARAnchor` named `WorldAnchor`. After confirm, `Building_Floorplan` stays parented to that anchor so the map does not ride the camera.

Walking on device uses the AR camera delta scaled by `androidLocomotionMetersScale`, with a jump clamp and smoothing. GPS hybrid was tried and later turned down because indoor GPS noise was bad. A small on-device "Walk x" tuner writes PlayerPrefs.

Two meshes, `Mesh1` and `Mesh2`, are the floors. Height decides which floor the minimap treats as current. Renderers stay available so pathfinding colliders do not vanish. Search is a Google-Maps style box over waypoint nodes (`WaypointSearchAndNavigateUI`). Route arrows and the line must follow the obstacle-lifted path, not a straight cut through walls. Arrival clears the path and can speak with Android TTS.

QR image anchoring was removed. Anchoring is manual Start / Confirm only.

A Play Mode helper, `FinalAppPresentationCheat`, forces a desktop demo and can tint the floorplan magenta for a presentation. Minimap and arrows stay their own colors.

Docs for the defense: `Docs/system-block-diagram.svg`, `Docs/system-schematic-diagram.svg`, `Docs/system-flow-chart.svg`, plus a PNG of the flow chart, and `Docs/users-manual.md`.

## Important objects (do not rename)

`finalapp 2`, `Building_Floorplan`, `Mesh1`, `Mesh2`, `Nodes`, `Player`, `Player 2` (inactive pose marker), `AR_XRHost`, `NavigationSystems`, `ViewCamera`, `FinalApp_UICanvas`, `WorldAnchor`.

`GameObject.Find` fallbacks depend on these names.

Scripts that carry the behavior:

- `Assets/Scripts/FinalAppSimple/FinalAppARFloorplanAnchor.cs`
- `Assets/Scripts/FinalAppSimple/FinalAppCircularMinimap.cs`
- `Assets/Scripts/FinalAppSimple/AuraOnboardingFlow.cs`
- `Assets/Scripts/FinalAppSimple/FinalAppPresentationCheat.cs`
- `Assets/Scripts/ARCampusNavigationDev/FinalUserNavigationController.cs`
- `Assets/Scripts/ARCampusNavigationDev/ARPathNavigationController.cs`
- `Assets/Scripts/ARCampusNavigationDev/WaypointSearchAndNavigateUI.cs`
- `Assets/Scripts/ARCampusNavigationDev/NodeInteractionController.cs`

Floorplan scale in the scene is `localScale = 280`. That number is the authored SketchUp scale, not a measured meter scale. Do not rescale the building to "fix" walking. Tune `androidLocomotionMetersScale` instead.

## How Cyrus works on it

He sends Game view or phone photos when the map is pink, arrows are wrong, the player falls, or search suggestions are empty. Read the shot, then check the script and the scene. Append real changes to `STATUS.md`. Refresh and compile in Unity before calling a change build-ready.

Editor Play Mode is a desktop stand-in. AR subsystems are disabled in the Editor on purpose. Device truth is an Android build.

## Known issues that already ate time

- Floorplan looked solid on device when the material was not actually transparent (URP Unlit, `_Mode`, `_TintColor`).
- Map drifted because `Building_Floorplan` got parented under the camera or player, or the anchor was frozen while tracking kept moving.
- A* returned no path when the graph had no edges, when physics chords were skipped, or when the safety plane was in the raycast mask.
- Search text on Android reverted to the partial query because the soft keyboard restored it.
- Minimap proxies copied the cyan floor tint and looked like a slab.
- `Player 2` must stay a transform marker. A second CharacterController phased through the mesh.
- C: fills up from Unity temp, Gradle, and ML frame dumps. Clean generated caches, not the source model or the current dataset.

## Status

Prototype used for the capstone manual and presentation. Last status notes in `STATUS.md` run through 2026-05-07 (ML storage cleanup) and 2026-05-04 (contributor statement). Scene work after that was not logged in the portion read for this profile. Check `STATUS.md` and git or Plastic history before assuming a later fix is missing.

## Do not

- Reintroduce QR anchoring.
- Rename the critical objects listed above.
- Store new video datasets or YOLO runs on `C:`.
- Claim GPS indoor tracking is accurate.
