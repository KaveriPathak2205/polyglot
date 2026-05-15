"""Piper TTS — synthesize speech in the language-matched voice."""

import logging
import subprocess
import uuid
from pathlib import Path

from config import (
    DEFAULT_LANG,
    PIPER_BINARY,
    PROJECT_ROOT,
    TEMP_DIR,
    get_piper_model,
    resolve_path,
)

logger = logging.getLogger(__name__)


def speak(text: str, lang_code: str) -> str:
    """
    Synthesize text with Piper for the given language.

    Returns path to the output WAV file.
    """
    model_rel, used_fallback = get_piper_model(lang_code)
    if used_fallback:
        logger.warning(
            "Unsupported TTS language %r — falling back to %s",
            lang_code,
            DEFAULT_LANG,
        )

    model_path = resolve_path(model_rel)
    json_path = Path(f"{model_path}.json")

    if not model_path.exists():
        raise FileNotFoundError(
            f"Piper model not found: {model_path}\n"
            "Download .onnx files from https://github.com/rhasspy/piper/releases"
        )
    if not json_path.exists():
        raise FileNotFoundError(
            f"Piper model config not found: {json_path}\n"
            "Download the matching .onnx.json alongside the .onnx file."
        )

    piper_bin = Path(PIPER_BINARY)
    if not piper_bin.is_absolute():
        piper_bin = PROJECT_ROOT / piper_bin
    if not piper_bin.exists():
        raise FileNotFoundError(
            f"Piper binary not found: {piper_bin}\n"
            "Download from https://github.com/rhasspy/piper/releases"
        )

    wav_path = str(Path(TEMP_DIR) / f"polyglot_reply_{uuid.uuid4().hex}.wav")

    subprocess.run(
        [
            str(piper_bin),
            "--model",
            str(model_path),
            "--output_file",
            wav_path,
        ],
        input=text.encode("utf-8"),
        check=True,
        cwd=str(PROJECT_ROOT),
    )

    return wav_path
