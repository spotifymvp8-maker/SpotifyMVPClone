import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';
// https://vite.dev/config/
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "./src"),
        },
    },
    server: {
        port: 3000,
        proxy: {
            '/api': {
                target:  import.meta.env.VITE_BACKEND_URL,
                changeOrigin: true,
            },
            '/ws': {
                target: import.meta.env.VITE_BACKEND_WS_URL,
                ws: true,
            },
            '/media': {
                target:  import.meta.env.VITE_BACKEND_URL,
                changeOrigin: true,
            }
        }
    }
});
