"""Microphone capture (VAD-gated) and speaker playback."""

import numpy as np
import scipy.io.wavfile as wavfile
import sounddevice as sd

from config import (
    CHUNK_DURATION_MS,
    CHUNK_SAMPLES,
    MIN_UTTERANCE_S,
    SAMPLE_RATE,
    SILENCE_THRESHOLD_S,
)
from vad import is_speech


def record_until_silence(vad_model) -> np.ndarray:
    """
    Stream mic input in 512-sample chunks, run VAD on each chunk,
    return the full utterance when silence exceeds SILENCE_THRESHOLD_S.
    """
    chunks: list[np.ndarray] = []
    silence_seconds = 0.0
    heard_speech = False
    chunk_duration_s = CHUNK_DURATION_MS / 1000.0
    min_samples = int(MIN_UTTERANCE_S * SAMPLE_RATE)

    print("Listening...", flush=True)

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        blocksize=CHUNK_SAMPLES,
    ) as stream:
        while True:
            chunk, _ = stream.read(CHUNK_SAMPLES)
            chunk = np.asarray(chunk, dtype=np.float32).flatten()

            if is_speech(vad_model, chunk):
                heard_speech = True
                silence_seconds = 0.0
                chunks.append(chunk.copy())
            elif heard_speech:
                silence_seconds += chunk_duration_s
                chunks.append(chunk.copy())

                if silence_seconds >= SILENCE_THRESHOLD_S:
                    audio = np.concatenate(chunks)
                    if audio.size >= min_samples:
                        return audio
                    # Too short — discard and listen again
                    chunks.clear()
                    heard_speech = False
                    silence_seconds = 0.0
                    print("Listening...", flush=True)


def play_audio(wav_path: str) -> None:
    """Play a WAV file through the default speaker."""
    sample_rate, data = wavfile.read(wav_path)

    if data.ndim > 1:
        data = data.mean(axis=1)

    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32768.0
    elif data.dtype == np.int32:
        data = data.astype(np.float32) / 2147483648.0
    else:
        data = data.astype(np.float32)

    sd.play(data, sample_rate)
    sd.wait()
