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

# ──────────────────────────────────────────────
# In-memory кэш рекомендаций
# ──────────────────────────────────────────────
# Кэш хранится в словаре: ключ = str(profile_id), значение = (timestamp, список треков).
# При каждом запросе проверяем, не истёк ли TTL.
# Если истёк — пересчитываем и обновляем кэш.
#
# Зачем кэш? Алгоритм делает несколько запросов к БД — кэшируем результат на 5 минут.
# Недостатки: теряется при рестарте, не работает при нескольких инстансах backend.
# В production: заменить на Redis.
_cache: dict[str, tuple[float, list]] = {}

# threading.Lock защищает кэш от race condition при параллельных запросах.
# Без блокировки два потока могут одновременно прочитать "устаревший" кэш
# и оба начнут пересчёт — лишняя нагрузка на БД.
_cache_lock = threading.Lock()

MAX_RECOMMENDATIONS = 20  # максимальное количество рекомендаций в ответе


def _get_cached(profile_id: UUID) -> list[Track] | None:
    """
    Возвращает кэшированные рекомендации, если TTL не истёк.
    Возвращает None если кэша нет или он устарел.
    """
    if RECOMMENDATION_CACHE_TTL <= 0:
        return None  # кэш отключён через конфиг

    key = str(profile_id)
    with _cache_lock:  # блокируем доступ к кэшу (thread-safe)
        if key in _cache:
            ts, result = _cache[key]
            if time() - ts < RECOMMENDATION_CACHE_TTL:
                return result   # TTL не истёк — возвращаем из кэша
            del _cache[key]     # TTL истёк — удаляем устаревшую запись
    return None


def _set_cached(profile_id: UUID, tracks: list[Track]) -> None:
    """Сохраняет рекомендации в кэш с текущим timestamp."""
    if RECOMMENDATION_CACHE_TTL <= 0:
        return  # кэш отключён

    key = str(profile_id)
    with _cache_lock:
        _cache[key] = (time(), tracks)


def _compute_recommendations(profile_id: UUID, db: Session) -> list[Track]:
    """
    Rule-based алгоритм рекомендаций (без ML).

    Логика в порядке приоритета:
        1. Исключаем треки, которые пользователь уже слышал
        2. Рекомендуем треки любимых артистов (из истории), которые не слышал
        3. Добавляем треки из плейлистов пользователя (которых нет в истории)
        4. Если рекомендаций мало — добираем новые треки из БД

    В конце перемешиваем и ограничиваем до MAX_RECOMMENDATIONS.
    """
    exclude_ids: set[UUID] = set()   # ID треков, которые не рекомендуем (уже слышал)
    candidates: list[Track] = []     # кандидаты для рекомендации

    # ── Шаг 1: получаем историю (треки к исключению) ──
    history_tracks = (
        db.query(ListeningHistory.track_id)
        .filter(ListeningHistory.user_id == profile_id)
        .distinct()  # каждый трек учитываем один раз, даже если слушали несколько раз
        .all()
    )
    exclude_ids.update(t[0] for t in history_tracks)

    # ── Шаг 2: любимые артисты из истории → их другие треки ──
    artists_from_history = (
        db.query(Track.artist)
        .join(ListeningHistory, ListeningHistory.track_id == Track.id)
        .filter(ListeningHistory.user_id == profile_id)
        .distinct()
        .limit(10)  # берём топ-10 уникальных артистов
        .all()
    )
    artist_names = [a[0] for a in artists_from_history]

    for artist in artist_names:
        # Ищем треки этого артиста, которые ещё не слышал пользователь
        q = db.query(Track).filter(Track.artist == artist)
        if exclude_ids:
            q = q.filter(~Track.id.in_(exclude_ids))  # ~ означает NOT IN
        tracks = q.limit(5).all()
        candidates.extend(tracks)
        exclude_ids.update(t.id for t in tracks)  # добавляем в исключения, чтобы не дублировать

    # ── Шаг 3: треки из плейлистов, которых нет в истории ──
    playlist_track_ids = (
        db.query(PlaylistTrack.track_id)
        .join(Playlist, Playlist.id == PlaylistTrack.playlist_id)
        .filter(Playlist.owner_id == profile_id)  # только плейлисты пользователя
        .distinct()
        .all()
    )
    # Оставляем только те ID, которых ещё нет в исключениях
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

    # ── Шаг 4: если мало рекомендаций — добираем новые треки из БД ──
    if len(candidates) < MAX_RECOMMENDATIONS:
        remaining = MAX_RECOMMENDATIONS - len(candidates)
        q = db.query(Track).order_by(Track.created_at.desc()).limit(remaining * 2)
        if exclude_ids:
            q = q.filter(~Track.id.in_(exclude_ids))
        fallback = q.all()
        random.shuffle(fallback)              # перемешиваем для разнообразия
        candidates.extend(fallback[:remaining])

    # ── Финал: перемешиваем, убираем дубликаты через dict.fromkeys, ограничиваем ──
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
    """
    Персонализированные рекомендации для текущего пользователя.

    Сначала проверяется кэш — если TTL не истёк, возвращается кэшированный результат.
    Иначе запускается алгоритм _compute_recommendations, результат кэшируется.
    """
    profile = _ensure_profile(user_id, db)

    # Проверяем кэш
    cached = _get_cached(profile.id)
    if cached is not None:
        return [TrackResponse.model_validate(t) for t in cached]

    # Кэш устарел или пуст — вычисляем заново
    tracks = _compute_recommendations(profile.id, db)
    _set_cached(profile.id, tracks)

    return [TrackResponse.model_validate(t) for t in tracks]
