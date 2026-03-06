"""Auth routes."""

from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_db
from app.models.auth_user import AuthUser
from app.models.user_profile import UserProfile
from app.schemas import UserCreate, UserLogin, UserResponse, Token, TokenWithUser
from app.utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)

router = APIRouter()
security = HTTPBearer()


@router.get("/health")
def auth_health():
    """Проверка работоспособности сервиса аутентификации."""
    return {"status": "ok", "service": "auth"}


@router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Регистрация: Auth создаёт только auth_users. Профиль создаёт User Service при первом GET /users/me."""
    existing_user = db.query(AuthUser).filter(AuthUser.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    existing_profile = db.query(UserProfile).filter(
        UserProfile.username == user_data.username
    ).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    hashed_password = get_password_hash(user_data.password)
    user = AuthUser(
        email=user_data.email,
        password_hash=hashed_password,
        initial_username=user_data.username,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    from app.routes.users import _ensure_profile

    profile = _ensure_profile(user.id, db)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "username": profile.username,
            "avatar_url": profile.avatar_url,
        },
    }


@router.post("/login", response_model=TokenWithUser)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Вход пользователя."""
    user = db.query(AuthUser).filter(AuthUser.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    from app.routes.users import _ensure_profile

    profile = _ensure_profile(user.id, db)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "username": profile.username,
            "avatar_url": profile.avatar_url,
        },
    }


@router.post("/logout")
def logout():
    """Выход пользователя."""
    # В production здесь нужно инвалидировать токен
    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=Token)
def refresh_token(refresh_data: dict, db: Session = Depends(get_db)):
    """Обновление токена."""
    refresh_token = refresh_data.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required"
        )
    
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    user = db.query(AuthUser).filter(AuthUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Create new tokens
    new_access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {"access_token": new_access_token, "refresh_token": new_refresh_token}


@router.get("/me", response_model=UserResponse)
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Получение текущего пользователя."""
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_id = payload.get("sub")
    user = db.query(AuthUser).filter(AuthUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    from app.routes.users import _ensure_profile

    profile = _ensure_profile(UUID(user_id), db)
    return {
        "id": user.id,
        "email": user.email,
        "username": profile.username,
        "avatar_url": profile.avatar_url,
        "created_at": user.created_at,
    }
