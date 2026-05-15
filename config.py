"""All tunable values — nothing hardcoded in other modules."""

import sys
import tempfile
from pathlib import Path

# Project root (directory containing this file)
PROJECT_ROOT = Path(__file__).resolve().parent

# Whisper / ASR
WHISPER_MODEL = "base"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE = "int8"
LANGUAGE_CONFIDENCE_THRESHOLD = 0.6

# Ollama
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.2:3b"
OLLAMA_TIMEOUT_S = 60

# Audio / VAD
SAMPLE_RATE = 16000
CHUNK_SAMPLES = 512  # Silero v5 requires 512 samples @ 16 kHz (32 ms)
CHUNK_DURATION_MS = 32
SILENCE_THRESHOLD_S = 1.2
VAD_THRESHOLD = 0.5
MIN_UTTERANCE_S = 0.3

# Piper TTS — download .onnx + .onnx.json from https://github.com/rhasspy/piper/releases
PIPER_MODELS = {
    "en": "models/en_US-amy-medium.onnx",
    "hi": "models/hi_IN-rohan-medium.onnx",  # hemant not on HF; rohan is Hindi medium
    "es": "models/es_ES-mls_9972-low.onnx",
}

if sys.platform == "win32":
    PIPER_BINARY = str(PROJECT_ROOT / "piper.exe")
else:
    PIPER_BINARY = str(PROJECT_ROOT / "piper")

DEFAULT_LANG = "en"
TEMP_DIR = tempfile.gettempdir()


def get_piper_model(lang_code: str) -> tuple[str, bool]:
    """Return (model path relative to project root, used_fallback)."""
    if lang_code in PIPER_MODELS:
        return PIPER_MODELS[lang_code], False
    return PIPER_MODELS[DEFAULT_LANG], True


def resolve_path(relative: str) -> Path:
    """Resolve a path relative to project root."""
    return PROJECT_ROOT / relative
