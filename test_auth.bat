@echo off
setlocal

REM Activate venv and run the auth tester
call tts-venv\Scripts\activate
python -m pip install --quiet python-dotenv requests
python scripts\test_auth_endpoints.py

endlocal

