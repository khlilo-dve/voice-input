# 🎙️ Voice Input for Claude Code

> Speak Chinese → structured English coding prompt in your clipboard. Fully local. Zero cloud.

**Version**: 1.0.0 | **License**: MIT

---

## Demo

Press hotkey, speak, release — 15 seconds later, paste a structured prompt:

```
Input (spoken Chinese):  "把这个接口改成异步，然后加缓存，注意兼容旧版本"

Output (clipboard):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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

---
Reply in Simplified Chinese (简体中文).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Architecture

```
┌── Windows ──────────────────────┐      ┌── WSL ─────────────────────────┐
│                                  │      │                                 │
│  Ctrl+Shift+V  →  Record Mic    │      │  faster-whisper medium → STT    │
│       ↓                         │      │           ↓                     │
│  Save WAV to shared path ───────┼──────┼→ Ollama Qwen2.5:7B → Format    │
│                                  │      │           ↓                     │
│  Poll result ← Notification ────┼──────┼─ Set Clipboard (UTF-8)          │
│                                  │      │                                 │
└──────────────────────────────────┘      └─────────────────────────────────┘
```

All data stays local. No API keys. No network after model download.

---

## Quick Start

### Prerequisites

- Windows 10/11 with WSL2
- NVIDIA GPU (8GB+ VRAM recommended) or CPU with 16GB+ RAM
- Python 3.12+

### 1. WSL: Install Ollama & Model

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:7b
```

### 2. WSL: Install Python Dependencies

```bash
cd voice-input
python3 -m venv ../.venv
source ../.venv/bin/activate
pip install faster-whisper requests
```

### 3. Windows: Install Recorder Dependencies

```powershell
pip install keyboard PyAudio
```

### 4. Copy Recorder to Windows

```powershell
copy "\\wsl$\Ubuntu\home\<user>\voice-input\voice_recorder.py" C:\Users\<you>\
copy "\\wsl$\Ubuntu\home\<user>\voice-input\start_everything.bat" C:\Users\<you>\
```

### 5. Launch

Double-click `C:\Users\<you>\start_everything.bat` — or run:

```powershell
wsl bash /home/<user>/voice-input/start_all.sh
start /MIN python C:\Users\<you>\voice_recorder.py
```

### 6. Use

| Action | Result |
|--------|--------|
| **Ctrl+Shift+V** | Start recording |
| Speak Chinese | Your coding instruction |
| **Ctrl+Shift+V** | Stop & auto-process |
| Wait for notification | "Prompt ready" |
| **Ctrl+V** | Paste structured prompt |

---

## How It Works

### Pipeline Stages

```
Hotkey Toggle (keyboard library, suppress=True)
    ↓
PyAudio Capture → 16kHz mono 16-bit WAV
    ↓
→ C:\voice-input\input.wav (shared filesystem)
    ↓
inotify-poll detects ready.txt
    ↓
faster-whisper medium (CPU/int8, beam=3, VAD filter)
    ↓
Ollama Qwen2.5:7B (Q4_K_M, 2048 max tokens)
    ↓
PowerShell Set-Clipboard (UTF-8)
    ↓
result.txt triggers Windows notification
```

### Graceful Degradation

| Failure | Fallback |
|---------|----------|
| Ollama not running | Raw Chinese text → clipboard |
| LLM timeout (15s) | Raw Chinese text → clipboard |
| STT empty / no speech | Notification: "No speech detected" |
| Clipboard fails | Save to `C:\voice-input\output.txt` |

---

## File Map

```
voice-input/
├── config.py                  # All settings: models, paths, prompts
├── stt_engine.py              # faster-whisper wrapper
├── llm_formatter.py           # Ollama Qwen2.5 formatter
├── voice_pipeline.py          # WSL watcher + orchestrator
├── voice_recorder.py          # Windows hotkey + mic client
├── start_all.sh               # WSL launcher (Ollama + pipeline)
├── stop_all.sh                # Graceful shutdown
├── start_everything.bat       # Windows one-click launcher
├── start_recorder.bat         # Windows recorder-only launcher
├── install_windows.ps1        # Windows dependency installer
├── requirements_windows.txt   # Windows pip dependencies
├── VERSION                    # 1.0.0
├── LICENSE                    # MIT
└── docs/
    └── Voice_Input_Process.md # Full documentation
```

---

## Configuration

Edit `config.py`:

```python
# ── STT ──────────────────────────
WHISPER_MODEL = "medium"          # tiny/base/small/medium/large-v3
WHISPER_LANGUAGE = "zh"           # Language code
WHISPER_DEVICE = "cpu"            # "cpu" or "cuda"

# ── LLM ─────────────────────────
OLLAMA_MODEL = "qwen2.5:7b"      # Any Ollama model
OLLAMA_TIMEOUT = 15               # Seconds before fallback
OLLAMA_SYSTEM_PROMPT = """..."""  # Customize output format

# ── Recording ───────────────────
MAX_RECORD_SECONDS = 600          # 10 minutes
HOTKEY = "<ctrl>+<shift>+v"       # Change in voice_recorder.py
```

---

## VRAM Budget

| Component | Memory |
|-----------|--------|
| faster-whisper medium | ~1.5 GB |
| Qwen2.5:7B Q4_K_M | ~4.5 GB |
| **Peak** (sequential) | **~5 GB** |

Works on 8GB VRAM GPUs. Purely CPU mode needs ~16GB system RAM.

---

## Performance

| Audio | STT | LLM | Total |
|-------|-----|-----|-------|
| 5s | ~1s | ~2s | ~3s |
| 30s | ~5s | ~3s | ~8s |
| 5min | ~50s | ~6s | ~56s |

*CPU i7-class, faster-whisper medium int8. GPU cuts STT time ~50%.*

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Hotkey not working | Is `voice_recorder.py` running? Check console. |
| Garbled Chinese text | `powershell.exe` must be reachable from WSL. |
| "Ollama not available" | `ollama serve` in WSL terminal. |
| STT stuck at loading | `export HF_HUB_OFFLINE=1` (already set in pipeline). |
| No notification | Check `/tmp/voice_pipeline.log` for errors. |
| PyAudio install fails | `pip install pipwin && pipwin install pyaudio` |

---

## Roadmap

- [ ] GPU-accelerated STT (CUDA in WSL)
- [ ] Real-time streaming transcription
- [ ] Wake word detection ("Hey Claude")
- [ ] Multi-language STT (auto-detect)
- [ ] System tray GUI for Windows recorder
- [ ] Configurable hotkey from config file

---

## Credits

Built by [khlilo](https://github.com/khlilo). Powered by:
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- [Ollama](https://ollama.com)
- [Qwen2.5](https://github.com/QwenLM/Qwen2.5)

---

[MIT License](LICENSE)
