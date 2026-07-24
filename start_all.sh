#!/bin/bash
# ============================================================
# Voice Input — Single Command Launcher
# Run in WSL: bash start_all.sh
# Starts Ollama + Pipeline Watcher. Keeps running in background.
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/../.venv"
OLLAMA_LOG="/tmp/ollama.log"
PIPELINE_LOG="/tmp/voice_pipeline.log"

echo "=== Voice Input Pipeline Launcher ==="

# 1. Ensure venv
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "[ERROR] venv not found at $VENV_DIR"
    exit 1
fi
source "$VENV_DIR/bin/activate"

# 2. Start Ollama (if not running)
if ! pgrep -x ollama > /dev/null; then
    echo "[1/2] Starting Ollama..."
    nohup ollama serve &> "$OLLAMA_LOG" &
    sleep 3
    if pgrep -x ollama > /dev/null; then
        echo "       Ollama started (PID: $(pgrep -x ollama))"
    else
        echo "       [WARN] Ollama may have failed to start. Check $OLLAMA_LOG"
    fi
else
    echo "[1/2] Ollama already running (PID: $(pgrep -x ollama))"
fi

# 3. Kill any existing pipeline watcher
OLD_PID=$(pgrep -f "python3 voice_pipeline.py" 2>/dev/null || true)
if [ -n "$OLD_PID" ]; then
    echo "       Stopping old pipeline (PID: $OLD_PID)..."
    kill "$OLD_PID" 2>/dev/null || true
    sleep 1
fi

# 4. Start pipeline watcher
echo "[2/2] Starting pipeline watcher..."
cd "$SCRIPT_DIR"
HF_HUB_OFFLINE=1 nohup python3 voice_pipeline.py &> "$PIPELINE_LOG" &
sleep 2

NEW_PID=$(pgrep -f "python3 voice_pipeline.py" 2>/dev/null | head -1 || true)
if [ -n "$NEW_PID" ]; then
    echo "       Pipeline started (PID: $NEW_PID)"
else
    echo "       [WARN] Pipeline may have failed. Check $PIPELINE_LOG"
fi

echo ""
echo "=== Ready ==="
echo "Ollama log:   $OLLAMA_LOG"
echo "Pipeline log: $PIPELINE_LOG"
echo ""
echo "On Windows, start the recorder:"
echo "  python C:\\Users\\31072\\voice_recorder.py"
echo ""
echo "Use: Ctrl+Shift+V to toggle recording"
