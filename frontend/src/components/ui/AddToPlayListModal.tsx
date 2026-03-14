import { useEffect, useState, useMemo } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useMusicStore } from "@/stores/useMusicStore";
import { Playlist } from "@/types";
import { Search, Check, Plus } from "lucide-react";

interface AddToPlaylistModalProps {
  trackId: string;
  isOpen: boolean;
  onClose: () => void;
}

const AddToPlaylistModal = ({ trackId, isOpen, onClose }: AddToPlaylistModalProps) => {
  const { getPlaylistsForModal, addTrackToPlaylist } = useMusicStore();

  const [playlists, setPlaylists] = useState<Playlist[]>([]);
  const [query, setQuery] = useState("");
  const [added, setAdded] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(false);

  // Загружаем все плейлисты при открытии модалки
  const loadPlaylists = async () => {
    setIsLoading(true);
    try {
      const data = await getPlaylistsForModal();
      setPlaylists(data);

      // отмечаем плейлисты, где уже есть трек
      const existing: Set<string> = new Set(
        data.filter(p => p.tracks.some(t => t.id === trackId)).map(p => p.id)
      );
      setAdded(existing);
    } catch (err) {
      console.error("Failed to load playlists:", err);
      setPlaylists([]);
      setAdded(new Set());
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      setQuery("");
      loadPlaylists();
    } else {
      setPlaylists([]);
      setAdded(new Set());
    }
  }, [isOpen, trackId]);

  // Добавляем трек в плейлист
  const handleAdd = async (playlistId: string) => {
    try {
      await addTrackToPlaylist(playlistId, trackId);
      setAdded(prev => new Set(prev).add(playlistId));
    } catch (err) {
      console.error("Failed to add track:", err);
    }
  };

  // Фильтруем плейлисты на клиенте
  const filteredPlaylists = useMemo(() => {
    if (!query.trim()) return playlists;
    return playlists.filter(p =>
      p.title.toLowerCase().includes(query.toLowerCase())
    );
  }, [playlists, query]);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Add to Playlist</DialogTitle>
        </DialogHeader>

        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search playlists..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        <div className="space-y-2 max-h-80 overflow-y-auto">
          {isLoading ? (
            <p className="text-sm text-spotify-text-muted text-center">Loading...</p>
          ) : filteredPlaylists.length === 0 ? (
            <p className="text-sm text-spotify-text-muted text-center">No playlists found</p>
          ) : (
            filteredPlaylists.map(p => {
              const isAdded = added.has(p.id);
              return (
                <div
                  key={p.id}
                  className="flex items-center justify-between p-2 rounded hover:bg-white/5"
                >
                  <span>{p.title}</span>
                  <Button
                    size="icon"
                    disabled={isAdded}
                    onClick={() => handleAdd(p.id)}
                    className="rounded-full bg-spotify-green hover:bg-spotify-green-hover"
                  >
                    {isAdded ? (
                      <Check className="h-4 w-4 text-black" />
                    ) : (
                      <Plus className="h-4 w-4 text-black" />
                    )}
                  </Button>
                </div>
              );
            })
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default AddToPlaylistModal;