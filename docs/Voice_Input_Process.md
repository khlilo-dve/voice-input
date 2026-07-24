# Voice Input — 全流程文档

**最后更新**: 2026-07-24
**版本**: v1.0

---

## 1. 概述

本地 AI 语音输入管线。说中文 → 自动转写 → LLM 格式化为结构化英文 prompt → 注入剪贴板。全链路离线，零数据上云。

**一句话**：按快捷键，说话，再按一次，等通知，粘贴。

### 适用场景

| 场景 | 效果 |
|------|------|
| 日常小改动 | 说完 2-3 秒拿到结果 |
| 中等重构需求 | STT + LLM 格式化，10-15 秒 |
| 大型项目描述（千字） | 支持 10 分钟录音，LLM 输出 2000+ tokens |

### 技术栈

```
faster-whisper (medium, CPU/int8)
        ↓
Ollama Qwen2.5:7B (Q4_K_M, ~4.5GB VRAM)
        ↓
Prompt Formatter (结构化输出)
        ↓
PowerShell UTF-8 (剪贴板注入)
```

**VRAM 占用**：峰值 ~5GB（STT 和 LLM 串行跑，不同时占用）

---

## 2. 架构

```
┌── Windows 侧 ──────────────────────┐
│                                     │
│  start_everything.bat               │
│       ↓                             │
│  voice_recorder.py (后台常驻)        │
│    · keyboard 全局热键 Ctrl+Shift+V  │
│    · PyAudio 麦克风采集 16kHz mono   │
│    · 写 WAV → C:\voice-input\       │
│    · 轮询 result.txt → 弹通知        │
│                                     │
├── 共享文件系统 ─────────────────────┤
│  C:\voice-input\  ←→  /mnt/c/voice-input/ │
│    input.wav                        │
│    ready.txt  (Windows → WSL 触发)   │
│    result.txt (WSL → Windows 通知)   │
│                                     │
├── WSL 侧 ──────────────────────────┤
│                                     │
│  start_all.sh                       │
│       ↓                             │
│  Ollama serve (常驻)                 │
│       +                             │
│  voice_pipeline.py (常驻守护)        │
│    · 轮询 ready.txt                 │
│    · stt_engine.py → 中文转写        │
│    · llm_formatter.py → 结构化格式化  │
│    · 写剪贴板 + result.txt           │
│                                     │
└─────────────────────────────────────┘
```

---

## 3. 一次性安装

### 3.1 WSL: Ollama + 模型

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:7b
```

模型大小 ~4.7GB，下载一次。

### 3.2 Windows: 录音依赖

```powershell
pip install keyboard PyAudio
```

### 3.3 复制文件到 Windows

```powershell
copy "\\wsl$\Ubuntu\home\khlilo\Genesis_Workspace\voice-input\voice_recorder.py" C:\Users\31072\
copy "\\wsl$\Ubuntu\home\khlilo\Genesis_Workspace\voice-input\start_everything.bat" C:\Users\31072\
```

### 3.4 WSL venv 验证

```bash
source Genesis_Workspace/.venv/bin/activate
python3 -c "from faster_whisper import WhisperModel; print('OK')"
python3 -c "import requests; print('OK')"
```

---

## 4. 日常使用

### 快速启动（推荐）

双击 `C:\Users\31072\start_everything.bat`。

做了什么：
1. 拉起 WSL 管线（Ollama + 守护进程），窗口自动最小化
2. 拉起 Windows 录音客户端，窗口自动最小化
3. 两个窗口都在后台跑，不需要管

### 开机自启（可选）

```powershell
explorer shell:startup
```

把 `start_everything.bat` 的快捷方式拖进去。之后开机自动启动全部服务。

### 使用流程

```
1.  Ctrl+Shift+V        → 录音开始
2.  说中文指令            → 想说什么说什么
3.  Ctrl+Shift+V        → 录音停止，自动处理
4.  等通知"Prompt ready" → 3-15 秒（取决于音频长度）
5.  Ctrl+V              → 粘贴结构化 prompt 到 Claude Code
```

### 示例

**输入（说）**：
> "帮我把用户表加一个 last_login 字段，同时更新所有相关的查询接口，注意索引和迁移脚本"

**输出（粘贴到 Claude Code）**：
```
Add last_login field to user table with index and migration

## Tasks
1. Create database migration adding last_login timestamp column to users table.
2. Add database index on last_login for query performance.
3. Update all user query interfaces to include last_login in SELECT and response DTOs.
4. Add unit tests verifying migration rollback and query correctness.

## Context & Constraints
- Must include index for performance.
- Migration must be reversible (add rollback script).

## Before Coding
- Inspect current users table schema and existing migrations.
- List all query interfaces that reference the users table.

---
Reply in Simplified Chinese (简体中文).
```

---

## 5. 交互模型

| 操作 | 反馈 | 说明 |
|------|------|------|
| 按 Ctrl+Shift+V | 控制台打印 `RECORDING STARTED` | 开始录音 |
| 正在说话 | 无反馈 | 想停就再按 |
| 再按 Ctrl+Shift+V | 控制台打印 `RECORDING STOPPED — processing...` | 自动进入管线 |
| 等待处理 | - | STT + LLM |
| 通知弹窗 | `Voice Input ✓ — Prompt ready (LLM)` | 结果已入剪贴板 |
| Ctrl+V | 结构化 prompt 粘贴 | 直接用 |

**注意事项**：
- 录音 <0.5 秒自动丢弃
- 热键抑制（Ctrl+Shift+V 不会在别的窗口触发粘贴）
- 如果 Ollama 挂了，降级为原始中文文本入剪贴板

---

## 6. 文件结构

```
Genesis_Workspace/voice-input/
├── config.py                  # 共享配置（模型、路径、参数）
├── stt_engine.py              # faster-whisper 转写
├── llm_formatter.py           # Ollama LLM 格式化
├── voice_pipeline.py          # WSL 管线编排器（守护进程）
├── voice_recorder.py          # Windows 录音客户端（守护进程）
├── start_all.sh               # WSL 一键启动（Ollama + 管线）
├── start_everything.bat       # Windows 一键启动（WSL + 录音端）
├── start_recorder.bat         # 仅录音端启动
├── requirements_windows.txt   # Windows Python 依赖
├── install_windows.ps1        # Windows 安装脚本
├── README.md                  # 快速参考
└── docs/
    └── Voice_Input_Process.md # 本文档
```

## 7. 配置速查

| 参数 | 值 | 位置 | 说明 |
|------|-----|------|------|
| 热键 | Ctrl+Shift+V | voice_recorder.py | 可改 |
| 录音格式 | 16kHz mono 16-bit WAV | voice_recorder.py | - |
| 录音上限 | 600s | config.py | 10 分钟 |
| 录音最短 | 0.5s | voice_recorder.py | 少于丢弃 |
| STT 模型 | faster-whisper medium | config.py | CPU/int8 |
| STT 语言 | zh | config.py | 中文 |
| LLM 模型 | qwen2.5:7b | config.py | Q4_K_M |
| LLM 输出上限 | 2048 tokens | llm_formatter.py | - |
| LLM 超时 | 15s | config.py | 超时降级 |
| 共享目录 | C:\voice-input\ | 两端都用 | WSL 自动映射 |

---

## 8. 故障排查

### 热键没反应

1. `voice_recorder.py` 在运行吗？看有没有控制台窗口
2. 在录音窗口里看有没有打印 `RECORDING STARTED`
3. 别的软件有没有占用 Ctrl+Shift+V

### 转录乱码

1. 确认 WSL 管线在运行：`pgrep -f voice_pipeline`
2. 检查管线日志：`tail -30 /tmp/voice_pipeline.log`
3. 如果卡在 `Loading faster-whisper model`：网络问题导致 HuggingFace 检查卡住，重启管线即可（已设置 `HF_HUB_OFFLINE=1`）

### 没有通知

1. 管线是否处理完成？看 `/tmp/voice_pipeline.log`
2. 如果日志里有 `Result written: ok_llm` 但没有弹窗：Windows 端轮询可能超时（30s），检查 STT + LLM 总耗时
3. 慢的话降低录音时长或用 medium 更小变体

### Ollama 不可用

```bash
# WSL 里手动启动
ollama serve &
ollama list | grep qwen2.5
```

如果模型没了：`ollama pull qwen2.5:7b`

### 剪贴板中文乱码

已通过 PowerShell UTF-8 方式修复。如果仍出现，检查 WSL 能否执行 `powershell.exe`：

```bash
powershell.exe -Command "Write-Host test"
```

### 录音端 PyAudio 安装失败

```powershell
# PyAudio 在 Windows 上需要预编译 wheel
pip install pipwin
pipwin install pyaudio
```

---

## 9. 性能特征

| 音频长度 | STT 耗时 | LLM 耗时 | 总等待 |
|----------|---------|---------|--------|
| 5s | ~1s | ~2s | ~3s |
| 30s | ~5s | ~3s | ~8s |
| 60s | ~10s | ~4s | ~14s |
| 300s (5min) | ~50s | ~6s | ~56s |
| 600s (10min) | ~100s | ~8s | ~108s |

*基于 CPU i7-13700K 等效性能估算，实际因硬件而异。medium 模型，CPU int8 量化。*

---

## 10. 已知限制

1. **单次录音上限 10 分钟** — 超过自动丢弃
2. **中文→英文翻译** — LLM prompt 是英文，但 Agent 回复可中文（已追加指令）
3. **无实时预览** — 必须等处理完才知道转写结果
4. **单声道** — 只有一个麦克风输入
5. **CPU STT** — WSL 的 CUDA 暂未配置，纯 CPU 推理。如切到 GPU 可将 STT 耗时减半
6. **无唤醒词** — 必须手动按快捷键
