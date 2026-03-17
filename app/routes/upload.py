"""
Upload routes — загрузка изображений и аудио с компьютера админа.

POST /api/upload/image — обложка альбома или трека (jpg, png, webp)
POST /api/upload/audio — аудиофайл трека (mp3)

Файлы сохраняются в media/images/ и media/songs/.
Возвращается URL вида /media/images/xxx.jpg для использования в album/track.
"""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from uuid import UUID

from app.dependencies import get_admin_user_id

router = APIRouter()

# Пути к папкам с медиафайлами.
# Path(__file__).resolve().parent — папка routes/
# .parent.parent.parent — корень проекта (три уровня вверх: routes → app → проект)
# / "media" — папка media/ в корне
MEDIA_DIR  = Path(__file__).resolve().parent.parent.parent / "media"
IMAGES_DIR = MEDIA_DIR / "images"
SONGS_DIR  = MEDIA_DIR / "songs"

# Разрешённые MIME-типы файлов (первая линия защиты от нежелательных файлов)
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg", "image/pjpeg"}
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/mp3", "audio/wav", "audio/ogg"}


def _ensure_dirs():
    """Создать папки media/images и media/songs если их нет (при первом запуске)."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    SONGS_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/image")
def upload_image(
    file: UploadFile = File(...),     # UploadFile — загружаемый файл (multipart/form-data)
    _: UUID = Depends(get_admin_user_id),  # только администраторы могут загружать файлы
):
    """
    Загрузить изображение (обложка альбома или трека).

    Принимает: jpg, png, webp.
    Возвращает: {"url": "/media/images/abc123.jpg"}

    URL сохраняется в album.image_url или track.image_url.
    Nginx отдаёт файл напрямую из /media при запросе этого URL.

    Имя файла генерируется через uuid4().hex — случайная строка без конфликтов.
    Это предотвращает: перезапись чужих файлов, угадывание имён файлов.
    """
    ct = (file.content_type or "").lower()

    # Проверка MIME-типа — не принимаем произвольные файлы
    if ct not in ALLOWED_IMAGE_TYPES and not any(t in ct for t in ("jpeg", "jpg", "png", "webp")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый тип файла ({ct}). Разрешены: jpg, png, webp",
        )

    _ensure_dirs()

    # Определяем расширение по MIME-типу
    ext = ".jpg" if "jpeg" in ct or "jpg" in ct else ".png" if "png" in ct else ".webp"

    # uuid4().hex — случайная строка из 32 hex-символов (без дефисов)
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = IMAGES_DIR / filename

    # Читаем файл из памяти и пишем на диск
    with open(filepath, "wb") as f:
        content = file.file.read()
        f.write(content)

    # Возвращаем URL, который клиент сохранит в album_id или track_id
    return {"url": f"/media/images/{filename}"}


@router.post("/audio")
def upload_audio(
    file: UploadFile = File(...),
    _: UUID = Depends(get_admin_user_id),
):
    """
    Загрузить аудиофайл (трек).

    Принимает: mp3, wav, ogg.
    Возвращает: {"url": "/media/songs/abc123.mp3"}

    URL сохраняется в track.file_url.
    Nginx проксирует запросы /media/songs/* на backend (не кэширует как статику!).
    """
    ct_audio = (file.content_type or "").lower()

    if ct_audio not in ALLOWED_AUDIO_TYPES and not any(t in ct_audio for t in ("mpeg", "mp3", "wav", "ogg")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый тип файла ({ct_audio}). Разрешены: mp3, wav, ogg",
        )

    _ensure_dirs()

    ext = ".mp3" if "mpeg" in ct_audio or "mp3" in ct_audio else ".wav" if "wav" in ct_audio else ".ogg"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = SONGS_DIR / filename

    with open(filepath, "wb") as f:
        content = file.file.read()
        f.write(content)

    return {"url": f"/media/songs/{filename}"}
