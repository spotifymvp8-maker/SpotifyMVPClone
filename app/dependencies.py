"""
FastAPI dependencies для авторизации.

Dependency Injection (DI) — механизм FastAPI: зависимости объявляются
в сигнатуре функции через Depends(...), и FastAPI автоматически их вычисляет
перед вызовом обработчика. Если dependency выбросит исключение — обработчик
не вызывается, клиент получает ошибку.

Использование в endpoints:
    - get_current_user_id: обязательная авторизация (401 если нет токена)
    - get_optional_user_id: опциональная (возвращает None если не авторизован)
    - get_admin_user_id: только для админов (403 если не админ)
"""

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.config import ADMIN_EMAILS
from app.database import get_db
from app.models.auth_user import AuthUser
from app.utils import decode_token

# ──────────────────────────────────────────────
# HTTPBearer — извлечение токена из заголовка
# ──────────────────────────────────────────────
# HTTPBearer автоматически извлекает токен из заголовка запроса:
#   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
#
# security (auto_error=True по умолчанию):
#   Если заголовка нет — сразу возвращает 403. Используется для защищённых эндпоинтов.
#
# security_optional (auto_error=False):
#   Если заголовка нет — возвращает None вместо ошибки. Используется для эндпоинтов,
#   доступных и анонимам, но ведущих себя иначе для авторизованных.
security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)


def get_optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional),
) -> Optional[UUID]:
    """
    Возвращает UUID пользователя из JWT-токена, или None если токена нет.
    Не выбрасывает исключение при отсутствии токена.

    Используется в эндпоинтах с опциональной авторизацией.
    Пример: GET /playlists/ — авторизованный видит свои + публичные,
    аноним — только публичные.
    """
    # Токен не передан вообще
    if not credentials:
        return None

    # Декодируем JWT: проверяем подпись и срок жизни
    payload = decode_token(credentials.credentials)
    if not payload:
        # Токен передан, но невалиден или истёк — возвращаем None, не ошибку
        return None

    user_id = payload.get("sub")  # "sub" (subject) — стандартное поле JWT с ID пользователя
    if not user_id:
        return None

    return UUID(user_id)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UUID:
    """
    Возвращает UUID пользователя из JWT-токена.
    Выбрасывает 401, если токен отсутствует, невалиден или истёк.

    Используется во всех эндпоинтах, требующих авторизации.
    Если добавить как dependency — неавторизованный пользователь никогда
    не дойдёт до тела функции-обработчика.
    """
    token = credentials.credentials  # сам JWT (без префикса "Bearer ")

    # decode_token проверяет подпись SECRET_KEY и срок жизни (exp)
    payload = decode_token(token)

    if not payload:
        # Токен невалиден: неверная подпись, истёк, или просто мусор
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user_id = payload.get("sub")
    if not user_id:
        # Валидный JWT, но без поля "sub" — такого быть не должно в норме
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    return UUID(user_id)


def get_admin_user_id(
    user_id: UUID = Depends(get_current_user_id),  # сначала проверяем, что вообще авторизован
    db: Session = Depends(get_db),
) -> UUID:
    """
    Проверяет, что авторизованный пользователь — администратор.
    Выбрасывает 403, если пользователь не найден или его email не в ADMIN_EMAILS.

    Цепочка зависимостей:
        get_admin_user_id → get_current_user_id → HTTPBearer
    FastAPI разрешает зависимости рекурсивно.

    Логика ролей проста: список email-адресов в переменной окружения ADMIN_EMAILS.
    Не требует отдельной таблицы ролей в БД.
    """
    # Делаем запрос в БД, чтобы получить email пользователя
    user = db.query(AuthUser).filter(AuthUser.id == user_id).first()

    # user.email.lower() — приводим к нижнему регистру для сравнения без учёта регистра
    if not user or user.email.lower() not in ADMIN_EMAILS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return user_id
