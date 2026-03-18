# Project Defense Materials

**Project:** Spotify Clone  
**Purpose:** Materials for the project defense presentation

---

## Documents (корень папки)

| File | Description |
|------|-------------|
| `DEFENSE_SPEECH.md` | Речь для защиты (Russian) |
| `DEFENSE_QA.md` | 100 вопросов и ответов (Russian) |
| `ARCHITECTURE_DIAGRAMS.md` | Сводное описание всех диаграмм |
| `FRONTEND_OVERVIEW.md` | Обзор Frontend: React, Zustand, маршруты, потоки |
| `TECH_OVERVIEW.md` | Обзор технологий всего проекта |
| `WORK_LOG_13_03_2026.md` | Отчёт о работе: поиск, библиотека, кнопки ♥ |
| `WORK_LOG_16_03_2026.md` | Отчёт о работе: Shuffle, Repeat, Jamendo API, диаграммы |

---

## Диаграммы (каждая в отдельной папке)

Каждая папка содержит **изображение** и **README.md** с подробным описанием: что изображено и как это работает.

| Папка | Изображения | Описание |
|-------|-------------|----------|
| `architecture-overview/` | architecture-overview.png, **-detailed.png** | Общая архитектура: Docker, Nginx, Frontend, Backend, PostgreSQL |
| `architecture-request-flow/` | architecture-request-flow.png, **-detailed.png** | Маршрутизация запросов: /, /api/*, /media/*, /ws/* |
| `backend-structure/` | backend-structure.png, **-detailed.png** | Структура app/: main, config, database, models, routes |
| `backend-request-flow/` | backend-request-flow.png, **-detailed.png** | Обработка HTTP: CORS → Router → Dependencies → Handler |
| `backend-database-layer/` | backend-database-layer.png, **-detailed.png** | SQLAlchemy: Engine, Session, get_db, ORM-модели |
| `backend-auth-flow/` | backend-auth-flow.png, **-detailed.png** | JWT: логин и защищённые эндпоинты |
| `backend-routes/` | backend-routes.png, **-detailed.png** | Роутеры API и их префиксы |
| `jamendo-architecture/` | jamendo-api-flow.png | Интеграция с Jamendo API: поиск, превью, импорт |

### Frontend — диаграммы

| Папка | Изображения | Описание |
|-------|-------------|----------|
| `frontend-structure/` | frontend-structure.png | Структура frontend/src: pages, layout, stores, components |
| `frontend-routes/` | frontend-routes.png | Маршрутизация React Router, защита страниц |
| `frontend-state-flow/` | frontend-state-flow.png | Zustand stores и потоки данных |
| `frontend-auth-flow/` | frontend-auth-flow.png | Аутентификация: login, 401, refresh token |
| `frontend-player-flow/` | frontend-player-flow.png | Плеер: queue, AudioPlayer, Shuffle, Repeat |

---

## Использование

- Диаграммы — для слайдов презентации
- README в каждой папке — для подготовки к объяснению схемы
- `DEFENSE_SPEECH.md` — во время устного выступления
- `DEFENSE_QA.md` — для ответов на вопросы комиссии
