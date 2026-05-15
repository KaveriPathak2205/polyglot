"""Polyglot — real-time multilingual voice agent (entry point)."""

import logging
import os
import sys
import time

from asr import load_whisper, transcribe
from audio import play_audio, record_until_silence
from config import DEFAULT_LANG
from llm import ConversationMemory, chat
from tts import speak
from vad import load_vad, warmup

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)


def main() -> None:
    print("Polyglot Voice Agent starting...")

    print("Loading VAD...")
    vad_model = load_vad()
    warmup(vad_model)

    print("Loading Whisper...")
    whisper_model = load_whisper()

    memory = ConversationMemory()
    current_lang = DEFAULT_LANG

    print("Ready. Speak now. (Ctrl+C to quit)\n")

    try:
        while True:
            t0 = time.time()
            audio = record_until_silence(vad_model)

            transcript, detected_lang = transcribe(whisper_model, audio)
            t1 = time.time()

            if not transcript.strip():
                continue

            if detected_lang != current_lang:
                print(f"[Language switch: {current_lang} → {detected_lang}]")
                current_lang = detected_lang

            print(f"User ({current_lang}): {transcript}")

            reply = chat(memory, transcript, current_lang)
            t2 = time.time()

            print(f"Agent ({current_lang}): {reply}")

            wav_path = speak(reply, current_lang)
            t3 = time.time()

            play_audio(wav_path)
            t4 = time.time()

            try:
                os.remove(wav_path)
            except OSError:
                pass

            print(
                f"[Latency] ASR: {(t1 - t0) * 1000:.0f}ms | "
                f"LLM: {(t2 - t1) * 1000:.0f}ms | "
                f"TTS: {(t3 - t2) * 1000:.0f}ms | "
                f"Total: {(t4 - t0) * 1000:.0f}ms\n"
            )

    except KeyboardInterrupt:
        print("\nGoodbye.")
        sys.exit(0)


if __name__ == "__main__":
    main()
