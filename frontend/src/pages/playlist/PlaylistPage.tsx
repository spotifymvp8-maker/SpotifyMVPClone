import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { usePlayerStore } from "@/stores/usePlayerStore";
import { useLibraryStore } from "@/stores/useLibraryStore";
import { useMusicStore } from "@/stores/useMusicStore";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Play, Pause, Heart } from "lucide-react";
import Topbar from "@/components/Topbar";
import { Playlist, Song } from "@/types";

const PlaylistPage = () => {
  const { playlistId } = useParams<{ playlistId: string }>();
  const { fetchPlaylistById } = useMusicStore();
  const { currentSong, isPlaying, togglePlay, playAlbum } = usePlayerStore();
  const { likeSong, unlikeSong, isSongLiked } = useLibraryStore();
  const [playlist, setPlaylist] = useState<Playlist | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadPlaylist = async () => {
      if (!playlistId) return;
      setIsLoading(true);
      try {
        const data = await fetchPlaylistById(playlistId);
        setPlaylist(data);
      } catch (err) {
        console.error("Failed to load playlist:", err);
        setPlaylist(null);
      } finally {
        setIsLoading(false);
      }
    };
    loadPlaylist();
  }, [playlistId, fetchPlaylistById]);

  const isPlaylistPlaying =
    isPlaying && playlist?.tracks?.some((t) => t.id === currentSong?.id);

  const handlePlayPlaylist = () => {
    if (!playlist?.tracks || playlist.tracks.length === 0) return;
    if (isPlaylistPlaying) {
      togglePlay();
      return;
    }
    const currentIndex = playlist.tracks.findIndex(
      (s) => s.id === currentSong?.id
    );
    playAlbum(playlist.tracks, currentIndex >= 0 ? currentIndex : 0);
  };

  const handlePlaySong = (song: Song, index: number) => {
    if (!playlist?.tracks) return;
    if (currentSong?.id === song.id) {
      togglePlay();
    } else {
      playAlbum(playlist.tracks, index);
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  if (isLoading || !playlist) {
    return (
      <main className="flex flex-1 flex-col min-h-0 overflow-hidden bg-spotify-charcoal">
        <Topbar />
        <div className="flex flex-1 items-center justify-center p-6 sm:p-8">
          <p className="text-sm text-spotify-text-muted">Loading...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="flex flex-1 flex-col min-h-0 overflow-hidden bg-spotify-charcoal">
      <div className="relative h-[260px] sm:h-[320px] md:h-[360px] lg:h-[420px] overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-black/30 via-black/50 to-spotify-charcoal" />
        <Topbar />
        <div className="absolute bottom-0 left-0 right-0 z-10 px-4 pb-5 sm:px-5 md:px-6 md:pb-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:gap-5 lg:gap-6">
            <div className="h-28 w-28 rounded bg-white/5 flex items-center justify-center sm:h-36 sm:w-36 md:h-44 md:w-44 lg:h-48 lg:w-48">
              <Play className="h-10 w-10 text-white/80" />
            </div>

            <div className="flex min-w-0 flex-col justify-end">
              <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-white/80 sm:text-xs">
                Playlist
              </p>

              <h1 className="mt-2 mb-3 text-2xl font-bold text-white sm:text-3xl md:text-4xl lg:mb-4">
                {playlist.title}
              </h1>

              <div className="flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-spotify-text-muted sm:text-sm">
                <span>{playlist.tracks?.length || 0} songs</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <ScrollArea className="flex-1 scrollbar-spotify">
        <div className="relative z-10 px-4 pb-28 pt-5 sm:px-5 sm:pt-6 md:px-6 md:pb-32">
          <div className="flex items-center gap-4 pb-4">
            <Button
              size="icon"
              className="h-12 w-12 rounded-full bg-spotify-green shadow-xl transition-all hover:scale-105 hover:bg-spotify-green-hover sm:h-14 sm:w-14"
              onClick={handlePlayPlaylist}
            >
              {isPlaylistPlaying ? (
                <Pause className="h-6 w-6 text-black sm:h-7 sm:w-7" fill="currentColor" />
              ) : (
                <Play className="ml-0.5 h-6 w-6 text-black sm:h-7 sm:w-7" fill="currentColor" />
              )}
            </Button>
          </div>

          <div className="space-y-1">
            {playlist.tracks?.map((song, index) => {
              const isCurrentSong = currentSong?.id === song.id;
              return (
                <div
                  key={song.id}
                  className={`group flex cursor-pointer items-center gap-3 rounded-md px-2.5 py-2 transition-colors sm:gap-4 sm:px-3 ${
                    isCurrentSong ? "bg-white/10" : "hover:bg-white/5"
                  }`}
                  onClick={() => handlePlaySong(song, index)}
                >
                  <div className="flex w-6 shrink-0 items-center justify-center text-xs text-spotify-text-muted group-hover:text-white sm:w-8 sm:text-sm">
                    {isCurrentSong && isPlaying ? (
                      <div className="flex h-4 items-center justify-center gap-0.5">
                        <div className="h-3 w-1 rounded bg-spotify-green animate-pulse" />
                        <div className="h-4 w-1 rounded bg-spotify-green animate-pulse delay-75" />
                        <div className="h-2 w-1 rounded bg-spotify-green animate-pulse delay-150" />
                      </div>
                    ) : (
                      <span className="group-hover:hidden">{index + 1}</span>
                    )}
                  </div>

                  <div className="hidden w-6 shrink-0 group-hover:flex items-center justify-center sm:w-8">
                    <Play className="h-4 w-4 text-white" fill="currentColor" />
                  </div>

                  <img
                    src={song.image_url || "/album-placeholder.png"}
                    alt={song.title}
                    className="h-10 w-10 shrink-0 rounded object-cover sm:h-11 sm:w-11"
                  />

                  <div className="min-w-0 flex-1">
                    <p
                      className={`truncate text-sm font-medium sm:text-base ${
                        isCurrentSong ? "text-spotify-green" : "text-white"
                      }`}
                    >
                      {song.title}
                    </p>
                    <p className="truncate text-xs text-spotify-text-muted sm:text-sm">
                      {song.artist}
                    </p>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      isSongLiked(song.id) ? unlikeSong(song.id) : likeSong(song);
                    }}
                    className={`shrink-0 transition-transform hover:scale-110 ${
                      isSongLiked(song.id) ? "" : "opacity-0 group-hover:opacity-100"
                    }`}
                  >
                    <Heart
                      className={`h-4 w-4 transition-colors ${
                        isSongLiked(song.id) ? "text-spotify-green" : "text-white/50 hover:text-white"
                      }`}
                      fill={isSongLiked(song.id) ? "currentColor" : "none"}
                    />
                  </button>

                  <span className="shrink-0 text-xs text-spotify-text-muted sm:text-sm">
                    {formatDuration(song.duration)}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </ScrollArea>
    </main>
  );
};

export default PlaylistPage;