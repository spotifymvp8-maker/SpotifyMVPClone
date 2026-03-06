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
    """Проверить, что пользователь — владелец плейлиста."""
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
    user_id: UUID | None = Depends(get_optional_user_id),
    db: Session = Depends(get_db),
):
    """Получить плейлисты: публичные + свои (если авторизован)."""
    query = db.query(Playlist)
    if user_id is None:
        query = query.filter(Playlist.is_public == True)
    else:
        query = query.filter(
            or_(Playlist.is_public == True, Playlist.owner_id == user_id)
        )
    return query.all()


@router.get("/me", response_model=list[PlaylistResponse])
def get_my_playlists(
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Получить плейлисты текущего пользователя."""
    playlists = db.query(Playlist).filter(Playlist.owner_id == user_id).all()
    return playlists


@router.get("/{playlist_id}", response_model=PlaylistResponse)
def get_playlist(
    playlist_id: UUID,
    user_id: UUID | None = Depends(get_optional_user_id),
    db: Session = Depends(get_db),
):
    """Получить плейлист по ID с треками (публичный или свой)."""
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found",
        )
    if not playlist.is_public and (user_id is None or playlist.owner_id != user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found",
        )
    return playlist


@router.post("/", response_model=PlaylistResponse)
def create_playlist(
    playlist_data: PlaylistCreate,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Создать новый плейлист (владелец — текущий пользователь)."""
    playlist = Playlist(
        owner_id=user_id,
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
    """Обновить плейлист (только владелец)."""
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found",
        )
    _require_owner(playlist, user_id)

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
    """Удалить плейлист (только владелец)."""
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found",
        )
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
    """Добавить трек в плейлист (только владелец)."""
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found",
        )
    _require_owner(playlist, user_id)

    track = db.query(Track).filter(Track.id == track_data.track_id).first()
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found",
        )

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
    """Удалить трек из плейлиста (только владелец)."""
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found",
        )
    _require_owner(playlist, user_id)

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
