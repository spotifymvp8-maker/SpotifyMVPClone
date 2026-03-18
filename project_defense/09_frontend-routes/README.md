# Frontend Routes

**Изображения:** `frontend-routes.png`

---

## Что изображено

Маршрутизация React Router в `App.tsx`. Все пути и их защита.

- **Публичные:** `/login`, `/presentation`
- **Защищённые (MainLayout):** `/`, `/search`, `/library`, `/playlists/new`, `/playlists/:id`, `/albums/:albumId`
- **Защищённые (без layout):** `/admin`
- **Fallback:** `*` → NotFoundPage

---

## Как это работает

1. **React Router** (`BrowserRouter`) сопоставляет URL с `Route` в `App.tsx`.

2. **Защита:** `element={isAuthenticated ? <HomePage /> : <Navigate to='/login' />}` — если пользователь не авторизован, редирект на `/login`.

3. **MainLayout** — `Route element={<MainLayout />}` с вложенными `Route`; контент рендерится через `<Outlet />` в MainLayout.

4. **Динамические параметры:** `/albums/:albumId`, `/playlists/:id` — доступ через `useParams()`.

5. **Логика редиректа на login:**
   - При `/login` и авторизованном пользователе → редирект на `/`
   - При любом защищённом маршруте и неавторизованном → редирект на `/login`

6. **Страницы вне MainLayout:** `/admin`, `/login`, `/presentation` — отображаются без LeftSidebar и плеера.
