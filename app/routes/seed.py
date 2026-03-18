"""
Seed routes — API для загрузки тестовых данных.

POST /api/seed/seed — создаёт пользователя, альбомы, треки, плейлист.
    ?force=true — обновить URL треков (SoundHelix) без пересоздания альбомов.

Обложки альбомов и треков скачиваются локально (picsum.photos ненадёжен из браузера).
"""

import uuid as uuid_module
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db

IMAGES_DIR = Path(__file__).resolve().parent.parent.parent / "media" / "images"


def _download_image(url: str) -> str | None:
    """Скачать изображение по URL и сохранить в media/images/. Вернуть локальный URL."""
    if not url or not url.startswith("http"):
        return None
    try:
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, follow_redirects=True)
            resp.raise_for_status()
        ct = resp.headers.get("content-type", "image/jpeg").lower()
        ext = ".png" if "png" in ct else ".webp" if "webp" in ct else ".jpg"
        filename = f"{uuid_module.uuid4().hex}{ext}"
        (IMAGES_DIR / filename).write_bytes(resp.content)
        return f"/media/images/{filename}"
    except Exception:
        return None
from app.models.auth_user import AuthUser
from app.models.user_profile import UserProfile
from app.models.album import Album
from app.models.track import Track
from app.models.playlist import Playlist
from app.models.playlist_track import PlaylistTrack
from app.utils import get_password_hash

router = APIRouter()

# Тестовые данные из Spotify-version
TEST_USER = {
    "email": "test@example.com",
    "password": "test123",
    "username": "testuser"
}

# Внешние URL для аудио (SoundHelix — бесплатные примеры)
SOUNDHELIX_BASE = "https://www.soundhelix.com/examples/mp3"

# Альбомы из seeds/albums.js
TEST_ALBUMS = [
    {"title": "Urban Nights", "artist": "Various Artists", "image_url": "https://picsum.photos/seed/album1/300/300", "release_year": 2024},
    {"title": "Coastal Dreaming", "artist": "Various Artists", "image_url": "https://picsum.photos/seed/album2/300/300", "release_year": 2024},
    {"title": "Midnight Sessions", "artist": "Various Artists", "image_url": "https://picsum.photos/seed/album3/300/300", "release_year": 2024},
    {"title": "Eastern Dreams", "artist": "Various Artists", "image_url": "https://picsum.photos/seed/album4/300/300", "release_year": 2024}
]

# Треки — file_url из SoundHelix (работают без локальных файлов)
TEST_TRACKS = [
    # Album 1: Urban Nights
    {"title": "City Rain", "artist": "Urban Echo", "duration": 245, "file_url": f"{SOUNDHELIX_BASE}/SoundHelix-Song-7.mp3", "image_url": "https://picsum.photos/seed/t7/300/300", "album_name": "Urban Nights"},
    {"title": "Neon Lights", "artist": "Night Runners", "duration": 198, "file_url": f"{SOUNDHELIX_BASE}/SoundHelix-Song-5.mp3", "image_url": "https://picsum.photos/seed/t5/300/300", "album_name": "Urban Nights"},
    {"title": "Urban Jungle", "artist": "City Lights", "duration": 223, "file_url": f"{SOUNDHELIX_BASE}/SoundHelix-Song-15.mp3", "image_url": "https://picsum.photos/seed/t15/300/300", "album_name": "Urban Nights"},
    {"title": "Neon Dreams", "artist": "Cyber Pulse", "duration": 267, "file_url": f"{SOUNDHELIX_BASE}/SoundHelix-Song-13.mp3", "image_url": "https://picsum.photos/seed/t13/300/300", "album_name": "Urban Nights"},
    # Album 2: Coastal Dreaming
    {"title": "Summer Daze", "artist": "Coastal Kids", "duration": 187, "file_url": f"{SOUNDHELIX_BASE}/SoundHelix-Song-4.mp3", "image_url": "https://picsum.photos/seed/t4/300/300", "album_name": "Coastal Dreaming"},
    {"title": "Ocean Waves", "artist": "Coastal Drift", "duration": 214, "file_url": f"{SOUNDHELIX_BASE}/SoundHelix-Song-9.mp3", "image_url": "https://picsum.photos/seed/t9/300/300", "album_name": "Coastal Dreaming"},
    {"title": "Crystal Rain", "artist": "Echo Valley", "duration": 243, "file_url": f"{SOUNDHELIX_BASE}/SoundHelix-Song-16.mp3", "image_url": "https://picsum.photos/seed/t16/300/300", "album_name": "Coastal Dreaming"},
    {"title": "Starlight", "artist": "Luna Bay", "duration": 195, "file_url": f"{SOUNDHELIX_BASE}/SoundHelix-Song-10.mp3", "image_url": "https://picsum.photos/seed/t10/300/300", "album_name": "Coastal Dreaming"},
    # Album 3: Midnight Sessions
    {"title": "Stay With Me", "artist": "Sarah Mitchell", "duration": 245, "file_url": f"{SOUNDHELIX_BASE}/SoundHelix-Song-1.mp3", "image_url": "https://picsum.photos/seed/t1/300/300", "album_name": "Midnight Sessions"},
    {"title": "Midnight Drive", "artist": "The Wanderers", "duration": 198, "file_url": f"{SOUNDHELIX_BASE}/SoundHelix-Song-2.mp3", "image_url": "https://picsum.photos/seed/t2/300/300", "album_name": "Midnight Sessions"},
    {"title": "Moonlight Dance", "artist": "Silver Shadows", "duration": 223, "file_url": f"{SOUNDHELIX_BASE}/SoundHelix-Song-14.mp3", "image_url": "https://picsum.photos/seed/t14/300/300", "album_name": "Midnight Sessions"},
    # Album 4: Eastern Dreams
    {"title": "Lost in Tokyo", "artist": "Electric Dreams", "duration": 178, "file_url": f"{SOUNDHELIX_BASE}/SoundHelix-Song-3.mp3", "image_url": "https://picsum.photos/seed/t3/300/300", "album_name": "Eastern Dreams"},
    {"title": "Neon Tokyo", "artist": "Future Pulse", "duration": 189, "file_url": f"{SOUNDHELIX_BASE}/SoundHelix-Song-17.mp3", "image_url": "https://picsum.photos/seed/t17/300/300", "album_name": "Eastern Dreams"},
    {"title": "Purple Sunset", "artist": "Dream Valley", "duration": 201, "file_url": f"{SOUNDHELIX_BASE}/SoundHelix-Song-12.mp3", "image_url": "https://picsum.photos/seed/t12/300/300", "album_name": "Eastern Dreams"},
    # Extra tracks (without album)
    {"title": "Mountain High", "artist": "The Wild Ones", "duration": 214, "file_url": f"{SOUNDHELIX_BASE}/SoundHelix-Song-6.mp3", "image_url": "https://picsum.photos/seed/t6/300/300", "album_name": ""},
    {"title": "Desert Wind", "artist": "Sahara Sons", "duration": 178, "file_url": f"{SOUNDHELIX_BASE}/SoundHelix-Song-8.mp3", "image_url": "https://picsum.photos/seed/t8/300/300", "album_name": ""},
    {"title": "Winter Dreams", "artist": "Arctic Pulse", "duration": 195, "file_url": f"{SOUNDHELIX_BASE}/SoundHelix-Song-11.mp3", "image_url": "https://picsum.photos/seed/t11/300/300", "album_name": ""},
    {"title": "Midnight Blues", "artist": "Jazz Cats", "duration": 189, "file_url": f"{SOUNDHELIX_BASE}/SoundHelix-Song-18.mp3", "image_url": "https://picsum.photos/seed/t18/300/300", "album_name": ""},
]


@router.post("/fix-images")
def fix_external_images(db: Session = Depends(get_db)):
    """
    Скачать все внешние обложки (http/https) и заменить на локальные пути.
    Решает проблему с picsum.photos и другими внешними URL (CORS, таймауты).
    """
    PLACEHOLDER = "/album-placeholder.png"
    updated_albums = 0
    updated_tracks = 0
    for album in db.query(Album).all():
        if album.image_url and album.image_url.startswith("http"):
            local = _download_image(album.image_url) or PLACEHOLDER
            album.image_url = local
            updated_albums += 1
    for track in db.query(Track).all():
        if track.image_url and track.image_url.startswith("http"):
            local = _download_image(track.image_url) or PLACEHOLDER
            track.image_url = local
            updated_tracks += 1
    db.commit()
    return {
        "message": "External images downloaded and replaced with local paths",
        "albums_updated": updated_albums,
        "tracks_updated": updated_tracks,
    }


@router.post("/seed")
def seed_database(
    force: bool = Query(False, description="Перезаписать треки (обновить file_url)"),
    db: Session = Depends(get_db),
):
    """
    Загрузить тестовые данные в БД.
    
    force=false: если альбомы уже есть — возвращает hint, не перезаписывает.
    force=true: обновляет file_url/image_url у существующих треков (для перехода на SoundHelix).
    """
    try:
        # 1. Тестовый пользователь (test@example.com / test123)
        existing_user = db.query(AuthUser).filter(AuthUser.email == TEST_USER["email"]).first()
        if not existing_user:
            user = AuthUser(
                email=TEST_USER["email"],
                password_hash=get_password_hash(TEST_USER["password"]),
            )
            db.add(user)
            db.flush()
            profile = UserProfile(
                id=user.id,
                username=TEST_USER["username"],
                avatar_url="https://picsum.photos/seed/user/200/200",
                bio="Test user account",
            )
            db.add(profile)
            db.commit()
        else:
            # Обновляем хеш пароля (на случай устаревшего формата)
            existing_user.password_hash = get_password_hash(TEST_USER["password"])
            db.commit()
            user = existing_user

        # 2. Если альбомы уже есть и force=false — не перезаписываем
        existing_albums = db.query(Album).count()
        if existing_albums > 0 and not force:
            return {
                "message": "Database already seeded",
                "user": TEST_USER["email"],
                "albums": existing_albums,
                "hint": "Use ?force=true to update track URLs",
            }

        if force and existing_albums > 0:
            # force=true: обновляем URL треков и обложки альбомов (скачиваем локально)
            PLACEHOLDER = "/album-placeholder.png"
            albums = db.query(Album).all()
            for i, album in enumerate(albums):
                if i < len(TEST_ALBUMS):
                    img = _download_image(TEST_ALBUMS[i]["image_url"]) or PLACEHOLDER
                    album.image_url = img
            tracks = db.query(Track).all()
            for i, track in enumerate(tracks):
                if i < len(TEST_TRACKS):
                    track.file_url = TEST_TRACKS[i]["file_url"]
                    track.duration = TEST_TRACKS[i]["duration"]
                    img = _download_image(TEST_TRACKS[i]["image_url"]) or PLACEHOLDER
                    track.image_url = img
            db.commit()
            return {
                "message": "Track and album URLs updated successfully (images downloaded locally)",
                "albums_updated": len(albums),
                "tracks_updated": len(tracks),
            }

        # 3. Создаём альбомы и треки (по 3 трека на альбом)
        # Обложки скачиваем локально — picsum.photos ненадёжен из браузера (CORS, таймауты)
        PLACEHOLDER = "/album-placeholder.png"
        for idx, album_data in enumerate(TEST_ALBUMS):
            img_url = _download_image(album_data["image_url"]) or PLACEHOLDER
            album = Album(
                title=album_data["title"],
                artist=album_data["artist"],
                image_url=img_url,
                release_year=album_data["release_year"],
            )
            db.add(album)
            db.flush()

            # Добавляем треки для этого альбома
            start_idx = idx * 3
            for track_data in TEST_TRACKS[start_idx:start_idx + 3]:
                track_img = _download_image(track_data["image_url"]) or img_url
                track = Track(
                    title=track_data["title"],
                    artist=track_data["artist"],
                    duration=track_data["duration"],
                    file_url=track_data["file_url"],
                    image_url=track_img,
                    album_name=track_data.get("album_name", ""),
                    album_id=album.id
                )
                db.add(track)
            db.commit()

        # 4. Треки без альбома (синглы)
        for track_data in TEST_TRACKS[9:]:
            track_img = _download_image(track_data["image_url"]) or PLACEHOLDER
            track = Track(
                title=track_data["title"],
                artist=track_data["artist"],
                duration=track_data["duration"],
                file_url=track_data["file_url"],
                image_url=track_img,
                album_name=track_data.get("album_name", "")
            )
            db.add(track)
        db.commit()

        # 5. Тестовый плейлист с первыми 5 треками
        playlist = Playlist(
            title="My Favorite Songs",
            owner_id=user.id,
            is_public=True
        )
        db.add(playlist)
        db.flush()
        
        # Добавляем треки в плейлист
        tracks = db.query(Track).limit(5).all()
        for position, track in enumerate(tracks):
            playlist_track = PlaylistTrack(
                playlist_id=playlist.id,
                track_id=track.id,
                position=position
            )
            db.add(playlist_track)
        db.commit()

        return {
            "message": "Database seeded successfully",
            "user": TEST_USER["email"],
            "password": TEST_USER["password"],
            "albums": len(TEST_ALBUMS),
            "tracks": len(TEST_TRACKS),
            "playlists": 1
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
