"""Shared configuration for voice input pipeline.

Version: 1.1.0
"""
import os
from pathlib import Path

__version__ = "1.1.0"

# ── Paths ──────────────────────────────────────────────
# Shared between Windows host and WSL
# On Windows: C:\voice-input\
# On WSL:     /mnt/c/voice-input/
SHARED_DIR_WIN = Path("C:/voice-input")
SHARED_DIR_WSL = Path("/mnt/c/voice-input")
AUDIO_FILE = "input.wav"
MARKER_FILE = "ready.txt"
RESULT_FILE = "result.txt"  # WSL pipeline writes result, Windows recorder reads it

# ── Audio ──────────────────────────────────────────────
SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit
AUDIO_FORMAT = "wav"

# ── STT ────────────────────────────────────────────────
WHISPER_MODEL = "medium"  # faster-whisper model size (already cached)
WHISPER_LANGUAGE = "zh"
WHISPER_DEVICE = "cpu"  # CPU mode for WSL compatibility
WHISPER_COMPUTE_TYPE = "int8"  # int8 for CPU speed

# ── LLM ────────────────────────────────────────────────
OLLAMA_MODEL = "qwen2.5:7b"
OLLAMA_TIMEOUT = 15  # seconds
OLLAMA_SYSTEM_PROMPT = """仅修正以下文本的 ASR 转写错误和水词，输出修正后的文本。不改原意、不加内容、不回答。

输入：嗯那个我今天发现就是那个 voice input 这个东西啊其实挺好用的就是有时候它会因为口语化的关系导致虽然字面上是对的但表达上不太书面所以我就在想能不能再加一层 LLM 把它润色一下
输出：我今天发现 voice input 挺好用的，只是有时候因为口语化的关系，字面准确但表达不够书面。我在想能不能加一层 LLM 润色。

输入：帮我写一个函数计算两个数的和
输出：帮我写一个函数，计算两个数的和。

输入：我把那个文件放到 D 盘的 projects 文件夹里面了然后运行的时候报错说什么 module not found 我检查了路径是对的不对啊是路径是错的
输出：我把文件放到 D 盘 projects 文件夹里了，运行时报错 module not found。我检查了路径——不对，路径是错的。
"""

# ── Hotkey ──────────────────────────────────────────────
HOTKEY = "<ctrl>+<shift>+v"

# ── Recording ───────────────────────────────────────────
MAX_RECORD_SECONDS = 600  # safety cap (10 min for large projects)
