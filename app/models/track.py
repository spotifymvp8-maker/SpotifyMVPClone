"""
Модель Track — музыкальный трек.

Связи:
    - album_id → Album (опционально, трек может быть синглом)
    - PlaylistTrack — многие-ко-многим с Playlist
    - ListeningHistory — история прослушиваний
"""

import uuid

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Track(Base):
    __tablename__ = "tracks"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    artist = Column(String(255), nullable=False, index=True)
    album_name = Column(String(255), nullable=True, index=True)  # Дублируется для быстрого поиска
    album_id = Column(PG_UUID(as_uuid=True), ForeignKey("albums.id", ondelete="SET NULL"), nullable=True, index=True)
    image_url = Column(String(500), nullable=True)   # Обложка трека
    duration = Column(Integer, nullable=False)      # Длительность в секундах
    file_url = Column(String(500), nullable=False)   # URL аудиофайла (локальный или SoundHelix)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (CheckConstraint("duration > 0", name="check_duration_positive"),)

    album_ref = relationship("Album", back_populates="songs")  # Альбом, к которому принадлежит трек
    playlist_tracks = relationship(
        "PlaylistTrack", back_populates="track", cascade="all, delete-orphan"
    )
    listening_history = relationship(
        "ListeningHistory", back_populates="track", cascade="all, delete-orphan"
    )
