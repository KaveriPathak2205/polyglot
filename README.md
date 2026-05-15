# Polyglot — Real-Time Multilingual Voice Agent

Case 11 fresher-day project: a Python CLI that listens on the microphone, detects end-of-speech with VAD, transcribes and detects language with Whisper, replies via a local Llama 3.2 3B (Ollama), and speaks back with Piper TTS in the matching voice.

## Architecture

```
Mic → Silero VAD → faster-whisper → Ollama (Llama 3.2 3B) → Piper TTS → Speaker
         ↑___________________________________________________________|
                              continuous loop
```

## Requirements

- Python 3.10+
- Microphone and speakers
- [Ollama](https://ollama.com/) with `llama3.2:3b`
- [Piper](https://github.com/rhasspy/piper/releases) binary + voice models

## Quick start

```bash
cd polyglot
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS
pip install -r requirements.txt

ollama pull llama3.2:3b
ollama serve                    # if not already running

python main.py
```

Speak after you see `Listening...`. Press **Ctrl+C** to quit.

## Piper setup

1. Download the Piper binary for your OS from [Piper releases](https://github.com/rhasspy/piper/releases).
   - Windows: place `piper.exe` in the `polyglot/` folder (next to `main.py`).
   - Linux/macOS: place `piper` in the project root and run `chmod +x ./piper`.
2. Download voice models (each needs **both** `.onnx` and `.onnx.json`):

   | Language | File |
   |----------|------|
   | English  | `en_US-amy-medium.onnx` |
   | Hindi    | `hi_IN-rohan-medium.onnx` (hemant is not published; rohan is the HF Hindi medium voice) |
   | Spanish  | `es_ES-mls_9972-low.onnx` |

3. Put all `.onnx` and `.onnx.json` files in `polyglot/models/`.
4. Paths are configured in `config.py` under `PIPER_MODELS`.

## Project layout

```
polyglot/
├── main.py           # main loop + latency logging
├── vad.py            # Silero VAD
├── asr.py            # faster-whisper ASR + language ID
├── llm.py            # Ollama chat + conversation memory
├── tts.py            # Piper TTS router
├── audio.py          # mic capture + playback
├── config.py         # thresholds, model paths
├── requirements.txt
├── DECISIONS.md
└── models/           # Piper .onnx voices (user-downloaded)
```

## Latency budget

| Stage        | Tool              | Target   |
|--------------|-------------------|----------|
| VAD          | Silero            | ~50ms    |
| ASR          | faster-whisper    | ~300ms   |
| LLM          | Llama 3.2 3B      | ~400ms   |
| TTS          | Piper             | ~200ms   |
| Audio play   | sounddevice       | ~100ms   |
| **Total**    |                   | **~1050ms** |

Each turn prints: `[Latency] ASR: … | LLM: … | TTS: … | Total: …`

*(ASR line includes listen + transcribe time.)*

## Evaluation scenarios

Run `python main.py` and speak these in order.

### Scenario 1 — Order status (EN → HI → EN)

1. EN: "Hi, I need to check the status of my order. The order ID is 4421."
2. EN: "Yes, the email is rahul@example.com."
3. HI: "Theek hai, lekin delivery kal tak ho jaayegi kya?"
4. HI: (follow-up if needed)
5. EN: "Can you confirm the order number again?"

**Pass:** Agent still knows order **4421** and **rahul@example.com** after Hindi turns.

### Scenario 2 — Hotels (ES → EN)

1. ES: Describe two hotel options; ask which is better.
2. ES: Follow-up about the second option.
3. EN: "Which was the second hotel option you mentioned?"

**Pass:** Agent recalls the **second hotel** from Spanish context.

### Scenario 4 — Weather (rapid language switches)

1. EN: Ask weather in London.
2. HI: Ask weather in Mumbai.
3. ES: Ask weather in Madrid.
4. EN: "Compare all three."

**Pass:** Agent consolidates all three prior answers.

## Configuration

Edit `config.py`:

- `WHISPER_MODEL` — `base` (default) or `small` for accuracy
- `WHISPER_DEVICE` — `cpu` or `cuda`
- `SILENCE_THRESHOLD_S` — end-of-utterance silence (default `1.2`)
- `VAD_THRESHOLD` — speech confidence (default `0.5`)

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `OSError WinError 127` / `torchaudio` on startup | Use the **polyglot venv** (see below), not another course project's Python. Run `pip install silero-vad onnxruntime`. VAD loads via ONNX, not `torch.hub`. |
| `Connection refused` on Ollama | Run `ollama serve` and `ollama pull llama3.2:3b` |
| Piper model not found | Download `.onnx` + `.onnx.json` into `models/` |
| No microphone | Check `python -c "import sounddevice; print(sounddevice.query_devices())"` |
| Slow ASR on CPU | Use `WHISPER_MODEL = "tiny"` or enable `cuda` |
| Wrong reply language | Whisper sets `current_lang`; system prompt forces same language |

### Use the project virtual environment (important on Windows)

If `python main.py` uses packages from another folder (e.g. `Text_to_Speech_WebApp\Lib`), create a dedicated venv:

```powershell
cd C:\Users\utpal\polyglot
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Confirm the venv is active: `where python` should point to `polyglot\.venv\Scripts\python.exe`.

## License

Open-source stack only — no paid APIs. See component licenses (Whisper, Silero, Ollama, Piper).
