import axios from "axios";

export const axiosInstance = axios.create({
	baseURL: "/api",
	withCredentials: true,
});

// Добавляем Bearer token к запросам
axiosInstance.interceptors.request.use((config) => {
	const stored = localStorage.getItem("spotify_tokens");
	if (stored) {
		try {
			const { access_token } = JSON.parse(stored);
			if (access_token) {
				config.headers.Authorization = `Bearer ${access_token}`;
			}
		} catch {
			// ignore
		}
	}
	return config;
});
