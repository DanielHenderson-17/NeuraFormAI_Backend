@echo off
REM =============================
REM Run Flutter Frontend (Windows)
REM =============================

REM Ensure Flutter is on PATH (uses local clone at C:\Users\Daniel\flutter)
set PATH=%PATH%;C:\Users\Daniel\flutter\bin

REM Move into Flutter project
cd /d %~dp0\flutter_frontend

echo 🔧 Checking Flutter installation...
flutter --version
if %errorlevel% neq 0 (
    echo ❌ Flutter not found or not working
    pause
    exit /b 1
)

echo 🔧 Resolving Flutter dependencies...
flutter pub get
if %errorlevel% neq 0 (
    echo ❌ Failed to get dependencies
    pause
    exit /b 1
)

echo 🔧 Building Flutter app for Windows...
flutter build windows --debug
if %errorlevel% neq 0 (
    echo ❌ Build failed
    pause
    exit /b 1
)

echo 🚀 Launching Flutter app for Windows...
echo.
echo If the app crashes, try running it directly from:
echo %~dp0\flutter_frontend\build\windows\x64\runner\Debug\flutter_frontend.exe
echo.
flutter run -d windows --verbose

echo.
echo App finished running. Press any key to exit...
pause


