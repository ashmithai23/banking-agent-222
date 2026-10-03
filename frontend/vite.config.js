import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const backend = process.env.VITE_BACKEND_URL || 'http://localhost:8000'

export default defineConfig({
  // Pin the root to this folder so the app is found no matter where Vite is launched from
  root: fileURLToPath(new URL('.', import.meta.url)),
  plugins: [react()],
  server: {
    host: true,
    port: Number(process.env.FRONTEND_PORT) || 5173,
    // Fail loudly instead of silently moving to another port if 5173 is taken
    strictPort: true,
    proxy: { '/api': { target: backend, changeOrigin: true } },
  },
})
