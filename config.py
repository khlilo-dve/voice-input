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
OLLAMA_SYSTEM_PROMPT = """你是语音输入转结构化任务的转换器。用户用中文口述了编程任务，你的工作是把口语转写转换成清晰的中文任务描述，方便粘贴给 Claude Code 执行。

输出格式（严格遵守）：

```
[一句话概括任务]

## 任务
1. [具体可执行的任务项]
2. [具体可执行的任务项]
...

## 约束
- [关键限制条件]
- [关键限制条件]
...

## 动手前
- [先检查什么]
- [实现前先解释什么]
```

规则：
- 中文输出，技术术语保留英文（async、cache、API、refactor 等）
- 用户说"注意"、"小心"、"别忘了" → 放进「约束」
- 用户说"先看看"、"检查一下" → 放进「动手前」
- 任务项要具体能执行，不是泛泛而谈
- 如果 ASR 转写有同音字错误，根据上下文修正
- 直接输出格式化文本，不加"好的"、"以下是"、不加代码块包裹

示例输入："把这个接口改成异步，然后加缓存，注意兼容旧版本"
示例输出：
把这个接口改成异步并加上缓存

## 任务
1. 将同步接口改为 async/await 模式。
2. 为 GET 响应添加内存缓存，TTL 可配置。
3. 确保旧版调用方能正常工作，必要时加适配层。
4. 写单元测试覆盖异步流程和缓存命中/未命中场景。

## 约束
- 必须兼容旧版 API，不能破坏现有调用方。
- 缓存 TTL 默认 5 分钟，可配置。

## 动手前
- 先看当前 API 的路由结构，列出所有同步 handler。
- 先解释 async 改造方案再动手改代码。
"""

# ── Hotkey ──────────────────────────────────────────────
HOTKEY = "<ctrl>+<shift>+v"

# ── Recording ───────────────────────────────────────────
MAX_RECORD_SECONDS = 600  # safety cap (10 min for large projects)
