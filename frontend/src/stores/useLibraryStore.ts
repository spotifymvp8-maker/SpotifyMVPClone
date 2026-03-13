import { create } from "zustand";
import { persist } from "zustand/middleware";
import { Album, Song } from "@/types";

interface LibraryStore {
	savedAlbums: Album[];
	likedSongs: Song[];

	saveAlbum: (album: Album) => void;
	removeAlbum: (id: string) => void;
	isAlbumSaved: (id: string) => boolean;

	likeSong: (song: Song) => void;
	unlikeSong: (id: string) => void;
	isSongLiked: (id: string) => boolean;
}

export const useLibraryStore = create<LibraryStore>()(
	persist(
		(set, get) => ({
			savedAlbums: [],
			likedSongs: [],

			saveAlbum: (album) =>
				set((s) => ({
					savedAlbums: s.savedAlbums.some((a) => a.id === album.id)
						? s.savedAlbums
						: [album, ...s.savedAlbums],
				})),

			removeAlbum: (id) =>
				set((s) => ({ savedAlbums: s.savedAlbums.filter((a) => a.id !== id) })),

			isAlbumSaved: (id) => get().savedAlbums.some((a) => a.id === id),

			likeSong: (song) =>
				set((s) => ({
					likedSongs: s.likedSongs.some((t) => t.id === song.id)
						? s.likedSongs
						: [song, ...s.likedSongs],
				})),

			unlikeSong: (id) =>
				set((s) => ({ likedSongs: s.likedSongs.filter((t) => t.id !== id) })),

			isSongLiked: (id) => get().likedSongs.some((t) => t.id === id),
		}),
		{ name: "spotify-library" }
	)
);
