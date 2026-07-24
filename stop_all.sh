#!/bin/bash
# Stop all voice input services in WSL

echo "=== Stopping Voice Input Services ==="

# Stop pipeline watcher
PIPE_PID=$(pgrep -f "python3 voice_pipeline.py" 2>/dev/null)
if [ -n "$PIPE_PID" ]; then
    kill $PIPE_PID 2>/dev/null && echo "[1/2] Pipeline stopped (PID: $PIPE_PID)" || echo "[1/2] Pipeline already stopped"
else
    echo "[1/2] Pipeline not running"
fi

# Stop Ollama (optional — comment out if you want to keep it)
# OLLAMA_PID=$(pgrep -x ollama)
# if [ -n "$OLLAMA_PID" ]; then
#     kill $OLLAMA_PID 2>/dev/null && echo "[2/2] Ollama stopped (PID: $OLLAMA_PID)"
# fi

# Clean shared files
rm -f /mnt/c/voice-input/*.txt /mnt/c/voice-input/*.wav 2>/dev/null
echo "Shared files cleaned"

echo "=== Done ==="
echo "Windows recorder: close its terminal window or Ctrl+C in that window"
