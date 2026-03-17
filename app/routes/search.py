"""Search routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.track import Track
from app.models.album import Album
from app.schemas import TrackResponse, AlbumResponse, ArtistSearchResult

router = APIRouter()


# Два декоратора — исправление 307-редиректа в Docker/Nginx.
# Без этого GET /api/search редиректился на /api/search/ с ошибкой в Docker.
@router.get("")
@router.get("/")
def search(
    q: str = Query(..., min_length=1),  # ... означает "обязательный параметр"
    db: Session = Depends(get_db),
):
    """
    Полнотекстовый поиск по трекам, альбомам и артистам.

    Параметр q — поисковая строка (минимум 1 символ).
    ilike — регистронезависимое LIKE в PostgreSQL (ILIKE).
    or_() — SQL OR: трек найдётся, если запрос есть хотя бы в одном поле.

    Структура ответа:
        {
            "tracks": [...],   — треки, где q есть в title/artist/album_name
            "albums": [...],   — альбомы, где q есть в title/artist
            "artists": [...]   — уникальные имена артистов из найденных треков/альбомов
        }

    Почему поиск работает без JOIN по альбомам?
        Поле album_name денормализовано в Track — хранится прямо в треке.
        Это ускоряет поиск: не нужен JOIN с таблицей albums.
    """
    query = q.strip().lower()
    if not query:
        return {"tracks": [], "albums": [], "artists": []}

    # Поиск треков по трём полям через OR
    # ilike("%{query}%") — содержит подстроку, регистр не важен
    tracks = (
        db.query(Track)
        .filter(
            or_(
                Track.title.ilike(f"%{query}%"),
                Track.artist.ilike(f"%{query}%"),
                Track.album_name.ilike(f"%{query}%"),  # добавлено для поиска по альбому
            )
        )
        .limit(20)
        .all()
    )

    # Поиск альбомов по двум полям
    albums = (
        db.query(Album)
        .filter(
            or_(
                Album.title.ilike(f"%{query}%"),
                Album.artist.ilike(f"%{query}%"),
            )
        )
        .limit(20)
        .all()
    )

    # Артисты — нет отдельной таблицы, собираем уникальные имена из треков и альбомов
    # Используем set для дедупликации
    artist_names = set()
    for t in tracks:
        if query in t.artist.lower():
            artist_names.add(t.artist)
    for a in albums:
        if query in a.artist.lower():
            artist_names.add(a.artist)

    # Сортируем по алфавиту, ограничиваем 20 результатами
    artists = [ArtistSearchResult(name=name) for name in sorted(artist_names)[:20]]

    return {
        "tracks": [TrackResponse.model_validate(t) for t in tracks],
        "albums": [AlbumResponse.model_validate(a) for a in albums],
        "artists": artists,
    }
