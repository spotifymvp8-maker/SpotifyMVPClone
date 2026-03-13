"""
Утилиты для аутентификации: хеширование паролей и JWT.

- bcrypt: хранение паролей в виде хеша (никогда не храним plain text)
- JWT: access token (короткий) + refresh token (длинный) для сессий
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
import bcrypt

from app.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Сравнение пароля с хешем через bcrypt. OAuth-пользователи (префикс oauth:) не могут входить по паролю."""
    if hashed_password.startswith("oauth:"):
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8") if isinstance(hashed_password, str) else hashed_password,
        )
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Хеширование пароля (bcrypt + соль). Результат сохраняется в auth_users.password_hash."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создание JWT access токена. В data обычно: sub (user_id), email. type='access'."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Создание JWT refresh токена (длинный срок жизни). Используется для обновления access."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Декодирование JWT. Возвращает payload или None при ошибке/истечении."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
