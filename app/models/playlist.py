"""
Модель Playlist — плейлист пользователя.

owner_id → user_profiles (не auth_users!).
История и плейлисты принадлежат "личности" (профилю), а не "учётным данным".

Треки хранятся через промежуточную таблицу PlaylistTrack, которая добавляет
поле position (порядок треков в плейлисте).
"""

import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # FK на user_profiles (не auth_users!) — плейлист принадлежит профилю.
    # ondelete="CASCADE" — при удалении пользователя удаляются все его плейлисты.
    # index=True — ускоряет запрос "мои плейлисты" (WHERE owner_id = ?)
    owner_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = Column(String(255), nullable=False)

    # is_public = True — плейлист виден всем пользователям.
    # is_public = False — виден только владельцу.
    is_public = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Связь с владельцем (UserProfile)
    owner = relationship("UserProfile", back_populates="playlists")

    # Треки плейлиста через промежуточную таблицу PlaylistTrack.
    # order_by="PlaylistTrack.position" — SQLAlchemy сортирует при загрузке.
    # cascade="all, delete-orphan" — при удалении плейлиста удаляются записи PlaylistTrack.
    tracks = relationship(
        "PlaylistTrack",
        back_populates="playlist",
        order_by="PlaylistTrack.position",
        cascade="all, delete-orphan",
    )
