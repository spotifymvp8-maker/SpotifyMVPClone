import { useState } from "react";
import { Link } from "react-router-dom";
import Topbar from "@/components/Topbar";
import { usePlayerStore } from "@/stores/usePlayerStore";
import { useLibraryStore } from "@/stores/useLibraryStore";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Heart, Play, BookOpen, Disc3 } from "lucide-react";

const LibraryPage = () => {
	const [activeTab, setActiveTab] = useState<"albums" | "songs">("albums");

	const { playAlbum, setCurrentSong } = usePlayerStore();
	const { savedAlbums, likedSongs, removeAlbum, unlikeSong } = useLibraryStore();

	const handlePlayAlbum = (e: React.MouseEvent, songs: typeof savedAlbums[0]["songs"]) => {
		e.preventDefault();
		e.stopPropagation();
		if (songs?.length) playAlbum(songs, 0);
	};

	return (
		<main className="flex flex-1 flex-col min-h-0 overflow-hidden bg-spotify-charcoal">
			<div className="relative h-[220px] min-h-[220px] bg-gradient-to-b from-indigo-900/60 via-spotify-charcoal to-spotify-charcoal sm:h-[260px] sm:min-h-[260px] md:h-[300px] md:min-h-[300px] lg:h-[340px] lg:min-h-[340px]">
				<Topbar />

				<div className="absolute bottom-0 left-0 right-0 px-4 pb-5 sm:px-5 md:px-6 md:pb-6">
					<h1 className="mb-4 text-2xl font-bold text-white sm:text-3xl md:mb-5 md:text-4xl">
						Your Library
					</h1>

					<div className="flex flex-wrap gap-2">
						<button
							onClick={() => setActiveTab("albums")}
							className={`rounded-full px-4 py-2 text-sm font-medium transition-colors sm:px-5 md:px-6 ${
								activeTab === "albums"
									? "bg-white text-black"
									: "bg-white/10 text-white hover:bg-white/20"
							}`}
						>
							Albums
						</button>

						<button
							onClick={() => setActiveTab("songs")}
							className={`rounded-full px-4 py-2 text-sm font-medium transition-colors sm:px-5 md:px-6 ${
								activeTab === "songs"
									? "bg-white text-black"
									: "bg-white/10 text-white hover:bg-white/20"
							}`}
						>
							Liked Songs
						</button>
					</div>
				</div>
			</div>

			<ScrollArea className="flex-1 scrollbar-spotify">
				<div className="relative z-10 -mt-6 px-4 pb-28 pt-0 sm:-mt-7 sm:px-5 md:-mt-8 md:px-6 md:pb-32">
					{activeTab === "albums" ? (
						<>
							{savedAlbums.length === 0 ? (
								<div className="flex flex-col items-center justify-center py-16 text-center">
									<Disc3 className="mb-4 h-14 w-14 text-white/20" />
									<p className="mb-2 text-base font-semibold text-white">
										No saved albums yet
									</p>
									<p className="text-sm text-spotify-text-muted">
										Open an album and press the heart button to save it here
									</p>
								</div>
							) : (
								<div className="grid grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-4 md:grid-cols-4 lg:grid-cols-5">
									{savedAlbums.map((album) => (
										<Link
											key={album.id}
											to={`/albums/${album.id}`}
											className="group relative block rounded-lg bg-white/5 p-3 transition-colors hover:bg-white/10 sm:p-4"
										>
											<div className="relative mb-3">
												<img
													src={album.image_url || "/album-placeholder.png"}
													alt={album.title}
													className="aspect-square w-full rounded-lg object-cover"
												/>

												<Button
													size="icon"
													onClick={(e) => handlePlayAlbum(e, album.songs)}
													className="absolute bottom-2 right-2 h-10 w-10 rounded-full bg-spotify-green opacity-0 shadow-xl transition-all hover:bg-spotify-green-hover group-hover:opacity-100 md:h-12 md:w-12"
												>
													<Play
														className="ml-0.5 h-4 w-4 text-black md:h-5 md:w-5"
														fill="currentColor"
													/>
												</Button>
											</div>

											<p className="truncate text-sm font-medium text-white sm:text-base">
												{album.title}
											</p>
											<p className="truncate text-xs text-spotify-text-muted sm:text-sm">
												{album.artist}
											</p>

											<button
												onClick={(e) => {
													e.preventDefault();
													e.stopPropagation();
													removeAlbum(album.id);
												}}
												className="mt-2 flex items-center gap-1 text-xs text-spotify-green hover:text-white transition-colors"
											>
												<Heart className="h-3 w-3" fill="currentColor" />
												<span>Saved</span>
											</button>
										</Link>
									))}
								</div>
							)}
						</>
					) : (
						<>
							{likedSongs.length === 0 ? (
								<div className="flex flex-col items-center justify-center py-16 text-center">
									<BookOpen className="mb-4 h-14 w-14 text-white/20" />
									<p className="mb-2 text-base font-semibold text-white">
										No liked songs yet
									</p>
									<p className="text-sm text-spotify-text-muted">
										Press the heart button on any track to add it here
									</p>
								</div>
							) : (
								<div className="space-y-2">
									{likedSongs.map((song, i) => (
										<div
											key={song.id}
											className="group flex cursor-pointer items-center gap-3 rounded-lg p-2.5 transition-colors hover:bg-white/10 sm:gap-4 sm:p-3"
											onClick={() => setCurrentSong(song)}
										>
											<span className="w-5 text-xs text-spotify-text-muted sm:w-6 sm:text-sm">
												{i + 1}
											</span>

											<img
												src={song.image_url || "/album-placeholder.png"}
												alt=""
												className="h-10 w-10 rounded object-cover sm:h-12 sm:w-12"
											/>

											<div className="min-w-0 flex-1">
												<p className="truncate text-sm font-medium text-white sm:text-base">
													{song.title}
												</p>
												<p className="truncate text-xs text-spotify-text-muted sm:text-sm">
													{song.artist}
													{song.album_name ? ` • ${song.album_name}` : ""}
												</p>
											</div>

											<button
												onClick={(e) => {
													e.stopPropagation();
													unlikeSong(song.id);
												}}
												className="text-spotify-green hover:text-white transition-colors"
											>
												<Heart className="h-4 w-4" fill="currentColor" />
											</button>

											<Button
												size="icon"
												className="h-9 w-9 rounded-full bg-spotify-green opacity-0 transition-opacity group-hover:opacity-100 hover:bg-spotify-green-hover sm:h-10 sm:w-10"
												onClick={(e) => {
													e.stopPropagation();
													setCurrentSong(song);
												}}
											>
												<Play
													className="ml-0.5 h-4 w-4 text-black sm:h-5 sm:w-5"
													fill="currentColor"
												/>
											</Button>
										</div>
									))}
								</div>
							)}
						</>
					)}
				</div>
			</ScrollArea>
		</main>
	);
};

export default LibraryPage;
