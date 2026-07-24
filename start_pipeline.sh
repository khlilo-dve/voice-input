#!/bin/bash
# Start the voice pipeline watcher in WSL
# Run this in a WSL terminal, leave it running in background

VENV="/home/khlilo/Genesis_Workspace/.venv"
PROJECT="/home/khlilo/Genesis_Workspace/voice-input"

# Ensure Ollama is running
if ! pgrep -x ollama > /dev/null; then
    echo "Starting Ollama..."
    ollama serve &>/tmp/ollama.log &
    sleep 3
fi

cd "$PROJECT"
source "$VENV/bin/activate"
exec python3 voice_pipeline.py
