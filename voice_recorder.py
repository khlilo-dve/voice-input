#!/usr/bin/env python3
"""Windows voice recorder — global hotkey toggle, saves WAV to shared path.

Runs on Windows host (not WSL).
Dependencies: keyboard, PyAudio

Hotkey: Ctrl+Shift+V (toggle recording on/off)
"""
import logging
import subprocess
import sys
import threading
import time
import wave
from pathlib import Path

try:
    import pyaudio
except ImportError:
    sys.exit("Run: pip install PyAudio")

try:
    import keyboard
except ImportError:
    sys.exit("Run: pip install keyboard")

# ── Configuration ─────────────────────────────────────
SHARED_DIR = Path("C:/voice-input")
AUDIO_FILE = "input.wav"
MARKER_FILE = "ready.txt"
RESULT_FILE = "result.txt"
SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit
FORMAT = pyaudio.paInt16
CHUNK = 1024

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("voice_recorder")


def show_notification(title: str, message: str):
    """Show a Windows notification popup (auto-closes after 3s)."""
    try:
        ps = (
            f"(New-Object -ComObject WScript.Shell).Popup("
            f"'{message}', 3, '{title}', 0x40"
            f")"
        )
        subprocess.Popen(
            ["powershell", "-WindowStyle", "Hidden", "-Command", ps],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass  # notification is best-effort


class VoiceRecorder:
    def __init__(self):
        self.recording = False
        self.frames: list[bytes] = []
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.start_time = 0.0
        self._watching = False

        # Ensure shared directory exists
        SHARED_DIR.mkdir(parents=True, exist_ok=True)
        # Clean up stale files
        (SHARED_DIR / MARKER_FILE).unlink(missing_ok=True)
        (SHARED_DIR / AUDIO_FILE).unlink(missing_ok=True)
        (SHARED_DIR / RESULT_FILE).unlink(missing_ok=True)

    def start_recording(self):
        if self.recording:
            return
        self.frames = []
        self.start_time = time.time()
        self.recording = True

        def callback(in_data, frame_count, time_info, status):
            if self.recording:
                self.frames.append(in_data)
            return (in_data, pyaudio.paContinue)

        self.stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK,
            stream_callback=callback,
        )
        self.stream.start_stream()
        logger.info("RECORDING STARTED")

    def stop_recording(self):
        if not self.recording:
            return

        self.recording = False
        elapsed = time.time() - self.start_time

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        if elapsed < 0.5:
            logger.warning(f"Too short ({elapsed:.1f}s), discarded")
            self.frames = []
            return

        # Save WAV
        wav_path = SHARED_DIR / AUDIO_FILE
        with wave.open(str(wav_path), "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(SAMPLE_WIDTH)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(b"".join(self.frames))

        # Write marker to trigger WSL pipeline
        marker = SHARED_DIR / MARKER_FILE
        marker.write_text(f"{time.time()}\n{elapsed:.1f}\n")

        logger.info(f"RECORDING STOPPED ({elapsed:.1f}s) — processing...")
        self.frames = []

        # Start watching for WSL pipeline result
        self._start_result_watcher()

    def _start_result_watcher(self):
        """Background thread: poll for result file from WSL pipeline."""
        if self._watching:
            return
        self._watching = True

        def watch():
            result_path = SHARED_DIR / RESULT_FILE
            # Remove any stale result
            result_path.unlink(missing_ok=True)
            deadline = time.time() + 30  # 30s timeout
            while time.time() < deadline:
                if result_path.exists():
                    try:
                        content = result_path.read_text(encoding="utf-8").strip()
                        lines = content.split("\n")
                        status = lines[0] if lines else "unknown"
                        detail = lines[1] if len(lines) > 1 else ""
                        result_path.unlink(missing_ok=True)

                        if status.startswith("ok"):
                            mode = "LLM" if "llm" in status else "raw text"
                            show_notification("Voice Input ✓", f"Prompt ready ({mode})")
                            logger.info(f"NOTIFICATION: Prompt ready ({mode})")
                        elif status == "error":
                            show_notification("Voice Input ✗", detail or "Processing failed")
                            logger.error(f"NOTIFICATION: Error - {detail}")
                        break
                    except Exception as e:
                        logger.error(f"Result read error: {e}")
                        break
                time.sleep(0.5)
            else:
                logger.warning("Result timeout — WSL pipeline may have failed")
            self._watching = False

        t = threading.Thread(target=watch, daemon=True)
        t.start()

    def _handle_hotkey(self):
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def run(self):
        keyboard.add_hotkey("ctrl+shift+v", self._handle_hotkey, suppress=True)

        logger.info("=" * 50)
        logger.info("Voice Recorder Ready")
        logger.info("Hotkey: Ctrl + Shift + V")
        logger.info(f"Output: {SHARED_DIR / AUDIO_FILE}")
        logger.info("=" * 50)
        print()

        keyboard.wait()


if __name__ == "__main__":
    recorder = VoiceRecorder()
    recorder.run()
