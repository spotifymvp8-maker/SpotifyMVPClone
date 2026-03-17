"""
Модель UserProfile — публичный профиль пользователя.

id совпадает с auth_users.id (паттерн Shared Primary Key для отношения 1:1).
Это гарантирует: никогда не будет профиля без пользователя.

Почему не в одной таблице с auth_users?
    - Разделение ответственности: auth = безопасность, profile = публичность
    - Плейлисты и история прослушиваний ссылаются на profile, а не на auth_user
    - В будущем можно добавить OAuth без затрагивания логики профилей
"""

from sqlalchemy import Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    # id = FK на auth_users.id И одновременно PK этой таблицы.
    # Паттерн Shared Primary Key: не генерируется отдельно, берётся из auth_users.
    # ondelete="CASCADE" — при удалении auth_users запись в user_profiles удаляется автоматически.
    id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # unique=True + index=True — имена уникальны, быстрый поиск при проверке занятости
    username = Column(String(50), unique=True, nullable=False, index=True)

    # Nullable поля — не обязательны при создании профиля
    avatar_url = Column(String(255))
    bio = Column(String(500))

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    # onupdate=func.now() — SQLAlchemy автоматически обновляет при любом UPDATE
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Обратная связь на AuthUser (back_populates="profile")
    auth_user = relationship("AuthUser", back_populates="profile")

    # Плейлисты пользователя: при удалении профиля — удаляются и плейлисты
    playlists = relationship(
        "Playlist", back_populates="owner", cascade="all, delete-orphan"
    )

    # История прослушиваний: при удалении профиля — удаляется история
    listening_history = relationship(
        "ListeningHistory", back_populates="user", cascade="all, delete-orphan"
    )
