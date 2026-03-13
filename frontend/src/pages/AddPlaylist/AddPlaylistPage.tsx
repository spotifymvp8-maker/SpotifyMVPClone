import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios"; // стандартный axios
import Topbar from "@/components/Topbar";
import { Button } from "@/components/ui/button";

const NewPlaylistPage = () => {
  const navigate = useNavigate();
  const [title, setTitle] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  
  // Проверяем, что переменная окружения подхватилась
  useEffect(() => {
    console.log("API URL:", import.meta.env.VITE_API_URL);
  }, []);

  const handleCreatePlaylist = async () => {
    if (!title.trim()) {
      setError("Please enter a playlist name");
      return;
    }

    setIsLoading(true);
    setError(null);

    const tokenData = localStorage.getItem("spotify_tokens");
    const accessToken = tokenData ? JSON.parse(tokenData).access_token : null;

    if (!accessToken) {
      setError("No Spotify access token found");
      setIsLoading(false);
      return;
    }

    try {
      const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

      const response = await axios.post(
        `${apiUrl}/playlists`,
        { title: title.trim() },
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      const playlistId = response.data.id;

      // фикс для возврата на прошлую страницу после создания плейлиста
      navigate(`/playlists/${playlistId}`, { replace: true });

    } catch (err: any) {
      console.error("Failed to create playlist:", err.response || err);
      setError("Failed to create playlist");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex-1 flex flex-col min-h-screen bg-spotify-charcoal">
      <Topbar />
      <div className="flex-1 flex flex-col items-center justify-center px-6">
        <h1 className="text-3xl font-bold text-white mb-4">Create New Playlist</h1>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Playlist name"
          className="w-full max-w-md p-3 rounded bg-white/10 text-white placeholder-white/60 mb-4 focus:outline-none focus:ring-2 focus:ring-spotify-green"
        />
        {error && <p className="text-red-500 mb-2">{error}</p>}
        <Button
          onClick={handleCreatePlaylist}
          disabled={isLoading}
          className="bg-spotify-green hover:bg-spotify-green-hover px-6 py-3 text-black font-bold"
        >
          {isLoading ? "Creating..." : "Create Playlist"}
        </Button>
      </div>
    </main>
  );
};

export default NewPlaylistPage;