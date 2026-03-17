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
    """
    Проверяет, совпадает ли введённый пароль с сохранённым хешем.

    bcrypt.checkpw() повторно хеширует plain_password с той же солью,
    что содержится в hashed_password, и сравнивает результат.
    Это единственный правильный способ проверки bcrypt-хешей.

    Префикс "oauth:" означает, что пользователь зарегистрировался через OAuth
    (например, Google) и у него нет пароля. Попытка войти по паролю всегда
    вернёт False — нельзя взломать OAuth-аккаунт перебором пароля.
    """
    if hashed_password.startswith("oauth:"):
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            # hashed_password из БД может быть str или bytes — приводим к bytes
            hashed_password.encode("utf-8") if isinstance(hashed_password, str) else hashed_password,
        )
    except Exception:
        # Если хеш повреждён или несовместимого формата — возвращаем False
        return False


def get_password_hash(password: str) -> str:
    """
    Хеширует пароль через bcrypt перед сохранением в БД.

    bcrypt автоматически генерирует случайную соль и включает её в хеш.
    Благодаря соли два одинаковых пароля дают разные хеши — радужные таблицы бесполезны.
    Алгоритм намеренно медленный (~100ms), что делает перебор нереальным.

    Результат сохраняется в auth_users.password_hash.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создаёт JWT access token.

    В data обычно передаётся:
        {"sub": str(user_id), "email": user.email}

    Поле "sub" (subject) — стандартное поле JWT, содержит идентификатор пользователя.
    Поле "type": "access" позволяет различать access и refresh токены.
    Поле "exp" — время истечения (Unix timestamp), проверяется при decode.

    Токен подписывается SECRET_KEY алгоритмом HS256.
    Подпись гарантирует целостность: если изменить payload — подпись не совпадёт.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Добавляем служебные поля JWT
    to_encode.update({"exp": expire, "type": "access"})

    # jwt.encode возвращает строку вида "header.payload.signature"
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Создаёт JWT refresh token с длинным сроком жизни.

    Refresh token используется только для получения нового access token
    через POST /api/auth/refresh. Хранится на клиенте (localStorage).

    Отличается от access token полем "type": "refresh" —
    это не позволяет использовать refresh token для авторизованных запросов.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Декодирует и проверяет JWT токен.

    jwt.decode выполняет три проверки:
        1. Подпись — совпадает ли с SECRET_KEY (защита от подделки)
        2. Алгоритм — совпадает ли с ожидаемым (защита от атаки "alg: none")
        3. Срок жизни — не истёк ли "exp" (защита от использования старых токенов)

    Возвращает payload (dict) если всё ок, или None если любая проверка не прошла.
    None обрабатывается в dependencies.py — там выбрасывается HTTPException 401.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # JWTError покрывает: неверную подпись, истёкший токен, неверный формат
        return None
