"""
FastAPI dependencies для авторизации.

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

# HTTPBearer — извлекает токен из заголовка Authorization: Bearer <token>
security = HTTPBearer()           # Требует токен, иначе 403
security_optional = HTTPBearer(auto_error=False)  # Токен опционален


def get_optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional),
) -> Optional[UUID]:
    """ID пользователя из JWT или None (для публичных endpoints с опциональным контентом)."""
    if not credentials:
        return None
    payload = decode_token(credentials.credentials)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    return UUID(user_id)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UUID:
    """ID пользователя из JWT. Вызывает 401, если токен отсутствует или невалиден."""
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    return UUID(user_id)


def get_admin_user_id(
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> UUID:
    """Проверка админских прав: email пользователя должен быть в ADMIN_EMAILS. Иначе 403."""
    user = db.query(AuthUser).filter(AuthUser.id == user_id).first()
    if not user or user.email.lower() not in ADMIN_EMAILS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user_id
