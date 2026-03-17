"""
Модель Album — музыкальный альбом.

Один альбом содержит много треков (relationship "songs").
При удалении альбома треки НЕ удаляются — album_id в треке становится NULL (SET NULL).
Это гарантирует, что пользователи не потеряют треки из плейлистов.
"""

import uuid

from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Album(Base):
    __tablename__ = "albums"

    id           = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title        = Column(String(255), nullable=False)
    artist       = Column(String(255), nullable=False)
    image_url    = Column(String(500), nullable=False)   # обложка (обязательна для альбома)
    release_year = Column(Integer, nullable=False)

    # Здесь определяются два столбца: created_at и updated_at.
    # created_at — это дата и время создания записи; по умолчанию устанавливается текущее время на сервере при создании альбома.
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # updated_at — это дата и время последнего изменения записи; по умолчанию тоже текущее время,
    # но автоматически обновляется при каждом изменении альбома.
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    

    # Треки альбома. Загружаются лениво (lazy loading) при первом обращении к album.songs.
    # cascade="all, delete-orphan" здесь НЕТ — при удалении альбома треки остаются (SET NULL в FK).
    # back_populates="album_ref" — обратная сторона Track.album_ref
    songs = relationship("Track", back_populates="album_ref", cascade="all, delete-orphan")
