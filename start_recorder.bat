@echo off
REM ============================================================
REM Voice Recorder — Windows Startup Launcher
REM Place shortcut to this file in shell:startup folder:
REM   Win+R → shell:startup → paste shortcut
REM ============================================================
cd /d C:\Users\31072
start "Voice Recorder" /MIN python voice_recorder.py
