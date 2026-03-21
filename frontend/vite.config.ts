import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'

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
        target: 'https://spotifymvpclone.up.railway.app',
        changeOrigin: true,
      },
      '/ws': {
        target: 'wss://spotifymvpclone.up.railway.app',
        ws: true,
      },
      '/media': {
        target: 'https://spotifymvpclone.up.railway.app',
        changeOrigin: true,
      }
    }
  }
})
