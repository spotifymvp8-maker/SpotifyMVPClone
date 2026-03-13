"""
Модель AuthUser — учётные данные для входа.

Таблица auth_users хранит:
    - email, password_hash — для входа (bcrypt)
    - initial_username — используется при создании UserProfile

Связь: 1:1 с UserProfile (profile — публичные данные: username, avatar, bio)
"""

import uuid

from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database import Base


class AuthUser(Base):
    __tablename__ = "auth_users"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # bcrypt hash
    initial_username = Column(String(50), nullable=True)  # Для миграции в UserProfile
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Один пользователь — один профиль. При удалении AuthUser удаляется и UserProfile
    profile = relationship(
        "UserProfile",
        back_populates="auth_user",
        uselist=False,
        cascade="all, delete-orphan",
    )
