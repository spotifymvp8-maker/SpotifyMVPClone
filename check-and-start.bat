@echo off
cd /d "%~dp0"

echo === Spotify Clone - Diagnostic ===
echo.
echo 1. Current folder: %CD%
echo.
echo 2. Docker in PATH?
where docker 2>nul
if %errorlevel% neq 0 (
    echo    NO - docker not found
    set "PATH=%PATH%;C:\Program Files\Docker\Docker\resources\bin"
    where docker 2>nul
    if %errorlevel% neq 0 echo    Still not found - is Docker Desktop installed?
) else (
    echo    YES
)
echo.
echo 3. Docker running?
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo    NO - start Docker Desktop first!
) else (
    echo    YES
)
echo.
echo 4. docker-compose.yml exists?
if exist "docker-compose.yml" (echo    YES) else (echo    NO)
echo.
pause
