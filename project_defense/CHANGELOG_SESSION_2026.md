# Сводный отчёт об изменениях проекта Spotify Clone — 2026

Проект: **Spotify Clone** (FastAPI + React + PostgreSQL + Docker)

---

## Содержание

1. [Обзор изменений](#обзор-изменений)
2. [Треки по категориям (жанрам)](#1-треки-по-категориям-жанрам)
3. [Автозапуск и ярлыки](#2-автозапуск-и-ярлыки)
4. [Мобильная адаптация и бургер-меню](#3-мобильная-адаптация-и-бургер-меню)
5. [Обложки альбомов](#4-обложки-альбомов)
6. [Liked Songs / My Favorite Songs](#5-liked-songs--my-favorite-songs)
7. [Иллюстрации](#иллюстрации)
8. [Изменённые файлы](#изменённые-файлы)

---

## Обзор изменений

| # | Изменение | Описание |
|---|-----------|----------|
| 1 | Треки по категориям | Главная и поиск — секции по жанрам (Rock, Pop, Jazz и т.д.) |
| 2 | Автозапуск | Batch-скрипты и ярлыки для запуска в Docker и отдельном окне |
| 3 | Мобильная адаптация | Бургер-меню, боковая панель от 1024px, все альбомы в сайдбаре |
| 4 | Обложки альбомов | Скачивание при seed, эндпоинт fix-images для существующих данных |
| 5 | Liked Songs | Виртуальный плейлист, My Favorite Songs показывает любимые треки |

---

## 1. Треки по категориям (жанрам)

### Backend

- **Эндпоинт** `GET /api/songs/browse-by-genre` — возвращает треки, сгруппированные по жанрам
- **Лимиты**: DEFAULT_LIMIT 100, MAX_LIMIT 500
- **Featured / Made For You / Trending**: по 12 треков (было 5–6)

### Frontend

- **Главная страница**: секции по жанрам под Made For You, Featured, Trending
- **Страница поиска**: при отсутствии запроса — треки по категориям (до 25 на жанр)
- **Типы**: в `Song` добавлено поле `genre`

---

## 2. Автозапуск и ярлыки

### Файлы

| Файл | Назначение |
|------|------------|
| `Spotify Clone.bat` | Полный запуск: Docker + браузер в режиме приложения |
| `test-app-window.bat` | Только окно приложения (Docker должен быть запущен) |
| `create_shortcut.vbs` | Создание ярлыков на рабочем столе |
| `spotify-clone-icon.ico` | Иконка приложения |
| `create_icon.py` | Генерация .ico из PNG |

### Ярлыки на рабочем столе

- **Spotify Clone** — полный запуск (Docker + приложение)
- **Spotify Clone (App)** — только окно приложения

### Логика `Spotify Clone.bat`

1. Проверка Docker
2. Запуск контейнеров (`docker compose up -d`)
3. Ожидание 15 секунд
4. Открытие в Edge/Chrome в режиме `--app` (отдельное окно без вкладок)

---

## 3. Мобильная адаптация и бургер-меню

### Боковая панель

- **Было**: видна от 768px (md), узкая 88px на md
- **Стало**: видна от 1024px (lg), всегда полная 280px

### Бургер-меню

- **Кнопка** ☰ в Topbar — видна при ширине < 1024px
- **MobileNavDrawer** — выдвижная панель слева с:
  - Home, Search, Your Library
  - Список всех альбомов с обложками и прокруткой
- **useMobileMenuStore** — состояние открытия/закрытия

### Альбомы в сайдбаре

- **Было**: `albums.slice(0, 8)` — только 8 альбомов
- **Стало**: все альбомы с прокруткой
- **Fallback**: `onError` → placeholder при ошибке загрузки изображения

---

## 4. Обложки альбомов

### Проблема

Обложки с picsum.photos не загружались (CORS, таймауты).

### Решение

**При seed** (`app/routes/seed.py`):
- Функция `_download_image(url)` — скачивает изображение и сохраняет в `media/images/`
- Альбомы и треки создаются с локальными URL (`/media/images/xxx.jpg`)

**Эндпоинт** `POST /api/seed/fix-images`:
- Находит все альбомы и треки с внешними URL (http/https)
- Скачивает изображения локально
- Заменяет URL в БД

**Использование** (после перезапуска backend):
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/seed/fix-images" -Method POST
```

---

## 5. Liked Songs / My Favorite Songs

### Проблема

Пользователь ставил ♥ на треках, но они не отображались в «My Favorite Songs».

### Решение

**Виртуальный плейлист**:
- Карточка **«Liked Songs»** — первая в разделе Playlists, показывает количество любимых треков
- Плейлист **«My Favorite Songs»** — отображает `likedSongs` из `useLibraryStore` вместо треков из БД
- При клике — воспроизведение любимых треков

**useLibraryStore**:
- Сравнение ID через `String(id)` для совместимости UUID/string
- `persist` в localStorage — данные сохраняются между сессиями

---

## Иллюстрации

См. папку `project_defense/14_changelog-illustrations/`:

| Файл | Описание |
|------|-----------|
| `architecture-launch-flow.png` | Схема автозапуска: ярлык → Docker → окно приложения |
| `mobile-burger-menu-flow.png` | Бургер-меню и мобильная навигация |
| `liked-songs-flow.png` | Поток данных Liked Songs / My Favorite Songs |
| `tracks-by-genre-flow.png` | Треки по категориям (жанрам) |
| `album-covers-fix-flow.png` | Исправление обложек альбомов |

---

## Изменённые файлы

### Backend

| Файл | Изменения |
|------|-----------|
| `app/routes/songs.py` | browse-by-genre, лимиты, Featured/Made For You/Trending |
| `app/routes/seed.py` | _download_image, fix-images, скачивание обложек при seed |

### Frontend

| Файл | Изменения |
|------|-----------|
| `frontend/src/pages/home/HomePage.tsx` | Секции по жанрам |
| `frontend/src/pages/search/SearchPage.tsx` | Треки по категориям |
| `frontend/src/pages/library/LibraryPage.tsx` | Liked Songs карточка, My Favorite Songs виртуальный |
| `frontend/src/layout/MainLayout.tsx` | MobileNavDrawer, breakpoint lg |
| `frontend/src/layout/components/LeftSidebar.tsx` | Все альбомы, onError для изображений |
| `frontend/src/layout/components/MobileNavDrawer.tsx` | Новый компонент |
| `frontend/src/components/Topbar.tsx` | Кнопка бургер-меню |
| `frontend/src/stores/useMusicStore.ts` | fetchTracksByGenre |
| `frontend/src/stores/useLibraryStore.ts` | String(id) для сравнения |
| `frontend/src/stores/useMobileMenuStore.ts` | Новый стор |
| `frontend/src/types/index.ts` | genre в Song |

### Скрипты и ресурсы

| Файл | Назначение |
|------|------------|
| `Spotify Clone.bat` | Автозапуск |
| `test-app-window.bat` | Окно приложения |
| `create_shortcut.vbs` | Создание ярлыков |
| `create_icon.py` | Генерация иконки |
| `spotify-clone-icon.ico` | Иконка |
| `spotify-clone-icon.png` | Исходное изображение |

---

*Документ создан 18.03.2026. Проект: Spotify Clone.*
