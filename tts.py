"""Local text-to-speech with Piper. Voice pre-loads at import."""

import io
import os
import threading
import wave
from pathlib import Path

_VOICE = None
_LOCK = threading.Lock()
_WARMUP_DONE = False

VOICES_DIR = Path(os.environ.get("ELLA_VOICES", r"D:\ella-voices"))
VOICE_NAME = os.environ.get("ELLA_VOICE", "jenny_dioco-medium")


def _load():
    global _VOICE
    if _VOICE is not None:
        return _VOICE
    from piper import PiperVoice

    onnx = VOICES_DIR / f"{VOICE_NAME}.onnx"
    if not onnx.exists():
        raise FileNotFoundError(f"Voice not found: {onnx}")
    _VOICE = PiperVoice.load(str(onnx))
    return _VOICE


def warmup():
    """Pre-load voice model in a background thread."""
    global _WARMUP_DONE
    if _WARMUP_DONE:
        return
    try:
        _load()
        _WARMUP_DONE = True
    except Exception:
        pass


def synthesize(text):
    """Return {"ok": True, "audio": bytes} or {"ok": False, "error": str}."""
    text = (text or "").strip()
    if not text:
        return {"ok": False, "error": "Nothing to say."}
    if len(text) > 2000:
        text = text[:2000]
    with _LOCK:
        try:
            voice = _load()
            buf = io.BytesIO()
            wav_file = wave.open(buf, "wb")
            voice.synthesize_wav(text, wav_file)
            wav_file.close()
            return {"ok": True, "audio": buf.getvalue()}
        except Exception as exc:
            return {"ok": False, "error": f"TTS failed: {exc}"}
