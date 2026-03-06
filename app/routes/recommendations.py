"""Recommendation Service — персонализированные рекомендации (rule-based MVP)."""

import random
import threading
from time import time
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import RECOMMENDATION_CACHE_TTL
from app.database import get_db
from app.dependencies import get_current_user_id
from app.models.listening_history import ListeningHistory
from app.models.playlist import Playlist
from app.models.playlist_track import PlaylistTrack
from app.models.track import Track
from app.routes.users import _ensure_profile
from app.schemas import TrackResponse

router = APIRouter()

# Кэш: key -> (timestamp, result)
_cache: dict[str, tuple[float, list]] = {}
_cache_lock = threading.Lock()
MAX_RECOMMENDATIONS = 20


def _get_cached(profile_id: UUID) -> list[Track] | None:
    """Получить из кэша, если не истёк TTL."""
    if RECOMMENDATION_CACHE_TTL <= 0:
        return None
    key = str(profile_id)
    with _cache_lock:
        if key in _cache:
            ts, result = _cache[key]
            if time() - ts < RECOMMENDATION_CACHE_TTL:
                return result
            del _cache[key]
    return None


def _set_cached(profile_id: UUID, tracks: list[Track]) -> None:
    """Сохранить в кэш."""
    if RECOMMENDATION_CACHE_TTL <= 0:
        return
    key = str(profile_id)
    with _cache_lock:
        _cache[key] = (time(), tracks)


def _compute_recommendations(profile_id: UUID, db: Session) -> list[Track]:
    """Rule-based: история + плейлисты + треки."""
    exclude_ids: set[UUID] = set()
    candidates: list[Track] = []

    # 1. Треки из истории (для исключения)
    history_tracks = (
        db.query(ListeningHistory.track_id)
        .filter(ListeningHistory.user_id == profile_id)
        .distinct()
        .all()
    )
    exclude_ids.update(t[0] for t in history_tracks)

    # 2. Артисты из истории — рекомендуем другие треки тех же артистов
    artists_from_history = (
        db.query(Track.artist)
        .join(ListeningHistory, ListeningHistory.track_id == Track.id)
        .filter(ListeningHistory.user_id == profile_id)
        .distinct()
        .limit(10)
        .all()
    )
    artist_names = [a[0] for a in artists_from_history]


    for artist in artist_names:
        q = db.query(Track).filter(Track.artist == artist)
        if exclude_ids:
            q = q.filter(~Track.id.in_(exclude_ids))
        tracks = q.limit(5).all()
        candidates.extend(tracks)
        exclude_ids.update(t.id for t in tracks)

    # 3. Треки из плейлистов пользователя, которых нет в истории
    playlist_track_ids = (
        db.query(PlaylistTrack.track_id)
        .join(Playlist, Playlist.id == PlaylistTrack.playlist_id)
        .filter(Playlist.owner_id == profile_id)
        .distinct()
        .all()
    )
    playlist_track_ids_set = {t[0] for t in playlist_track_ids} - exclude_ids

    if playlist_track_ids_set:
        tracks_from_playlists = (
            db.query(Track)
            .filter(Track.id.in_(playlist_track_ids_set))
            .limit(10)
            .all()
        )
        candidates.extend(tracks_from_playlists)
        exclude_ids.update(t.id for t in tracks_from_playlists)

    # 4. Если мало — добавить популярные/новые треки
    if len(candidates) < MAX_RECOMMENDATIONS:
        remaining = MAX_RECOMMENDATIONS - len(candidates)
        q = db.query(Track).order_by(Track.created_at.desc()).limit(remaining * 2)
        if exclude_ids:
            q = q.filter(~Track.id.in_(exclude_ids))
        fallback = q.all()
        random.shuffle(fallback)
        candidates.extend(fallback[:remaining])

    # Перемешать и ограничить
    random.shuffle(candidates)
    return list(dict.fromkeys(candidates))[:MAX_RECOMMENDATIONS]


@router.get("/health")
def recommendations_health():
    """Health check для Recommendation Service."""
    return {"status": "ok", "service": "recommendation"}


@router.get("/")
def get_recommendations(
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Персонализированные рекомендации (rule-based MVP, с кэшированием)."""
    profile = _ensure_profile(user_id, db)

    cached = _get_cached(profile.id)
    if cached is not None:
        return [TrackResponse.model_validate(t) for t in cached]

    tracks = _compute_recommendations(profile.id, db)
    _set_cached(profile.id, tracks)
    return [TrackResponse.model_validate(t) for t in tracks]
