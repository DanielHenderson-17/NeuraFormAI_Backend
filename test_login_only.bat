@echo off
setlocal

call tts-venv\Scripts\activate
set PYTHONUNBUFFERED=1
python -m pip install --quiet python-dotenv requests google-auth-oauthlib
python scripts\test_login_only.py

echo.
echo (Press any key to close this window)
pause >nul
endlocal

