@echo off
REM ============================================================
REM Voice Input — Complete Launcher
REM Starts WSL pipeline + Windows recorder in one click.
REM Place shortcut in: Win+R → shell:startup → paste shortcut
REM ============================================================

echo Starting Voice Input Pipeline...

REM 1. Start WSL services (Ollama + Pipeline Watcher)
echo [1/2] Launching WSL services...
start "Voice-WSL" /MIN wsl bash /home/khlilo/Genesis_Workspace/voice-input/start_all.sh

REM 2. Wait for WSL to initialize
timeout /t 5 /nobreak > nul

REM 3. Start Windows recorder
echo [2/2] Launching Windows recorder...
start "Voice-Recorder" /MIN python C:\Users\31072\voice_recorder.py

echo Done. Press Ctrl+Shift+V to start recording.
