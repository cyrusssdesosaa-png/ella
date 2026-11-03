"""Local speech-to-text with faster-whisper. Model loads on first use."""

import os
import tempfile
import threading

# Patch av.open to drop the metadata_errors kwarg that faster-whisper passes
# but this PyAV build does not accept.
import av as _av

_av_real_open = _av.open


def _av_safe_open(*args, **kwargs):
    kwargs.pop("metadata_errors", None)
    return _av_real_open(*args, **kwargs)


_av.open = _av_safe_open

_MODEL = None
_INFO = ""
_LOCK = threading.Lock()
SIZE = os.environ.get("ELLA_STT_MODEL", "base.en")


def _load():
    global _MODEL, _INFO
    if _MODEL is not None:
        return _MODEL
    from faster_whisper import WhisperModel

    errors = []
    for device, compute in (("cuda", "float16"), ("cpu", "int8")):
        try:
            _MODEL = WhisperModel(SIZE, device=device, compute_type=compute)
            _INFO = f"{SIZE} on {device} {compute}"
            return _MODEL
        except Exception as exc:
            errors.append(f"{device}: {exc}")
    raise RuntimeError("; ".join(errors))


def transcribe(raw, suffix=".webm"):
    if not raw or len(raw) < 800:
        return {"ok": False, "error": "No audio came through. Check the mic."}
    fd, path = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(raw)
        with _LOCK:
            try:
                model = _load()
                segments, _ = model.transcribe(path, language="en", beam_size=1, vad_filter=True)
                text = " ".join(seg.text.strip() for seg in segments).strip()
            except RuntimeError as exc:
                if "cuda" in str(exc).lower() or "cublas" in str(exc).lower():
                    global _MODEL, _INFO
                    from faster_whisper import WhisperModel

                    _MODEL = WhisperModel(SIZE, device="cpu", compute_type="int8")
                    _INFO = f"{SIZE} on cpu int8"
                    segments, _ = _MODEL.transcribe(path, language="en", beam_size=1, vad_filter=True)
                    text = " ".join(seg.text.strip() for seg in segments).strip()
                else:
                    raise
    except Exception as exc:
        return {"ok": False, "error": f"Speech-to-text failed: {exc}"}
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
    if not text:
        return {
            "ok": False,
            "error": "I heard only silence. Speak a bit louder or closer to the mic.",
            "engine": _INFO,
        }
    return {"ok": True, "text": text, "engine": _INFO}
