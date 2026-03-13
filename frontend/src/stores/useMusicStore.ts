import { create } from "zustand";
import { Song, Album } from "@/types";
import { axiosInstance } from "@/lib/axios";

function extractError(err: unknown): string {
	if (!err || typeof err !== "object") return "Неизвестная ошибка";
	const r = err as { response?: { status?: number; data?: { detail?: unknown } } };
	const detail = r.response?.data?.detail;
	if (typeof detail === "string") return detail;
	if (Array.isArray(detail) && detail[0] && typeof detail[0] === "object" && "msg" in detail[0]) {
		return String((detail[0] as { msg?: string }).msg) || "Ошибка валидации";
	}
	if (r.response?.status === 403) return "Требуются права администратора. Войдите как test@example.com / test123";
	if (r.response?.status === 401) return "Сессия истекла. Войдите снова.";
	return "Ошибка запроса";
}

interface CreateAlbumData {
	title: string;
	artist: string;
	image_url: string;
	release_year: number;
}

interface CreateSongData {
	title: string;
	artist: string;
	album_id?: string;
	image_url?: string;
	file_url: string;
	duration: number;
}

interface UpdateAlbumData {
	title?: string;
	artist?: string;
	image_url?: string;
	release_year?: number;
}

interface UpdateSongData {
	title?: string;
	artist?: string;
	album_id?: string | null;
	image_url?: string | null;
	file_url?: string;
	duration?: number;
}

interface MusicStore {
	featuredSongs: Song[];
	madeForYouSongs: Song[];
	trendingSongs: Song[];
	albums: Album[];
	isLoading: boolean;
	error: string | null;
	clearError: () => void;
	setError: (msg: string) => void;

	fetchFeaturedSongs: () => Promise<void>;
	fetchMadeForYouSongs: () => Promise<void>;
	fetchTrendingSongs: () => Promise<void>;
	fetchAlbums: () => Promise<void>;
	fetchAlbumById: (id: string) => Promise<Album | null>;
	search: (query: string) => Promise<{ tracks: Song[]; albums: Album[]; artists: { name: string }[] }>;

	createAlbum: (data: CreateAlbumData) => Promise<Album | null>;
	createSong: (data: CreateSongData) => Promise<Song | null>;
	updateAlbum: (id: string, data: UpdateAlbumData) => Promise<Album | null>;
	deleteAlbum: (id: string) => Promise<boolean>;
	updateSong: (id: string, data: UpdateSongData) => Promise<Song | null>;
	deleteSong: (id: string) => Promise<boolean>;
	uploadImage: (file: File) => Promise<string | null>;
	uploadAudio: (file: File) => Promise<string | null>;
}

export const useMusicStore = create<MusicStore>((set, get) => ({
	featuredSongs: [],
	madeForYouSongs: [],
	trendingSongs: [],
	albums: [],
	isLoading: false,
	error: null,
	clearError: () => set({ error: null }),
	setError: (msg: string) => set({ error: msg }),

	fetchFeaturedSongs: async () => {
		set({ isLoading: true, error: null });
		try {
			const response = await axiosInstance.get("/songs/featured");
			set({ featuredSongs: response.data, isLoading: false });
		} catch (error: any) {
			set({ error: extractError(error), isLoading: false });
		}
	},

	fetchMadeForYouSongs: async () => {
		set({ isLoading: true, error: null });
		try {
			const response = await axiosInstance.get("/songs/made-for-you");
			set({ madeForYouSongs: response.data, isLoading: false });
		} catch (error: any) {
			set({ error: extractError(error), isLoading: false });
		}
	},

	fetchTrendingSongs: async () => {
		set({ isLoading: true, error: null });
		try {
			const response = await axiosInstance.get("/songs/trending");
			set({ trendingSongs: response.data, isLoading: false });
		} catch (error: any) {
			set({ error: extractError(error), isLoading: false });
		}
	},

	fetchAlbums: async () => {
		set({ isLoading: true, error: null });
		try {
			const response = await axiosInstance.get("/albums");
			set({ albums: response.data, isLoading: false });
		} catch (error: any) {
			set({ error: extractError(error), isLoading: false });
		}
	},

	fetchAlbumById: async (id: string) => {
		set({ isLoading: true, error: null });
		try {
			const response = await axiosInstance.get(`/albums/${id}`);
			set({ isLoading: false });
			return response.data;
		} catch (error: any) {
			set({ error: extractError(error), isLoading: false });
			return null;
		}
	},

	search: async (query: string) => {
		set({ isLoading: true, error: null });
		try {
			const response = await axiosInstance.get("/search", {
				params: { q: query },
			});
			set({ isLoading: false });
			return response.data;
		} catch (error: any) {
			set({ error: extractError(error), isLoading: false });
			return { tracks: [], albums: [], artists: [] };
		}
	},

	createAlbum: async (data: CreateAlbumData) => {
		set({ error: null });
		try {
			const response = await axiosInstance.post("/albums", data);
			const album = response.data;
			set((state) => ({ albums: [album, ...state.albums] }));
			return album;
		} catch (error: any) {
			set({ error: extractError(error) });
			return null;
		}
	},

	createSong: async (data: CreateSongData) => {
		set({ error: null });
		try {
			const payload = {
				...data,
				album_id: data.album_id || null,
				image_url: data.image_url || null,
			};
			const response = await axiosInstance.post("/songs/", payload);
			return response.data;
		} catch (err: unknown) {
			set({ error: extractError(err) });
			return null;
		}
	},

	updateAlbum: async (id: string, data: UpdateAlbumData) => {
		set({ error: null });
		try {
			const response = await axiosInstance.put(`/albums/${id}`, data);
			const album = response.data;
			set((state) => ({
				albums: state.albums.map((a) => (a.id === id ? album : a)),
			}));
			return album;
		} catch (error: any) {
			set({ error: extractError(error) });
			return null;
		}
	},

	deleteAlbum: async (id: string) => {
		set({ error: null });
		try {
			await axiosInstance.delete(`/albums/${id}`);
			set((state) => ({ albums: state.albums.filter((a) => a.id !== id) }));
			return true;
		} catch (error: any) {
			set({ error: extractError(error) });
			return false;
		}
	},

	updateSong: async (id: string, data: UpdateSongData) => {
		set({ error: null });
		try {
			const response = await axiosInstance.put(`/songs/${id}`, data);
			const song = response.data;
			set((state) => ({
				albums: state.albums.map((a) => ({
					...a,
					songs: a.songs?.map((s) => (s.id === id ? song : s)) ?? [],
				})),
			}));
			return response.data;
		} catch (error: any) {
			set({ error: extractError(error) });
			return null;
		}
	},

	deleteSong: async (id: string) => {
		set({ error: null });
		try {
			await axiosInstance.delete(`/songs/${id}`);
			set((state) => ({
				albums: state.albums.map((a) => ({
					...a,
					songs: a.songs?.filter((s) => s.id !== id) ?? [],
				})),
			}));
			return true;
		} catch (error: any) {
			set({ error: extractError(error) });
			return false;
		}
	},

	uploadImage: async (file: File) => {
		const formData = new FormData();
		formData.append("file", file, file.name);
		try {
			const response = await axiosInstance.post("/upload/image", formData);
			const url = response.data?.url;
			return typeof url === "string" ? url : null;
		} catch (err: unknown) {
			set({ error: extractError(err) });
			return null;
		}
	},

	uploadAudio: async (file: File) => {
		const formData = new FormData();
		formData.append("file", file, file.name);
		try {
			const response = await axiosInstance.post("/upload/audio", formData);
			const url = response.data?.url;
			return typeof url === "string" ? url : null;
		} catch (err: unknown) {
			set({ error: extractError(err) });
			return null;
		}
	},
}));
