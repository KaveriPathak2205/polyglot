# Polyglot — Design Decisions

## 1. faster-whisper over Whisper.cpp

**Choice:** faster-whisper (Python bindings to CTranslate2).

**Why:** Native Python integration, single `pip install`, and built-in language detection via `info.language` / `info.language_probability` in one `transcribe()` call. Whisper.cpp would need a separate language-ID step or CLI parsing.

## 2. Llama 3.2 3B over larger models

**Choice:** `llama3.2:3b` via Ollama.

**Why:** Fits in ~4 GB RAM on a typical student laptop, starts quickly, and targets sub-500 ms generation for short voice replies. Larger models (7B+) improve quality but blow the latency budget and RAM.

## 3. Piper over Coqui XTTS

**Choice:** Piper (ONNX voices + local binary).

**Why:** Lightweight, CPU-friendly, no GPU required, fast synthesis (~200 ms target), and solid Hindi voices (`hi_IN-hemant-medium`). Coqui XTTS is heavier and slower for a fresher-day demo loop.

## 4. Language switch strategy

**Choice:** Update `current_lang` every turn from Whisper; inject language into a **fresh system message** each Ollama call; **never** reset `ConversationMemory` on switch.

**Why:** Evaluation scenarios require recalling facts (order 4421, hotel option, weather in three cities) after EN → HI → ES switches. Only the reply language hint changes; full `user`/`assistant` history is always sent.

## 5. Silence threshold: 1.2 seconds

**Choice:** `SILENCE_THRESHOLD_S = 1.2` with Silero VAD at 0.5 confidence.

**Why:** Balances not cutting off mid-sentence pauses vs. not waiting too long after the user stops. Shorter values feel snappy but truncate thoughtful speakers; longer values add dead air to every turn.

## 6. VAD chunk size: 512 samples (32 ms)

**Choice:** Fixed 512-sample blocks at 16 kHz (not 30 ms / 480 samples).

**Why:** Silero VAD v5 requires exactly 512 samples at 16 kHz; other sizes raise errors. Documented in config as `CHUNK_SAMPLES`.
