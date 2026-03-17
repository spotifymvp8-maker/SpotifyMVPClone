"""Playlist routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user_id, get_optional_user_id
from app.models.playlist import Playlist
from app.models.playlist_track import PlaylistTrack
from app.models.track import Track
from app.schemas import PlaylistCreate, PlaylistResponse, PlaylistTrackAdd, PlaylistUpdate

router = APIRouter()


def _require_owner(playlist: Playlist, user_id: UUID) -> None:
    """
    Проверяет, что пользователь — владелец плейлиста.
    Вызывается перед любой мутирующей операцией (PUT, DELETE, добавление/удаление треков).

    Выбрасывает 403 Forbidden, если user_id != playlist.owner_id.
    Это предотвращает изменение чужих плейлистов.
    """
    if playlist.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can edit this playlist",
        )


@router.get("/health")
def playlist_health():
    """Health check для Playlist Service."""
    return {"status": "ok", "service": "playlist"}


@router.get("/", response_model=list[PlaylistResponse])
def get_all_playlists(
    user_id: UUID | None = Depends(get_optional_user_id),  # None если не авторизован
    db: Session = Depends(get_db),
):
    """
    Список плейлистов с учётом авторизации.

    Авторизованный пользователь видит:
        - все публичные плейлисты (is_public=True)
        - свои приватные плейлисты (owner_id == user_id)

    Анонимный пользователь видит:
        - только публичные плейлисты
    """
    query = db.query(Playlist)
    if user_id is None:
        # Аноним — только публичные
        query = query.filter(Playlist.is_public == True)
    else:
        # Авторизованный — публичные ИЛИ свои
        query = query.filter(
            or_(Playlist.is_public == True, Playlist.owner_id == user_id)
        )
    return query.all()


@router.get("/me", response_model=list[PlaylistResponse])
def get_my_playlists(
    user_id: UUID = Depends(get_current_user_id),  # обязательная авторизация
    db: Session = Depends(get_db),
):
    """Плейлисты текущего пользователя (все: публичные и приватные)."""
    playlists = db.query(Playlist).filter(Playlist.owner_id == user_id).all()
    return playlists


@router.get("/{playlist_id}", response_model=PlaylistResponse)
def get_playlist(
    playlist_id: UUID,
    user_id: UUID | None = Depends(get_optional_user_id),
    db: Session = Depends(get_db),
):
    """
    Плейлист по ID с треками.

    Приватный плейлист возвращает 404 (не 403!) если запрашивает не владелец.
    Возврат 404 вместо 403 — security best practice: не раскрываем факт существования.
    """
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")

    # Приватный плейлист недоступен анонимам и чужим пользователям
    if not playlist.is_public and (user_id is None or playlist.owner_id != user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")

    return playlist


@router.post("/", response_model=PlaylistResponse)
def create_playlist(
    playlist_data: PlaylistCreate,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Создать плейлист.

    owner_id берётся из JWT токена (не из тела запроса).
    Это гарантирует, что пользователь не может создать плейлист от имени другого.
    """
    playlist = Playlist(
        owner_id=user_id,          # владелец = текущий пользователь из токена
        title=playlist_data.title,
        is_public=playlist_data.is_public,
    )
    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    return playlist


@router.put("/{playlist_id}", response_model=PlaylistResponse)
def update_playlist(
    playlist_id: UUID,
    playlist_data: PlaylistUpdate,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Обновить плейлист. Только владелец."""
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")

    _require_owner(playlist, user_id)  # проверяем права ПЕРЕД изменением

    update_data = playlist_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(playlist, field, value)

    db.commit()
    db.refresh(playlist)
    return playlist


@router.delete("/{playlist_id}")
def delete_playlist(
    playlist_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Удалить плейлист. Только владелец.

    Каскадно удалятся все записи PlaylistTrack (треки из плейлиста).
    Сами треки (в таблице tracks) не удаляются.
    """
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")

    _require_owner(playlist, user_id)

    db.delete(playlist)
    db.commit()
    return {"message": "Playlist deleted successfully"}


@router.post("/{playlist_id}/tracks", response_model=PlaylistResponse)
def add_track_to_playlist(
    playlist_id: UUID,
    track_data: PlaylistTrackAdd,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Добавить трек в плейлист. Только владелец.

    Если position не передан — трек добавляется в конец.
    position = текущее количество треков в плейлисте (0-based).

    UniqueConstraint на (playlist_id, position) в БД предотвращает коллизии позиций.
    """
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")

    _require_owner(playlist, user_id)

    track = db.query(Track).filter(Track.id == track_data.track_id).first()
    if not track:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Track not found")

    # Если position не указан — добавляем в конец (позиция = количество текущих треков)
    max_position = db.query(PlaylistTrack.position).filter(
        PlaylistTrack.playlist_id == playlist_id
    ).count()

    playlist_track = PlaylistTrack(
        playlist_id=playlist_id,
        track_id=track_data.track_id,
        position=track_data.position if track_data.position is not None else max_position,
    )
    db.add(playlist_track)
    db.commit()
    db.refresh(playlist)
    return playlist


@router.delete("/{playlist_id}/tracks/{track_id}")
def remove_track_from_playlist(
    playlist_id: UUID,
    track_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Удалить трек из плейлиста. Только владелец.

    Удаляется только запись PlaylistTrack (связь).
    Сам трек в таблице tracks остаётся нетронутым.
    """
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")

    _require_owner(playlist, user_id)

    # Ищем конкретную связь в таблице playlist_tracks
    playlist_track = db.query(PlaylistTrack).filter(
        PlaylistTrack.playlist_id == playlist_id,
        PlaylistTrack.track_id == track_id,
    ).first()
    if not playlist_track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found in playlist",
        )

    db.delete(playlist_track)
    db.commit()
    return {"message": "Track removed from playlist successfully"}
