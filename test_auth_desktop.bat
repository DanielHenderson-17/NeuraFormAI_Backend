@echo off
setlocal

REM Activate venv and run the desktop auth tester
call tts-venv\Scripts\activate
set PYTHONUNBUFFERED=1
python -m pip install --quiet python-dotenv requests google-auth-oauthlib
python scripts\test_auth_endpoints_desktop.py

endlocal
echo.
echo (Press any key to close this window)
pause >nul

