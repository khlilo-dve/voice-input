"""LLM formatter using local Ollama Qwen2.5."""
import logging
import requests
import json
from config import OLLAMA_MODEL, OLLAMA_TIMEOUT, OLLAMA_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

OLLAMA_API = "http://localhost:11434/api/chat"


def format_prompt(chinese_text: str) -> str:
    """Convert Chinese coding instruction to structured English prompt.

    Args:
        chinese_text: Raw Chinese transcription from STT.

    Returns:
        Structured English prompt ready for Claude Code.
        Falls back to raw Chinese text on any error.
    """
    logger.info(f"Formatting with {OLLAMA_MODEL}: {chinese_text[:60]}...")

    # Quick sanity: if the text is a single word or gibberish, skip LLM call
    if len(chinese_text.strip()) < 4:
        logger.warning("Text too short for LLM formatting, returning raw")
        return chinese_text

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": OLLAMA_SYSTEM_PROMPT},
            {"role": "user", "content": chinese_text},
        ],
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 2048,
        },
    }

    try:
        resp = requests.post(
            OLLAMA_API,
            json=payload,
            timeout=OLLAMA_TIMEOUT,
        )
        resp.raise_for_status()
        result = resp.json()
        formatted = result["message"]["content"].strip()
        logger.info(f"Formatted ({len(formatted)} chars): {formatted[:80]}...")
        return formatted

    except requests.exceptions.ConnectionError:
        logger.error("Ollama not running. Start with: ollama serve")
        return chinese_text
    except requests.exceptions.Timeout:
        logger.error(f"Ollama timeout after {OLLAMA_TIMEOUT}s")
        return chinese_text
    except Exception as e:
        logger.error(f"LLM formatting failed: {e}")
        return chinese_text


def check_ollama_health() -> bool:
    """Check if Ollama is running and model is available."""
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=5)
        resp.raise_for_status()
        models = [m["name"] for m in resp.json().get("models", [])]
        available = any(OLLAMA_MODEL in m for m in models)
        if not available:
            logger.warning(f"{OLLAMA_MODEL} not found in Ollama models: {models}")
        return available
    except Exception:
        return False
