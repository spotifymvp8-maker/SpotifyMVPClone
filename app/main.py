"""
FastAPI приложение Spotify Clone.

Точка входа: uvicorn app.main:app --reload

Структура:
    - CORS: разрешает запросы с frontend (localhost:3000 и др.)
    - Роутеры: auth, songs, albums, playlists, search, seed и т.д.
    - /health — проверка подключения к PostgreSQL
"""

import os
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from fastapi.staticfiles import StaticFiles

from app.routes import auth, songs, albums, users, websocket, playlists, seed, search, player, recommendations, upload

app = FastAPI(title="Spotify Clone API")

# CORS: разрешает запросы с указанных origins (в production — ограничить!)
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://127.0.0.1:3000,http://127.0.0.1:3001,http://127.0.0.1:3002")
ALLOWED_ORIGINS = [o.strip() for o in CORS_ORIGINS.split(",")] if CORS_ORIGINS else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры — каждый обрабатывает свой набор endpoints
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(songs.router, prefix="/api/songs", tags=["Songs"])
app.include_router(albums.router, prefix="/api/albums", tags=["Albums"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(playlists.router, prefix="/api/playlists", tags=["Playlists"])
app.include_router(seed.router, prefix="/api/seed", tags=["Seed"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(player.router, prefix="/api/player", tags=["Player"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(websocket.router, tags=["WebSocket"])

# Раздача загруженных медиафайлов (images, songs)
_media_dir = Path(__file__).resolve().parent.parent / "media"
_media_dir.mkdir(parents=True, exist_ok=True)
(_media_dir / "images").mkdir(exist_ok=True)
(_media_dir / "songs").mkdir(exist_ok=True)
app.mount("/media", StaticFiles(directory=str(_media_dir)), name="media")


@app.get("/")
def root():
    """Корневой endpoint — базовая информация об API."""
    return {"message": "Spotify Clone API", "status": "ok"}


@app.get("/health")
def health(db: Session = Depends(get_db)):
    """Проверка подключения к PostgreSQL (SELECT 1)."""
    try:
        db.execute(text("SELECT 1"))
        return {"database": "ok"}
    except Exception as e:
        return {"database": "error", "detail": str(e)}
