# Frontend Auth Flow

**Изображения:** `frontend-auth-flow.png`

---

## Что изображено

Два потока: **вход в систему** (login) и **обработка 401** (refresh token).

**Login:** форма → POST /api/auth/login → токены в store и localStorage → редирект на `/`  
**401:** запрос → 401 → axios interceptor → POST /api/auth/refresh → новые токены → повтор запроса

---

## Как это работает

### Поток входа (Login)

1. Пользователь вводит email и password в `LoginPage`.
2. `login({ email, password })` вызывает `POST /api/auth/login`.
3. Backend возвращает `{ access_token, refresh_token, user }`.
4. `useAuthStore` сохраняет токены в `tokens` и `user` в state.
5. `localStorage.setItem(TOKEN_KEY, ...)` и `localStorage.setItem(USER_KEY, ...)` — персистентность.
6. `isAuthenticated = true` → React Router редиректит на `/`.

### Поток регистрации (Register)

Аналогично login: `POST /api/auth/register` → токены → store + localStorage → редирект.

### Поток 401 (Refresh Token)

1. Любой запрос с истёкшим access_token получает **401 Unauthorized**.
2. **axios interceptor** перехватывает ошибку.
3. Если уже идёт refresh — запрос ставится в очередь `failedQueue`.
4. Вызов `POST /api/auth/refresh` с `refresh_token` из localStorage.
5. Успех: новые токены → `localStorage` → `window.dispatchEvent(auth:token-refreshed)` → `AuthProvider` обновляет store → повтор исходного запроса.
6. Неудача: `localStorage` очищается → `auth:logout` → `AuthProvider` вызывает `reset()` и редирект на `/login`.

### AuthProvider

- При монтировании: `checkAuth()` — читает localStorage, восстанавливает сессию.
- Слушает `auth:logout` → `reset()` + `window.location.href = "/login"`.
- Слушает `auth:token-refreshed` → `setTokensFromRefresh(detail)`.
