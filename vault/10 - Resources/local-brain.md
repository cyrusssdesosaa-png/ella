---
status: active
project: jarvis
type: guide
---

# Local brain

Default brain is local. It calls Ollama at `http://127.0.0.1:11434` and does not spend an API key. Cloud is a switch on the side panel. Cloud uses OpenRouter for chat and Groq for routines, then falls back to Ollama.

This PC has 8 GB of video memory. One heavy model at a time. `llama3.2:3b` fits. A 9B model is the size in the local-Jarvis demo and may be tight. Do not pull a 12B or 70B model onto this GPU.

Ollama was not running when this note was written. Start Ollama, then pick the installed model on the panel. The panel lists whatever `/api/tags` returns.

Voice stays local. Do not use ElevenLabs. Do not clone another person's voice. The installed Jarvis app is the voice. Kokoro is the local voice line when a clip needs one. Voice Studio is the open-source app from the demo. Install it later on `D:\` only for Cyrus's own voice.

Calendar and Gmail stay disconnected until Cyrus connects his own Google account in that tool's chat. Do not invent a meeting.

A website breakdown is notes about how a public page is built. The rebuild is original. Do not copy a name, logo, or asset.

The paid prompt pack from the video stays out. These notes are the pack.
