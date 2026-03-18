@echo off
echo Testing app window mode...
echo.
echo Make sure Spotify Clone is already running (docker compose up).
echo.
timeout /t 2 /nobreak >nul

set "APP_URL=http://localhost:3000"
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    echo Opening Edge in app mode...
    start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --app=%APP_URL%
    goto :done
)
if exist "C:\Program Files\Microsoft\Edge\Application\msedge.exe" (
    echo Opening Edge in app mode...
    start "" "C:\Program Files\Microsoft\Edge\Application\msedge.exe" --app=%APP_URL%
    goto :done
)
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo Opening Chrome in app mode...
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app=%APP_URL%
    goto :done
)
echo No Edge or Chrome found. Opening default browser...
start http://localhost:3000

:done
echo.
echo If a separate window opened (no tabs/address bar) - it works!
pause
