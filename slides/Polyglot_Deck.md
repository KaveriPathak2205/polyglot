# Polyglot — 5-Slide Deck
## Real-Time Multilingual Voice Agent (Case 11)

Copy each slide into PowerPoint / Google Slides (one section = one slide).

---

## SLIDE 1 — Title

**Polyglot**  
*Real-Time Multilingual Voice Agent*

- University Fresher Day Project — **Case 11**
- Speak naturally in **English, Hindi, or Spanish**
- Agent listens, understands, remembers, and replies in your language

*Your Name | Course | Date*

**Speaker note:** Open with a live demo line: “One assistant, many languages — no cloud APIs.”

---

## SLIDE 2 — Problem & Solution

### The challenge
- Voice assistants often **forget context** when the user switches language
- Cloud APIs cost money and need internet
- End-to-end voice loops must stay **fast** for natural conversation

### Our solution — Polyglot
- **100% local** pipeline on a laptop (open-source only)
- **One continuous loop:** Mic → VAD → Speech recognition → LLM → TTS → Speaker
- **Persistent memory** across language switches

**Speaker note:** Emphasize “fresher-friendly stack” — no paid keys, runs on student hardware.

---

## SLIDE 3 — System Architecture

```
  [Microphone]
       |
       v
  Silero VAD  -------- detect end of speech (~1.2s silence)
       |
       v
  faster-whisper ----- transcript + language code (e.g. hi, en, es)
       |
       v
  Ollama (Llama 3.2 3B) -- reply in SAME language + full chat history
       |
       v
  Piper TTS ------------ matched voice per language
       |
       v
  [Speaker]  --> loop
```

**Design principle:** Language changes every turn; **conversation memory never resets.**

---

## SLIDE 4 — Technology Stack & Performance

| Stage | Tool | Target latency |
|-------|------|----------------|
| Voice activity detection | Silero VAD | ~50 ms |
| Speech + language ID | faster-whisper | ~300 ms |
| Reasoning | Llama 3.2 3B (Ollama) | ~400 ms |
| Speech synthesis | Piper TTS | ~200 ms |
| Playback | sounddevice | ~100 ms |
| **Total (target)** | | **~1.05 s** |

**Stack:** Python CLI · silero-vad · faster-whisper · Ollama · Piper · sounddevice

**Speaker note:** Mention CPU-friendly choices (int8 Whisper, 3B model, ONNX VAD).

---

## SLIDE 5 — Highlights, Demo & Conclusion

### What makes Polyglot stand out
1. **Multilingual memory** — recalls order #4421 after EN → HI → EN switch  
2. **Language-aware replies** — system prompt updates; history stays intact  
3. **Fully offline** — privacy-friendly, no API keys  
4. **Measurable** — per-turn latency printed for evaluation  

### Demo scenarios tested
- **Scenario 1:** Order status (English → Hindi → English)  
- **Scenario 2:** Hotel options (Spanish → English recall)  
- **Scenario 4:** Weather in 3 cities → “Compare all three”  

### Thank you
**Questions?**  
*GitHub / demo video / live mic demo*

**Speaker note:** End with 30-second live demo if allowed.

---

## Optional backup slide (if Q&A)

**Limitations & future work**
- Hindi TTS uses `rohan` voice (hemant model unavailable on Hugging Face)
- CPU latency varies with hardware; GPU optional for Whisper
- Future: more languages, push-to-talk UI, web dashboard
