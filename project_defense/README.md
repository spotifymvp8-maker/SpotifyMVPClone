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
| `01_architecture-overview/` | architecture-overview.png, **-detailed.png** | Общая архитектура: Docker, Nginx, Frontend, Backend, PostgreSQL |
| `02_architecture-request-flow/` | architecture-request-flow.png, **-detailed.png** | Маршрутизация запросов: /, /api/*, /media/*, /ws/* |
| `03_backend-structure/` | backend-structure.png, **-detailed.png** | Структура app/: main, config, database, models, routes |
| `04_backend-database-layer/` | backend-database-layer.png, **-detailed.png** | SQLAlchemy: Engine, Session, get_db, ORM-модели |
| `05_backend-routes/` | backend-routes.png, **-detailed.png** | Роутеры API и их префиксы |
| `06_backend-request-flow/` | backend-request-flow.png, **-detailed.png** | Обработка HTTP: CORS → Router → Dependencies → Handler |
| `07_backend-auth-flow/` | backend-auth-flow.png, **-detailed.png** | JWT: логин и защищённые эндпоинты |
| `13_jamendo-architecture/` | jamendo-api-flow.png | Интеграция с Jamendo API: поиск, превью, импорт |

### Frontend — диаграммы

| Папка | Изображения | Описание |
|-------|-------------|----------|
| `08_frontend-structure/` | frontend-structure.png | Структура frontend/src: pages, layout, stores, components |
| `09_frontend-routes/` | frontend-routes.png | Маршрутизация React Router, защита страниц |
| `10_frontend-auth-flow/` | frontend-auth-flow.png | Аутентификация: login, 401, refresh token |
| `11_frontend-state-flow/` | frontend-state-flow.png | Zustand stores и потоки данных |
| `12_frontend-player-flow/` | frontend-player-flow.png | Плеер: queue, AudioPlayer, Shuffle, Repeat |

### Иллюстрации сессии

| Папка | Описание |
|-------|----------|
| `14_changelog-illustrations/` | Иллюстрации изменений: автозапуск, бургер-меню, Liked Songs, жанры, обложки |

---

## Использование

- Диаграммы — для слайдов презентации
- README в каждой папке — для подготовки к объяснению схемы
- `DEFENSE_SPEECH.md` — во время устного выступления
- `DEFENSE_QA.md` — для ответов на вопросы комиссии
