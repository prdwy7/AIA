import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Admin console (S22) — dev server proxies /v1 to the central core-api.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    proxy: {
      '/v1': 'http://localhost:8000',
    },
  },
})
