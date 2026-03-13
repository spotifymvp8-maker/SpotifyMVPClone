import { useEffect, useState, useCallback } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import Topbar from "@/components/Topbar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useMusicStore } from "@/stores/useMusicStore";
import { Song } from "@/types";
import { Search, Plus, Check, X } from "lucide-react";

const PlaylistEditPage = () => {
  const { id: playlistId } = useParams();
  const { search } = useMusicStore();

  const [playlist, setPlaylist] = useState<any>(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Song[]>([]);
  const [addedTracks, setAddedTracks] = useState<Set<string>>(new Set());

  const tokenData = localStorage.getItem("spotify_tokens");
  const accessToken = tokenData ? JSON.parse(tokenData).access_token : null;

  const authHeader = {
    headers: { Authorization: `Bearer ${accessToken}` },
  };

  const apiUrl = import.meta.env.VITE_API_URL;

  const loadPlaylist = useCallback(async () => {
    const res = await axios.get(
      `${apiUrl}/playlists/${playlistId}`,
      authHeader
    );
    setPlaylist(res.data);

    const ids = new Set<string>(res.data.tracks.map((t: Song) => t.id));
    setAddedTracks(ids);
  }, [playlistId]);

  useEffect(() => {
    loadPlaylist();
  }, [loadPlaylist]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    const data = await search(query.trim());
    setResults(data.tracks);
  };

  const addTrack = async (trackId: string) => {
    await axios.post(
      `${apiUrl}/playlists/${playlistId}/tracks`,
      {
        track_id: trackId,
        position: null,
      },
      authHeader
    );

    setAddedTracks(prev => new Set(prev).add(trackId));
    loadPlaylist();
  };

  const removeTrack = async (trackId: string) => {
    await axios.delete(
      `${apiUrl}/playlists/${playlistId}/tracks/${trackId}`,
      authHeader
    );

    setPlaylist((prev: any) =>
      prev
        ? { ...prev, tracks: prev.tracks.filter((t: Song) => t.id !== trackId) }
        : prev
    );

    setAddedTracks(prev => {
      const copy = new Set(prev);
      copy.delete(trackId);
      return copy;
    });
  };

  return (
    <main className="flex-1 flex flex-col h-screen bg-spotify-charcoal overflow-hidden">
      <Topbar />

      <ScrollArea className="flex-1">
        <div className="p-6 space-y-8 pb-28">
          {playlist && (
            <div>
              <h1 className="text-4xl font-bold text-white">{playlist.title}</h1>
              <p className="text-spotify-text-muted">
                {playlist.tracks.length} tracks
              </p>
            </div>
          )}

          <form onSubmit={handleSearch} className="relative max-w-xl">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-spotify-text-muted" />
            <Input
              placeholder="Search tracks to add..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="pl-12 h-12 rounded-full bg-white/10 border-0 text-white"
            />
          </form>

          {results.length > 0 && (
            <section>
              <h2 className="text-2xl font-bold text-white mb-4">
                Search Results
              </h2>
              <div className="space-y-2">
                {results.map((song) => {
                  const isAdded = addedTracks.has(song.id);
                  return (
                    <div
                      key={song.id}
                      className="flex items-center gap-4 p-3 rounded-lg bg-white/5"
                    >
                      <img
                        src={song.image_url || "/album-placeholder.png"}
                        className="h-12 w-12 rounded"
                      />
                      <div className="flex-1">
                        <p className="text-white">{song.title}</p>
                        <p className="text-sm text-spotify-text-muted">
                          {song.artist}
                        </p>
                      </div>

                      <Button
                        size="icon"
                        disabled={isAdded}
                        onClick={() => addTrack(song.id)}
                        className={`rounded-full ${
                          isAdded
                            ? "bg-green-600 cursor-not-allowed"
                            : "bg-spotify-green hover:bg-spotify-green-hover"
                        }`}
                      >
                        {isAdded ? (
                          <Check className="h-5 w-5 text-black" />
                        ) : (
                          <Plus className="h-5 w-5 text-black" />
                        )}
                      </Button>
                    </div>
                  );
                })}
              </div>
            </section>
          )}

          {playlist && playlist.tracks.length > 0 && (
            <section>
              <h2 className="text-2xl font-bold text-white mb-4">
                Playlist Tracks
              </h2>
              <div className="space-y-2">
                {playlist.tracks.map((song: Song, i: number) => (
                  <div
                    key={song.id}
                    className="group flex items-center gap-4 p-3 rounded-lg bg-white/5"
                  >
                    <span className="w-6 text-spotify-text-muted">
                      {i + 1}
                    </span>
                    <img
                      src={song.image_url || "/album-placeholder.png"}
                      className="h-12 w-12 rounded"
                    />
                    <div className="flex-1">
                      <p className="text-white">{song.title}</p>
                      <p className="text-sm text-spotify-text-muted">
                        {song.artist}
                      </p>
                    </div>

                    <Button
                      size="icon"
                      variant="ghost"
                      onClick={() => removeTrack(song.id)}
                      className="opacity-0 group-hover:opacity-100 transition"
                    >
                      <X className="h-5 w-5" />
                    </Button>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
      </ScrollArea>
    </main>
  );
};

export default PlaylistEditPage;