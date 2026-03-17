"""Player / History Service — фиксация прослушивания треков."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user_id
from app.models.listening_history import ListeningHistory
from app.models.track import Track
from app.routes.users import _ensure_profile
from app.schemas import PlayRecord, TrackResponse

router = APIRouter()


@router.get("/health")
def player_health():
    """Health check для Player / History Service."""
    return {"status": "ok", "service": "player"}


@router.post("/play")
def record_play(
    body: PlayRecord,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Зафиксировать прослушивание трека.

    Вызывается frontend при каждом нажатии кнопки Play.
    Каждое прослушивание — отдельная запись в listening_history.
    Записи накапливаются и используются сервисом рекомендаций:
        - анализируются любимые артисты
        - уже прослушанные треки исключаются из рекомендаций

    _ensure_profile гарантирует наличие профиля (в listening_history
    ссылка на user_profiles, а не auth_users).
    """
    # Убеждаемся, что профиль существует (lazy creation)
    profile = _ensure_profile(user_id, db)

    # Проверяем, что трек существует в БД
    track = db.query(Track).filter(Track.id == body.track_id).first()
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found",
        )

    # Создаём запись в истории. played_at проставляется автоматически (server_default).
    record = ListeningHistory(user_id=profile.id, track_id=body.track_id)
    db.add(record)
    db.commit()
    db.refresh(record)

    return {"id": record.id, "track_id": body.track_id, "played_at": record.played_at}


@router.get("/history")
def get_history(
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    История прослушиваний текущего пользователя.

    Возвращает записи в порядке убывания времени (новые первыми).
    Каждая запись содержит данные самого трека (через relationship r.track).
    """
    profile = _ensure_profile(user_id, db)

    records = (
        db.query(ListeningHistory)
        .filter(ListeningHistory.user_id == profile.id)
        .order_by(ListeningHistory.played_at.desc())  # новые прослушивания первыми
        .all()
    )

    # Формируем ответ вручную, добавляя данные трека к каждой записи
    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "track_id": r.track_id,
            "played_at": r.played_at,
            "track": TrackResponse.model_validate(r.track),  # вложенный объект трека
        }
        for r in records
    ]
