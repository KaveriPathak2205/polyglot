"""Smoke tests for Polyglot modules (no mic / Piper required for most)."""

import sys


def test_config() -> None:
    from config import CHUNK_SAMPLES, get_piper_model, resolve_path

    assert CHUNK_SAMPLES == 512
    path, fallback = get_piper_model("en")
    assert path.endswith(".onnx")
    assert fallback is False
    _, fallback = get_piper_model("fr")
    assert fallback is True
    print("config: OK")


def test_memory() -> None:
    from llm import ConversationMemory, _system_prompt

    mem = ConversationMemory()
    assert mem.get_history() == []
    mem.add("user", "hello")
    mem.add("assistant", "hi")
    assert len(mem.get_history()) == 2
    mem.reset()
    assert mem.get_history() == []
    assert "hi" in _system_prompt("hi")
    print("memory: OK")


def test_vad_chunk_validation() -> None:
    import numpy as np

    from config import CHUNK_SAMPLES
    from vad import is_speech, load_vad, warmup

    model = load_vad()
    warmup(model)
    chunk = np.zeros(CHUNK_SAMPLES, dtype=np.float32)
    result = is_speech(model, chunk)
    assert isinstance(result, bool)
    print(f"vad: OK (silence check returned speech={result})")


def main() -> int:
    tests = [test_config, test_memory, test_vad_chunk_validation]
    failed = 0
    for test in tests:
        try:
            test()
        except Exception as exc:
            print(f"{test.__name__}: FAILED — {exc}", file=sys.stderr)
            failed += 1
    if failed:
        print(f"\n{failed} test(s) failed")
        return 1
    print("\nAll smoke tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
