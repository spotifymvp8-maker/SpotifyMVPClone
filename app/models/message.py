"""
Модель Message — чат-сообщения между пользователями.

Структура:
    - sender_id, receiver_id — отправитель и получатель (связаны с auth_users)
    - content — текст сообщения
    - created_at, updated_at — время создания и последнего редактирования

Удаление пользователя при CASCADE приводит к удалению его сообщений.
"""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, func, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Message(Base):
    __tablename__ = "messages"

    # Уникальный идентификатор сообщения (UUID).
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Отправитель сообщения.
    # FK на auth_users, CASCADE — при удалении пользователя сообщение удаляется.
    sender_id = Column(
        PG_UUID(as_uuid=True), 
        ForeignKey("auth_users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )

    # Получатель сообщения.
    # Аналогично — FK c CASCADE.
    receiver_id = Column(
        PG_UUID(as_uuid=True), 
        ForeignKey("auth_users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )

    # Текст сообщения.
    content = Column(Text, nullable=False)

    # Дата/время создания сообщения (выставляется БД при вставке).
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False, 
        index=True
    )

    # Дата/время последнего изменения (выставляется БД, обновляется при каждом UPDATE).
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ORM-связь на объект AuthUser для sender.
    sender = relationship("AuthUser", foreign_keys=[sender_id])
    # ORM-связь на объект AuthUser для receiver.
    receiver = relationship("AuthUser", foreign_keys=[receiver_id])
