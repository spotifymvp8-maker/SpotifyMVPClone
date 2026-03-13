"""
Подключение к PostgreSQL и управление сессиями SQLAlchemy.

- engine: пул соединений к БД
- SessionLocal: фабрика сессий (каждый запрос = новая сессия)
- Base: базовый класс для ORM-моделей (app.models.*)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # Проверка соединения перед использованием
    echo=False,           # True — логировать все SQL-запросы (для отладки)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()  # Все модели наследуются от Base


def get_db():
    """
    Dependency для FastAPI: при каждом запросе создаётся сессия, после ответа — закрывается.
    Использование: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Создание всех таблиц по моделям (альтернатива Alembic миграциям)."""
    import app.models  # noqa: F401 — загрузка моделей для регистрации в metadata

    Base.metadata.create_all(bind=engine)
