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
    """
    Возвращает профиль пользователя, создавая его при первом обращении.

    Паттерн "ленивое создание" (lazy creation):
        - При регистрации сразу создаётся AuthUser
        - UserProfile создаётся этой функцией при первом вызове
        - Если профиль уже есть — просто возвращаем его

    Почему отдельная функция, а не создание в момент регистрации?
        Это позволяет создать профиль в любой момент, даже если при регистрации
        что-то пошло не так. Также используется в auth.py и player.py.

    Алгоритм выбора username:
        1. Берём initial_username из AuthUser (то что пользователь ввёл при регистрации)
        2. Если занято — добавляем суффикс _1, _2, ... пока не найдём свободное
        3. Fallback: если initial_username пустой — используем часть email до @
    """
    # Проверяем, есть ли уже профиль
    profile = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if profile:
        return profile  # профиль существует — возвращаем как есть

    # Профиля нет — создаём
    auth_user = db.query(AuthUser).filter(AuthUser.id == user_id).first()
    if not auth_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Определяем базовый username
    base_username = (
        auth_user.initial_username
        if getattr(auth_user, "initial_username", None)
        else auth_user.email.split("@")[0]
    )
    base_username = base_username or "user"

    # Ищем свободный username (добавляем суффикс если занят)
    username = base_username
    counter = 0
    while db.query(UserProfile).filter(UserProfile.username == username).first():
        counter += 1
        username = f"{base_username}_{counter}"

    # Создаём профиль с найденным свободным username
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
    """
    Профиль текущего пользователя.

    _ensure_profile создаёт профиль если его нет.
    Это нужно для пользователей, зарегистрированных через OAuth или
    созданных до введения UserProfile.
    """
    profile = _ensure_profile(user_id, db)
    return profile


@router.put("/me", response_model=UserProfileResponse)
def update_my_profile(
    update_data: UserUpdate,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Обновить профиль текущего пользователя (имя, аватар, bio).

    exclude_unset=True — обновляем только переданные поля.
    Это позволяет обновить только аватар, не трогая username.
    """
    profile = _ensure_profile(user_id, db)
    data = update_data.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/", response_model=list[UserProfileResponse])
def get_all_users(
    _: UUID = Depends(get_current_user_id),  # только авторизованные
    db: Session = Depends(get_db),
):
    """
    Список всех пользователей (публичные данные профиля).

    Используется в чате для отображения списка пользователей.
    Возвращает UserProfileResponse — без email (email в auth_users, не в user_profiles).
    """
    profiles = db.query(UserProfile).all()
    return profiles


@router.get("/messages/{user_id}", response_model=list[MessageResponse])
def get_messages(
    user_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    История переписки с пользователем.

    Возвращает все сообщения, где один из участников — user_id из URL.
    Сортировка по времени (старые первыми) — удобно для отображения в чате.

    Используется при открытии диалога: подгружаем историю из БД,
    последующие сообщения приходят в реальном времени через WebSocket.
    """
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
    """Получить публичный профиль пользователя по ID."""
    profile = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return profile
