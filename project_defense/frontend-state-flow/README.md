# Frontend State Flow

**Изображения:** `frontend-state-flow.png`

---

## Что изображено

Zustand store'ы и их взаимодействие с компонентами и API.

- **useAuthStore** — user, tokens, isAuthenticated; login, logout, refreshToken, checkAuth
- **usePlayerStore** — currentSong, queue, isPlaying; playAlbum, setCurrentSong, togglePlay, playNext, playPrevious; shuffle, repeat
- **useMusicStore** — albums, featured, trending; fetchAlbums, search, CRUD, upload, playlists
- **useArtistStore** — selectedArtist, isSidebarOpen; openArtist, closeArtist
- **useLibraryStore** — savedAlbums, likedSongs (persist); saveAlbum, likeSong

---

## Как это работает

1. **Zustand** — лёгкий state manager без провайдеров. Компонент вызывает `useAuthStore()` и получает актуальное состояние и методы.

2. **useAuthStore** — хранит user и tokens; при `login`/`register` сохраняет в localStorage; `checkAuth` восстанавливает при загрузке; `reset` вызывается при logout.

3. **usePlayerStore** — единственный источник правды для плеера. `playAlbum` устанавливает queue и currentSong; `AudioPlayer` и `PlaybackControls` читают и обновляют состояние.

4. **useMusicStore** — загружает данные с API (albums, songs, search); используется на HomePage, SearchPage, AlbumPage, AdminPage; методы `createAlbum`, `uploadImage` и т.д. для админки.

5. **useLibraryStore** — `persist` в localStorage; `savedAlbums` и `likedSongs` сохраняются между сессиями; кнопки ♥ на карточках вызывают `likeSong`/`unlikeSong`.

6. **useArtistStore** — UI-состояние панели «Об исполнителе»; `openArtist({ name, imageUrl })` открывает sidebar с информацией.

7. **Поток данных:** Страница → store (вызов метода) → API (axios) → store (set) → компоненты ре-рендерятся.
