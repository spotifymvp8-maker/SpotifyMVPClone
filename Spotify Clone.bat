@echo off
cd /d "%~dp0"

REM Add Docker to PATH (needed when launched from shortcut)
set "PATH=%PATH%;C:\Program Files\Docker\Docker\resources\bin"

echo.
echo ========================================
echo   Spotify Clone - Starting...
echo ========================================
echo.
echo Folder: %CD%
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker is not running. Starting Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo.
    echo Wait 30-60 seconds for Docker to start, then try again.
    echo Or start Docker Desktop manually from the Start menu.
    pause
    exit /b 1
)

echo [1/2] Starting Docker containers...
docker compose up -d

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to start containers.
    echo Make sure Docker Desktop is fully started (tray icon).
    pause
    exit /b 1
)

echo.
echo [2/2] Waiting for app to start (15 sec), then opening in app window...
timeout /t 15 /nobreak >nul

REM Try to open in standalone app window (no tabs, no address bar)
set "APP_URL=http://localhost:3000"
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --app=%APP_URL%
    goto :opened
)
if exist "C:\Program Files\Microsoft\Edge\Application\msedge.exe" (
    start "" "C:\Program Files\Microsoft\Edge\Application\msedge.exe" --app=%APP_URL%
    goto :opened
)
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app=%APP_URL%
    goto :opened
)

REM Fallback: open in default browser
start http://localhost:3000

:opened
echo.
echo Done! App window opened: %APP_URL%
echo.
echo You can close this window.
timeout /t 3
exit
