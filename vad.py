"""Silero VAD — ONNX inference without importing torchaudio."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

from config import CHUNK_SAMPLES, PROJECT_ROOT, SAMPLE_RATE, VAD_THRESHOLD

_CONTEXT = 64  # for 16 kHz


class SileroOnnxVAD:
    """Minimal Silero VAD ONNX wrapper (numpy state only, no torchaudio)."""

    def __init__(self, model_path: Path) -> None:
        import onnxruntime as ort

        opts = ort.SessionOptions()
        opts.inter_op_num_threads = 1
        opts.intra_op_num_threads = 1
        providers = ["CPUExecutionProvider"]
        self.session = ort.InferenceSession(
            str(model_path),
            providers=providers,
            sess_options=opts,
        )
        self.reset_states()

    def reset_states(self, batch_size: int = 1) -> None:
        self._state = np.zeros((2, batch_size, 128), dtype=np.float32)
        self._context = np.zeros((batch_size, _CONTEXT), dtype=np.float32)
        self._last_sr = 0
        self._last_batch_size = 0

    def __call__(self, x: np.ndarray, sr: int) -> float:
        x = np.asarray(x, dtype=np.float32)
        if x.ndim == 1:
            x = x.reshape(1, -1)
        if x.shape[-1] != CHUNK_SAMPLES:
            raise ValueError(
                f"Expected {CHUNK_SAMPLES} samples, got {x.shape[-1]}"
            )

        batch_size = x.shape[0]
        if not self._last_batch_size or self._last_batch_size != batch_size:
            self.reset_states(batch_size)
        if self._last_sr and self._last_sr != sr:
            self.reset_states(batch_size)

        x_in = np.concatenate([self._context, x], axis=1).astype(np.float32)
        ort_inputs = {
            "input": x_in,
            "state": self._state,
            "sr": np.array(sr, dtype=np.int64),
        }
        out, state = self.session.run(None, ort_inputs)
        self._state = state
        self._context = x_in[:, -_CONTEXT:]
        self._last_sr = sr
        self._last_batch_size = batch_size
        return float(np.asarray(out).reshape(-1)[0])


def _find_onnx_model() -> Path:
    """Locate silero_vad.onnx without importing silero_vad (avoids torchaudio)."""
    candidates: list[Path] = [
        PROJECT_ROOT / "models" / "silero_vad.onnx",
    ]

    for prefix in sys.path:
        candidates.append(
            Path(prefix) / "silero_vad" / "data" / "silero_vad.onnx"
        )

    for path in candidates:
        if path.is_file():
            return path

    raise FileNotFoundError(
        "silero_vad.onnx not found. Run:\n"
        "  pip install silero-vad onnxruntime\n"
        "Or copy silero_vad.onnx into polyglot/models/ "
        "(from site-packages/silero_vad/data/ after pip install)."
    )


def load_vad() -> SileroOnnxVAD:
    """Load Silero VAD ONNX model."""
    return SileroOnnxVAD(_find_onnx_model())


def warmup(model: SileroOnnxVAD) -> None:
    """Run one dummy inference so the first real chunk is fast."""
    chunk = np.zeros(CHUNK_SAMPLES, dtype=np.float32)
    model(chunk, SAMPLE_RATE)


def is_speech(model: SileroOnnxVAD, chunk: np.ndarray) -> bool:
    """Return True if chunk contains speech above VAD_THRESHOLD."""
    audio = np.asarray(chunk, dtype=np.float32).flatten()
    if audio.size != CHUNK_SAMPLES:
        raise ValueError(f"Expected {CHUNK_SAMPLES} samples, got {audio.size}")
    prob = model(audio, SAMPLE_RATE)
    return prob >= VAD_THRESHOLD
