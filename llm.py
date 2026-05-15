"""Ollama chat wrapper with persistent conversation memory."""

import logging

import requests

from config import OLLAMA_MODEL, OLLAMA_TIMEOUT_S, OLLAMA_URL

logger = logging.getLogger(__name__)

_FALLBACK_REPLIES = {
    "en": "Sorry, I could not reach the language model. Please try again.",
    "hi": "माफ़ कीजिए, भाषा मॉडल से कनेक्ट नहीं हो पाया। कृपया फिर कोशिश करें।",
    "es": "Lo siento, no pude conectar con el modelo. Inténtalo de nuevo.",
}


def _system_prompt(lang_code: str) -> str:
    return (
        "You are a helpful multilingual voice assistant.\n"
        "CRITICAL RULES:\n"
        f"1. Always reply in the SAME language the user just spoke. "
        f"Current language: {lang_code}\n"
        "2. Keep replies SHORT — 1-3 sentences max (this is voice output)\n"
        "3. NEVER forget context from earlier in the conversation, "
        "even if the language changes\n"
        "4. If asked about something from a previous turn "
        '(e.g. "the second option"), refer back to it correctly.'
    )


class ConversationMemory:
    """Stores user/assistant turns; system prompt is rebuilt each call."""

    def __init__(self) -> None:
        self._messages: list[dict[str, str]] = []

    def add(self, role: str, content: str) -> None:
        self._messages.append({"role": role, "content": content})

    def get_history(self) -> list[dict[str, str]]:
        return list(self._messages)

    def reset(self) -> None:
        """Clear conversation history (system prompt is not stored here)."""
        self._messages.clear()


def chat(memory: ConversationMemory, user_text: str, lang_code: str) -> str:
    """
    Send user message + full history to Ollama; return assistant reply.

    Memory is updated only on success. System message includes current lang_code.
    """
    messages = [
        {"role": "system", "content": _system_prompt(lang_code)},
        *memory.get_history(),
        {"role": "user", "content": user_text},
    ]

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=OLLAMA_TIMEOUT_S,
        )
        response.raise_for_status()
        data = response.json()
        reply = data.get("message", {}).get("content", "").strip()
        if not reply:
            raise ValueError("Empty reply from Ollama")
    except (requests.RequestException, ValueError, KeyError) as exc:
        logger.error("Ollama request failed: %s", exc)
        return _FALLBACK_REPLIES.get(lang_code, _FALLBACK_REPLIES["en"])

    memory.add("user", user_text)
    memory.add("assistant", reply)
    return reply
