"""faster-whisper transcription + language detection."""

import numpy as np
from faster_whisper import WhisperModel

from config import (
    DEFAULT_LANG,
    LANGUAGE_CONFIDENCE_THRESHOLD,
    WHISPER_COMPUTE,
    WHISPER_DEVICE,
    WHISPER_MODEL,
)

_last_lang = DEFAULT_LANG


def load_whisper() -> WhisperModel:
    """Load the Whisper model once at startup."""
    return WhisperModel(
        WHISPER_MODEL,
        device=WHISPER_DEVICE,
        compute_type=WHISPER_COMPUTE,
    )


def transcribe(model: WhisperModel, audio: np.ndarray) -> tuple[str, str]:
    """
    Transcribe audio and detect language.

    Returns (transcript_text, language_code).
    Falls back to previous language if confidence < threshold.
    """
    global _last_lang

    audio = np.asarray(audio, dtype=np.float32).flatten()
    if audio.size == 0:
        return "", _last_lang

    segments, info = model.transcribe(audio, beam_size=5)
    text = "".join(segment.text for segment in segments).strip()

    if info.language_probability >= LANGUAGE_CONFIDENCE_THRESHOLD:
        lang = info.language or _last_lang
    else:
        lang = _last_lang

    if lang:
        _last_lang = lang

    return text, lang
