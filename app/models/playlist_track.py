"""
Модель PlaylistTrack — связующая таблица плейлист ↔ трек (многие-ко-многим).

Обычная связь многие-ко-многим реализуется простой таблицей (playlist_id, track_id).
Здесь добавлено поле position — порядок трека в плейлисте (0, 1, 2, ...).
Из-за этого нужна полноценная модель, а не просто association table.

Ограничения:
    UniqueConstraint(playlist_id, position) — в одном плейлисте не может быть
        двух треков на одной позиции.
    CheckConstraint(position >= 0) — позиция не может быть отрицательной.
"""

import uuid

from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database import Base


class PlaylistTrack(Base):
    __tablename__ = "playlist_tracks"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # FK на playlists. ondelete="CASCADE" — при удалении плейлиста удаляются все его треки.
    playlist_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("playlists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,  # ускоряет "все треки плейлиста" (WHERE playlist_id = ?)
    )

    # FK на tracks. ondelete="CASCADE" — при удалении трека удаляются все его вхождения в плейлисты.
    track_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("tracks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Порядковый номер трека в плейлисте. 0-based (первый трек = 0).
    # При добавлении нового трека position = текущее количество треков в плейлисте.
    position = Column(Integer, nullable=False)

    __table_args__ = (
        # Два трека не могут занимать одну позицию в одном плейлисте
        UniqueConstraint("playlist_id", "position", name="uq_playlist_position"),
        # Позиция не может быть отрицательной
        CheckConstraint("position >= 0", name="check_position_non_negative"),
    )

    # Обратные связи на Playlist и Track
    playlist = relationship("Playlist", back_populates="tracks")
    track    = relationship("Track",    back_populates="playlist_tracks")
