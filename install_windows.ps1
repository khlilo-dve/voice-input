# Run on Windows host to install recording client dependencies
Write-Host "Installing voice recorder dependencies..." -ForegroundColor Green
pip install pynput PyAudio
Write-Host "Done. Run: python voice_recorder.py" -ForegroundColor Green
