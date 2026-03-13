"""
Модель UserProfile — публичный профиль пользователя.

id совпадает с auth_users.id (1:1). Хранит username, avatar, bio.
Плейлисты и история прослушиваний ссылаются на user_profiles, а не на auth_users.
"""

from sqlalchemy import Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    username = Column(String(50), unique=True, nullable=False, index=True)
    avatar_url = Column(String(255))   # URL аватара
    bio = Column(String(500))          # О себе
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    auth_user = relationship("AuthUser", back_populates="profile")
    playlists = relationship(
        "Playlist", back_populates="owner", cascade="all, delete-orphan"
    )
    listening_history = relationship(
        "ListeningHistory", back_populates="user", cascade="all, delete-orphan"
    )
