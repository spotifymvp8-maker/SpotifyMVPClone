# Frontend Player Flow

**Изображения:** `frontend-player-flow.png`

---

## Что изображено

Поток воспроизведения музыки: от клика «Play» до следующего трека.

- **usePlayerStore** — queue, currentSong, isPlaying, shuffle, repeat
- **AudioPlayer** — скрытый `<audio>`, синхронизация с store
- **PlaybackControls** — UI: прогресс, кнопки, громкость

---

## Как это работает

### Инициация воспроизведения

1. Пользователь кликает «Play» на карточке трека или альбома.
2. Вызывается `playAlbum(songs, startIndex)` или `setCurrentSong(song)`.
3. `usePlayerStore` обновляет: `queue`, `currentSong`, `currentIndex`, `isPlaying = true`.
4. Если Shuffle включён — генерируется `shuffledQueue` (алгоритм Фишера-Йейтса).

### AudioPlayer

1. `<audio src={currentSong?.file_url}>` — источник из store.
2. `useEffect` на `isPlaying`: `play()` или `pause()`.
3. `useEffect` на `volume`, `isMuted`: `audio.volume = isMuted ? 0 : volume`.
4. **onEnded:** если `repeatMode === "one"` — `currentTime = 0` + `play()`; иначе — `playNext()`.

### PlaybackControls

1. Отображает обложку, название, исполнителя.
2. Кнопки Play/Pause → `togglePlay()`, Next/Prev → `playNext()` / `playPrevious()`.
3. Slider прогресса → `setProgress()`, синхронизация с `timeupdate` на `<audio>`.
4. Shuffle, Repeat → `toggleShuffle()`, `toggleRepeat()`.

### Shuffle (перемешивание)

- При включении: текущий трек — первый, остальные перемешиваются через Fisher-Yates.
- Результат в `shuffledQueue`; воспроизведение идёт по `shuffledIndex`.
- При `playNext()` в shuffle: переход к `shuffledIndex + 1`; при конце и Repeat All — новая пересортировка.

### Repeat (повтор)

| Режим | Поведение |
|-------|-----------|
| Off | Конец очереди → остановка |
| All | Конец → первый трек (в shuffle — пересортировка) |
| One | Конец трека → перезапуск того же |

### Запись прослушивания

При смене трека вызывается `recordPlay(trackId)` → `POST /api/player/play` (если пользователь авторизован).
