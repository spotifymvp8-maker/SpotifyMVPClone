"""
Конфигурация приложения.

Все настройки берутся из переменных окружения (.env).
"""

import os
import secrets

from dotenv import load_dotenv

load_dotenv()  # Загружает .env из корня проекта

# Подключение к PostgreSQL (формат: postgresql://user:password@host:port/dbname)
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/spotify_clone"
)

# JWT: секрет для подписи токенов, алгоритм, время жизни
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Access token истекает через 30 мин
REFRESH_TOKEN_EXPIRE_DAYS = 7    # Refresh token — через 7 дней

# Админы: email через запятую в ADMIN_EMAILS. Только они могут создавать/редактировать треки.
_admin_raw = os.getenv("ADMIN_EMAILS", "test@example.com")
ADMIN_EMAILS = {
    e.strip().lower()
    for e in _admin_raw.split(",")
    if e.strip()
}
if not ADMIN_EMAILS:
    ADMIN_EMAILS = {"test@example.com"}

# Рекомендации: время жизни кэша в секундах (0 = без кэша)
RECOMMENDATION_CACHE_TTL = int(os.getenv("RECOMMENDATION_CACHE_TTL", "300"))
