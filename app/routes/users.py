"""User routes — User Service: профили пользователей."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user_id
from app.models.auth_user import AuthUser
from app.models.user_profile import UserProfile
from app.models.message import Message
from app.schemas import UserProfileResponse, UserUpdate, MessageResponse

router = APIRouter()


def _ensure_profile(user_id: UUID, db: Session) -> UserProfile:
    """Создать профиль при первом обращении (из initial_username или email)."""
    profile = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if profile:
        return profile
    auth_user = db.query(AuthUser).filter(AuthUser.id == user_id).first()
    if not auth_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    base_username = (
        auth_user.initial_username
        if getattr(auth_user, "initial_username", None)
        else auth_user.email.split("@")[0]
    )
    base_username = base_username or "user"
    username = base_username
    counter = 0
    while db.query(UserProfile).filter(UserProfile.username == username).first():
        counter += 1
        username = f"{base_username}_{counter}"
    profile = UserProfile(id=user_id, username=username, avatar_url=None, bio="")
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/health")
def user_health():
    """Health check для User Service."""
    return {"status": "ok", "service": "user"}


@router.get("/me", response_model=UserProfileResponse)
def get_my_profile(
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Получить профиль текущего пользователя (создаётся при первом обращении)."""
    profile = _ensure_profile(user_id, db)
    return profile


@router.put("/me", response_model=UserProfileResponse)
def update_my_profile(
    update_data: UserUpdate,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Обновить профиль текущего пользователя."""
    profile = _ensure_profile(user_id, db)
    data = update_data.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/", response_model=list[UserProfileResponse])
def get_all_users(
    _: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Получить всех пользователей (только публичные данные профиля)."""
    profiles = db.query(UserProfile).all()
    return profiles


@router.get("/messages/{user_id}", response_model=list[MessageResponse])
def get_messages(
    user_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Получить сообщения с пользователем."""
    messages = db.query(Message).filter(
        (Message.sender_id == user_id) | (Message.receiver_id == user_id)
    ).order_by(Message.created_at).all()
    return messages


@router.get("/{user_id}", response_model=UserProfileResponse)
def get_user(
    user_id: UUID,
    _: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Получить профиль пользователя по ID (только публичные данные)."""
    profile = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return profile
