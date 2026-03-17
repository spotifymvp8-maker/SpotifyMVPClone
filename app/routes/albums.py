"""Album routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_admin_user_id
from app.models.album import Album
from app.models.track import Track
from app.schemas import AlbumCreate, AlbumResponse, AlbumUpdate

router = APIRouter()


# Два декоратора — исправление 307-редиректа (см. songs.py за подробностями)
@router.get("", response_model=list[AlbumResponse])
@router.get("/", response_model=list[AlbumResponse])
def get_all_albums(db: Session = Depends(get_db)):
    """
    Список всех альбомов.

    AlbumResponse включает поле songs (список треков).
    SQLAlchemy загружает треки лениво через relationship("songs").
    Для больших данных стоит добавить пагинацию.
    """
    albums = db.query(Album).all()
    return albums


@router.get("/{album_id}", response_model=AlbumResponse)
def get_album(album_id: UUID, db: Session = Depends(get_db)):
    """
    Альбом по ID с вложенными треками.

    Треки подгружаются автоматически через lazy loading (Album.songs relationship).
    """
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Album not found"
        )
    return album


@router.post("", response_model=AlbumResponse)
@router.post("/", response_model=AlbumResponse)
def create_album(
    album_data: AlbumCreate,
    _: UUID = Depends(get_admin_user_id),
    db: Session = Depends(get_db),
):
    """Создать альбом. Только для администраторов."""
    album = Album(**album_data.model_dump())
    db.add(album)
    db.commit()
    db.refresh(album)
    return album


@router.put("/{album_id}", response_model=AlbumResponse)
def update_album(
    album_id: UUID,
    album_data: AlbumUpdate,
    _: UUID = Depends(get_admin_user_id),
    db: Session = Depends(get_db),
):
    """
    Обновить альбом. Только для администраторов.

    Важно: при изменении title альбома нужно обновить album_name во всех треках.
    Это сделано здесь — денормализованное поле синхронизируется вручную.
    """
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Album not found"
        )

    update_data = album_data.model_dump(exclude_unset=True)

    # Если меняется название альбома — обновляем денормализованное поле album_name во всех треках
    if "title" in update_data:
        db.query(Track).filter(Track.album_id == album_id).update(
            {"album_name": update_data["title"]}
        )

    for field, value in update_data.items():
        setattr(album, field, value)

    db.commit()
    db.refresh(album)
    return album


@router.delete("/{album_id}")
def delete_album(
    album_id: UUID,
    _: UUID = Depends(get_admin_user_id),
    db: Session = Depends(get_db),
):
    """
    Удалить альбом. Только для администраторов.

    Треки НЕ удаляются — album_id в треках становится NULL (SET NULL в FK).
    Треки остаются как синглы, не исчезают из плейлистов пользователей.
    """
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Album not found"
        )

    db.delete(album)
    db.commit()
    return {"message": "Album deleted successfully"}
