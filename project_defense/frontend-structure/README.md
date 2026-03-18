# Frontend Structure

**Изображения:** `frontend-structure.png`

---

## Что изображено

Структура папки `frontend/src/` — React-приложения на Vite.

- **main.tsx** — точка входа, AuthProvider, BrowserRouter
- **App.tsx** — роутинг, Routes, Toaster
- **pages/** — страницы по маршрутам (Home, Search, Library, Album, Admin, Login и т.д.)
- **layout/** — MainLayout, LeftSidebar, PlaybackControls, AudioPlayer, ArtistInfoSidebar
- **stores/** — Zustand: useAuthStore, usePlayerStore, useMusicStore, useArtistStore, useLibraryStore
- **components/** — Topbar, ui (Radix + Tailwind), skeletons
- **lib/** — axios (с JWT interceptor), utils (cn)
- **providers/** — AuthProvider (checkAuth, auth:logout, auth:token-refreshed)
- **types/** — Song, Album, Playlist, User, SearchResult

---

## Как это работает

1. **main.tsx** рендерит приложение в `#root`, оборачивает в `AuthProvider` и `BrowserRouter`.

2. **AuthProvider** при монтировании вызывает `checkAuth()` — восстанавливает сессию из localStorage.

3. **App.tsx** определяет маршруты: защищённые страницы требуют `isAuthenticated`, иначе редирект на `/login`.

4. **MainLayout** — общая обёртка: левая панель, контент (`<Outlet />`), правая панель исполнителя, плеер внизу.

5. **stores/** — Zustand store'ы без провайдеров; компоненты подписываются через `useAuthStore()`, `usePlayerStore()` и т.д.

6. **lib/axios.ts** — единый экземпляр axios с `baseURL: "/api"`, добавлением Bearer token и обработкой 401 (refresh).

7. **types/index.ts** — общие TypeScript-интерфейсы для Song, Album, User и др., синхронизированные с Pydantic-схемами backend.
