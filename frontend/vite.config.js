import { defineConfig } from 'vite'
import react, { reactCompilerPreset } from '@vitejs/plugin-react'
import babel from '@rolldown/plugin-babel'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    babel({ presets: [reactCompilerPreset()] })
  ],
  server: {
    proxy: {
      // Same-origin proxy avoids browser CORS blocks while developing on :5173.
      // Backend still receives the request; the browser never cross-origin fetches.
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/upload': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/profile': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/analytics': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/quality-check': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/warehouse': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
