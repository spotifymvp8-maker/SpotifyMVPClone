# Обзор Frontend — React + TypeScript + Vite

Полное описание архитектуры, компонентов и потоков данных фронтенд-приложения Spotify Clone.

---

## Содержание

1. [Общая архитектура](#1-общая-архитектура)
2. [Структура папки frontend](#2-структура-папки-frontend)
3. [Маршрутизация (React Router)](#3-маршрутизация-react-router)
4. [Управление состоянием (Zustand)](#4-управление-состоянием-zustand)
5. [Поток аутентификации](#5-поток-аутентификации)
6. [Поток воспроизведения (Player)](#6-поток-воспроизведения-player)
7. [Диаграммы и подробная документация](#7-диаграммы-и-подробная-документация)
8. [Ключевые библиотеки](#8-ключевые-библиотеки)
9. [Дизайн-система](#9-дизайн-система)

---

## 1. Общая архитектура

```
main.tsx
    │
    ├── AuthProvider (проверка токена при загрузке)
    │       │
    │       └── BrowserRouter
    │               │
    │               └── App.tsx
    │                       │
    │                       ├── Routes (React Router)
    │                       │   ├── /login → LoginPage
    │                       │   ├── MainLayout (Outlet)
    │                       │   │   ├── / → HomePage
    │                       │   │   ├── /search → SearchPage
    │                       │   │   ├── /library → LibraryPage
    │                       │   │   ├── /albums/:id → AlbumPage
    │                       │   │   └── ...
    │                       │   ├── /admin → AdminPage
    │                       │   └── /presentation → PresentationPage
    │                       │
    │                       └── Toaster (react-hot-toast)
```

**Точка входа:** `main.tsx` → `AuthProvider` → `BrowserRouter` → `App.tsx`

**Layout:** `MainLayout` оборачивает все основные страницы и содержит:
- `LeftSidebar` — навигация, плейлисты
- `Outlet` — контент страницы
- `ArtistInfoSidebar` — панель «Об исполнителе»
- `AudioPlayer` — скрытый `<audio>` элемент
- `PlaybackControls` — плеер внизу экрана

---

## 2. Структура папки frontend

```
frontend/
│
├── src/
│   ├── pages/              ← Страницы (по одному маршруту)
│   │   ├── home/           — Главная (Featured, Trending, Made for You)
│   │   ├── search/         — Поиск (debounce, жанры, Jamendo)
│   │   ├── library/       — Your Library (альбомы, любимые треки)
│   │   ├── album/          — Страница альбома
│   │   ├── admin/          — Админ-панель (вне MainLayout)
│   │   ├── login/          — Вход и регистрация
│   │   ├── AddPlaylist/    — Создание плейлиста
│   │   ├── playlistEditPage/ — Редактирование плейлиста
│   │   ├── presentation/   — Презентация проекта
│   │   └── 404/            — Not Found
│   │
│   ├── layout/             ← Обёртка страниц
│   │   ├── MainLayout.tsx
│   │   └── components/
│   │       ├── LeftSidebar.tsx
│   │       ├── PlaybackControls.tsx
│   │       ├── AudioPlayer.tsx
│   │       └── ArtistInfoSidebar.tsx
│   │
│   ├── stores/             ← Zustand (глобальное состояние)
│   │   ├── useAuthStore.ts
│   │   ├── usePlayerStore.ts
│   │   ├── useMusicStore.ts
│   │   ├── useArtistStore.ts
│   │   └── useLibraryStore.ts
│   │
│   ├── components/         ← Переиспользуемые компоненты
│   │   ├── Topbar.tsx
│   │   ├── ui/             — Radix UI + Tailwind
│   │   │   ├── button.tsx, input.tsx, slider.tsx
│   │   │   ├── dialog.tsx, avatar.tsx, scroll-area.tsx
│   │   │   ├── PlaylistCard.tsx
│   │   │   ├── AddToPlayListModal.tsx
│   │   │   └── JamendoImportModal.tsx
│   │   └── skeletons/
│   │       └── Skeleton.tsx
│   │
│   ├── lib/                ← Утилиты
│   │   ├── axios.ts        — axios + JWT interceptor + 401 refresh
│   │   └── utils.ts        — cn() для Tailwind
│   │
│   ├── providers/
│   │   └── AuthProvider.tsx — checkAuth, auth:logout, auth:token-refreshed
│   │
│   ├── types/
│   │   └── index.ts        — Song, Album, Playlist, User, SearchResult
│   │
│   ├── App.tsx             ← Роутинг
│   ├── main.tsx            ← Точка входа
│   ├── index.css           ← Tailwind + глобальные стили
│   └── App.css             ← CSS-переменные
│
├── public/                 ← Статика
├── package.json
├── vite.config.ts          ← Proxy /api, /media, /ws → backend
├── tailwind.config.js      ← Spotify-цвета, шрифты
└── index.html
```

Подробнее: [frontend-structure/README.md](./08_frontend-structure/README.md)

---

## 3. Маршрутизация (React Router)

| Путь | Страница | Layout | Защита |
|------|----------|--------|--------|
| `/login` | LoginPage | — | Редирект на `/` если авторизован |
| `/` | HomePage | MainLayout | Требуется auth |
| `/search` | SearchPage | MainLayout | Требуется auth |
| `/library` | LibraryPage | MainLayout | Требуется auth |
| `/playlists/new` | NewPlaylistPage | MainLayout | Требуется auth |
| `/playlists/:id` | PlaylistEditPage | MainLayout | — |
| `/albums/:albumId` | AlbumPage | MainLayout | Требуется auth |
| `/admin` | AdminPage | — | Требуется auth |
| `/presentation` | PresentationPage | — | Публичный |
| `*` | NotFoundPage | MainLayout | — |

Подробнее: [frontend-routes/README.md](./09_frontend-routes/README.md)

---

## 4. Управление состоянием (Zustand)

| Store | Назначение |
|-------|-----------|
| **useAuthStore** | user, tokens, isAuthenticated; login, register, logout, refreshToken, checkAuth |
| **usePlayerStore** | currentSong, queue, isPlaying; playAlbum, setCurrentSong, togglePlay, playNext, playPrevious; shuffle, repeat |
| **useMusicStore** | albums, featured/trending/madeForYou; fetchAlbums, search, CRUD альбомов/треков, upload, playlists |
| **useArtistStore** | selectedArtist, isSidebarOpen; openArtist, closeArtist, toggleSidebar |
| **useLibraryStore** | savedAlbums, likedSongs (persist → localStorage); saveAlbum, likeSong |

Подробнее: [frontend-state-flow/README.md](./11_frontend-state-flow/README.md)

---

## 5. Поток аутентификации

1. **Загрузка приложения:** `AuthProvider` вызывает `checkAuth()` — читает `localStorage` (spotify_tokens, spotify_user), восстанавливает сессию.
2. **Вход:** `login()` → `POST /api/auth/login` → токены в localStorage и store.
3. **Запросы:** `axios` interceptor добавляет `Authorization: Bearer <access_token>`.
4. **401:** interceptor вызывает `POST /api/auth/refresh` → новые токены → повтор запроса; при неудаче — `auth:logout` → редирект на `/login`.
5. **Выход:** `logout()` → `POST /api/auth/logout` → `reset()` → очистка localStorage.

Подробнее: [frontend-auth-flow/README.md](./10_frontend-auth-flow/README.md)

---

## 6. Поток воспроизведения (Player)

1. **Инициация:** `playAlbum(songs)` или `setCurrentSong(song)` — обновляет `queue`, `currentSong`, `isPlaying`.
2. **AudioPlayer:** `<audio src={currentSong?.file_url}>` — слушает `isPlaying`, `volume`, `repeatMode`; при `onEnded` вызывает `playNext()` или перезапуск (Repeat One).
3. **PlaybackControls:** отображает прогресс, кнопки Play/Pause/Next/Prev, Shuffle, Repeat, громкость.
4. **Shuffle:** алгоритм Фишера-Йейтса — предварительное перемешивание очереди в `shuffledQueue`.
5. **Repeat:** off → all → one → off; Repeat One обрабатывается в `AudioPlayer.handleEnded`.

Подробнее: [frontend-player-flow/README.md](./12_frontend-player-flow/README.md)

---

## 7. Диаграммы и подробная документация

| Папка | Описание |
|-------|----------|
| [08_frontend-structure](./08_frontend-structure/) | Структура папок и файлов |
| [09_frontend-routes](./09_frontend-routes/) | Маршрутизация и защита |
| [11_frontend-state-flow](./11_frontend-state-flow/) | Zustand stores и потоки данных |
| [10_frontend-auth-flow](./10_frontend-auth-flow/) | Аутентификация и refresh токена |
| [12_frontend-player-flow](./12_frontend-player-flow/) | Плеер, очередь, shuffle, repeat |

---

## 8. Ключевые библиотеки

| Библиотека | Назначение |
|-----------|-----------|
| `react` 19.x | UI-компоненты, хуки |
| `react-router-dom` 7.x | SPA-маршрутизация |
| `zustand` 5.x | Глобальное состояние |
| `axios` 1.x | HTTP-клиент (baseURL: /api) |
| `tailwindcss` 3.x | Utility-first CSS |
| `@radix-ui/*` | Доступные примитивы (dialog, slider, avatar) |
| `lucide-react` | Иконки |
| `react-hot-toast` | Уведомления |
| `socket.io-client` | WebSocket (чат) |
| `class-variance-authority` + `clsx` + `tailwind-merge` | Варианты стилей |
| `vite` 7.x | Сборщик, dev-сервер, proxy |

---

## 9. Дизайн-система

| Цвет | HEX | Применение |
|------|-----|-----------|
| Spotify Green | #1DB954 | Кнопки Play, акценты |
| Black | #121212 | Основной фон |
| Charcoal | #181818 | Карточки |
| Sidebar | #000000 | Левая панель |
| Text Muted | #b3b3b3 | Второстепенный текст |

- **Шрифт:** Plus Jakarta Sans (аналог Spotify Circular)
- **Vite proxy:** `/api`, `/media`, `/ws` → `http://localhost:8000`

---

*Документ подготовлен 18.03.2026. Проект: Spotify Clone (React + Vite + Zustand)*
