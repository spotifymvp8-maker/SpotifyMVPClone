"""
Модель ListeningHistory — история прослушиваний.

Каждое нажатие "play" на фронтенде создаёт новую запись.
История накапливается и используется сервисом рекомендаций:
    - извлекает любимых артистов пользователя
    - предлагает их треки, которые ещё не слушались

Ссылается на user_profiles (не auth_users) — история принадлежит "личности",
а не учётным данным.
"""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database import Base


class ListeningHistory(Base):
    __tablename__ = "listening_history"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # FK на user_profiles. ondelete="CASCADE" — при удалении пользователя удаляется история.
    # index=True — ускоряет "история конкретного пользователя" (WHERE user_id = ?)
    user_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # FK на tracks. ondelete="CASCADE" — при удалении трека удаляются записи о его прослушивании.
    # index=True — ускоряет подсчёт прослушиваний трека
    track_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("tracks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Время прослушивания. server_default — PostgreSQL проставляет автоматически при INSERT.
    played_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Связи для удобного доступа к объектам через ORM (user.listening_history, track.listening_history)
    user  = relationship("UserProfile", back_populates="listening_history")
    track = relationship("Track",       back_populates="listening_history")
