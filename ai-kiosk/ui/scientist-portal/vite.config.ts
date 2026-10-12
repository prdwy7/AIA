import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Scientist portal (S21) — dev server proxies /v1 to the central core-api.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/v1': 'http://localhost:8000',
    },
  },
})
