@echo off
REM =============================
REM NeuraFormAI Project Runner
REM =============================

REM 1️⃣ Activate virtual environment
call tts-venv\Scripts\activate

REM 2️⃣ Start backend server
start cmd /k "uvicorn app.main:app --reload"

REM 3️⃣ Launch frontend PyQt app
start cmd /k "python -m chat_ui.main"

REM 4️⃣ (Optional) Run unit tests
REM Uncomment next line if you want tests to run automatically
REM pytest tests/

echo.
echo ✅ Backend and UI started successfully!
pause
