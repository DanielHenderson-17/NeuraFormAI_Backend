@echo off
REM =============================
REM NeuraFormAI Project Runner
REM =============================

REM 2️⃣ Activate virtual environment
call tts-venv\Scripts\activate

REM 3️⃣ Start backend server
start cmd /k "uvicorn app.main:app --reload"

REM 4️⃣ Launch frontend PyQt app with Chromium flags
@REM start cmd /k "python launch.py"

REM 5️⃣ (Optional) Run unit tests
REM Uncomment next line if you want tests to run automatically
REM pytest tests/

echo.
echo ✅ Backend and UI started successfully!
pause
