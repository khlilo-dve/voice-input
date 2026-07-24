#!/usr/bin/env python3
"""WSL pipeline orchestrator — watches for audio, runs STT→LLM→clipboard."""
import os
os.environ["HF_HUB_OFFLINE"] = "1"  # force offline before any HF imports

import logging
import subprocess
import sys
import time
from pathlib import Path

from config import SHARED_DIR_WSL, MARKER_FILE, AUDIO_FILE, RESULT_FILE
from stt_engine import transcribe
from llm_formatter import format_prompt, check_ollama_health

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("voice_pipeline")


def ensure_shared_dir() -> Path:
    d = SHARED_DIR_WSL
    d.mkdir(parents=True, exist_ok=True)
    return d


def set_clipboard(text: str) -> bool:
    """Write text to Windows clipboard with proper UTF-8 encoding."""
    tmp = SHARED_DIR_WSL / ".clipboard_tmp.txt"
    tmp.write_text(text, encoding="utf-8")
    win_path = "C:\\voice-input\\.clipboard_tmp.txt"
    ps_cmd = (
        f"$text = [System.IO.File]::ReadAllText('{win_path}', [System.Text.Encoding]::UTF8);"
        f"Set-Clipboard -Value $text"
    )
    try:
        proc = subprocess.run(
            ["powershell.exe", "-Command", ps_cmd],
            capture_output=True,
            timeout=5,
        )
        if proc.returncode != 0:
            logger.error(f"PowerShell clipboard error: {proc.stderr.decode()}")
            return False
        return True
    except Exception as e:
        logger.error(f"Clipboard write failed: {e}")
        return False


def write_result(status: str, detail: str = "") -> None:
    """Write result file that Windows recorder can read for notifications."""
    result = SHARED_DIR_WSL / RESULT_FILE
    content = f"{status}\n{detail}\n{time.time()}"
    result.write_text(content, encoding="utf-8")
    logger.info(f"Result written: {status} {detail}")


def process_audio() -> None:
    """Run the full pipeline: STT → LLM → Clipboard."""
    audio_path = SHARED_DIR_WSL / AUDIO_FILE

    if not audio_path.exists():
        logger.error(f"Audio file not found: {audio_path}")
        write_result("error", "Audio file not found")
        return

    # Step 1: STT
    try:
        chinese_text = transcribe(str(audio_path))
    except ValueError as e:
        logger.error(f"STT failed: {e}")
        write_result("error", str(e))
        return
    except Exception as e:
        logger.error(f"STT unexpected error: {e}")
        write_result("error", "Transcription error")
        return

    logger.info(f"STT result: {chinese_text}")

    # Step 2: LLM polishing
    if check_ollama_health():
        formatted = format_prompt(chinese_text)
    else:
        logger.warning("Ollama not available, using raw text")
        formatted = chinese_text

    # Step 3: Clipboard
    if set_clipboard(formatted):
        status = "ok_llm" if formatted != chinese_text else "ok_raw"
        preview = formatted[:100].replace("\n", " ") + "..."
        write_result(status, preview)
        logger.info("Pipeline complete — prompt in clipboard")
    else:
        fallback = SHARED_DIR_WSL / "output.txt"
        fallback.write_text(formatted, encoding="utf-8")
        logger.warning(f"Clipboard failed, saved to {fallback}")
        write_result("error", f"Saved to {fallback}")


def watch_loop() -> None:
    """Poll for marker files and process when found."""
    ensure_shared_dir()
    logger.info(f"Watching {SHARED_DIR_WSL} for {MARKER_FILE}...")
    logger.info("Press Ctrl+C to stop.")
    if check_ollama_health():
        logger.info("Ollama: connected")
    else:
        logger.warning("Ollama: not available (run 'ollama serve' in another terminal)")

    marker = SHARED_DIR_WSL / MARKER_FILE
    audio = SHARED_DIR_WSL / AUDIO_FILE
    result = SHARED_DIR_WSL / RESULT_FILE

    # Clean stale result
    result.unlink(missing_ok=True)

    while True:
        if marker.exists():
            logger.info("Marker detected, processing...")
            time.sleep(0.3)
            process_audio()
            # Cleanup input
            marker.unlink(missing_ok=True)
            audio.unlink(missing_ok=True)
            logger.info("Ready for next recording.")

        time.sleep(0.5)


if __name__ == "__main__":
    try:
        watch_loop()
    except KeyboardInterrupt:
        logger.info("Pipeline watcher stopped.")
        sys.exit(0)
