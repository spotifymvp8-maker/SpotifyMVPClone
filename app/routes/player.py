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
    """Записать событие прослушивания трека (при каждом play)."""
    profile = _ensure_profile(user_id, db)
    track = db.query(Track).filter(Track.id == body.track_id).first()
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found",
        )
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
    """Получить историю прослушиваний текущего пользователя."""
    profile = _ensure_profile(user_id, db)
    records = (
        db.query(ListeningHistory)
        .filter(ListeningHistory.user_id == profile.id)
        .order_by(ListeningHistory.played_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "track_id": r.track_id,
            "played_at": r.played_at,
            "track": TrackResponse.model_validate(r.track),
        }
        for r in records
    ]
