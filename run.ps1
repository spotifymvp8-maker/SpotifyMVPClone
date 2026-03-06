# Запуск FastAPI сервера
Set-Location $PSScriptRoot
# Для локального запуска (без Docker) используем localhost
if (-not $env:DATABASE_URL -or $env:DATABASE_URL -match "@postgres:") {
    $env:DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/spotify_clone"
}
python -m uvicorn app.main:app --reload
