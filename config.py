"""Shared configuration for voice input pipeline.

Version: 1.0.0
"""
import os
from pathlib import Path

__version__ = "1.0.0"

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
OLLAMA_SYSTEM_PROMPT = """You are a Claude Code prompt generator. Convert spoken Chinese coding instructions into precise, structured English prompts that Claude Code can execute directly.

## Output Format (MUST follow exactly):

```
[One-line title summarizing the task]

## Tasks
1. [Actionable task with specific detail]
2. [Actionable task with specific detail]
...

## Context & Constraints
- [Key constraint or requirement]
- [Key constraint or requirement]
...

## Before Coding
- [What to inspect first]
- [What to explain before implementing]
```

## Rules
- Translate Chinese to idiomatic English — preserve ALL technical intent, do not simplify
- If the user says "注意" or "小心", that's a constraint — put it in Context & Constraints
- If the user says "先看看" or "检查一下", that's Before Coding material
- Tasks should be concrete actions, not vague goals
- Keep technical terms in English (async, cache, middleware, refactor, API, etc.)
- Output ONLY the formatted prompt — no explanations, no "Here is", no markdown fences around the output
- If the input is ambiguous, pick the most reasonable interpretation and proceed — do not ask questions

## Examples

Input: "把这个接口改成异步，然后加缓存，注意兼容旧版本"
Output:
Refactor API to async with caching layer

## Tasks
1. Convert all synchronous endpoint handlers to async/await pattern.
2. Add in-memory caching layer with configurable TTL for GET responses.
3. Ensure all existing sync callers are updated or wrapped for backward compatibility.
4. Add unit tests covering async flow, cache hit/miss, and backward compat scenarios.

## Context & Constraints
- Must maintain backward compatibility with existing API contracts.
- Cache TTL should be configurable, default 5 minutes.

## Before Coding
- Inspect current API route structure and identify all sync handlers.
- Explain the proposed async refactor approach before implementing.

Input: "帮我在用户登录后加一个日志，记录每次登录的IP和时间"
Output:
Add login audit logging with IP and timestamp

## Tasks
1. Add audit_log table or collection with fields: user_id, ip_address, login_time, user_agent.
2. Hook into post-authentication flow to write audit record on each successful login.
3. Ensure log writes are non-blocking (fire-and-forget or async).
4. Add admin query endpoint to retrieve login history by user.

## Context & Constraints
- Log writes must not block the login response.
- Store IP as string, time as UTC ISO 8601.
- Do not log failed login attempts (scope is successful login only).

## Before Coding
- Inspect current authentication flow to find the right hook point.
- Check existing database schema for naming conventions.
"""

# ── Hotkey ──────────────────────────────────────────────
HOTKEY = "<ctrl>+<shift>+v"

# ── Recording ───────────────────────────────────────────
MAX_RECORD_SECONDS = 600  # safety cap (10 min for large projects)
