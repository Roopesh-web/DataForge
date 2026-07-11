import { defineConfig, loadEnv } from 'vite'
import react, { reactCompilerPreset } from '@vitejs/plugin-react'
import babel from '@rolldown/plugin-babel'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const envDir = import.meta.dirname
  const env = loadEnv(mode, envDir, '')
  const base = env.VITE_BASE || '/'
  // Dev-server proxy only — never baked into the production bundle.
  const proxyTarget = env.VITE_DEV_PROXY_TARGET || 'http://localhost:8000'

  const proxyPaths = [
    '/health',
    '/openapi.json',
    '/upload',
    '/profile',
    '/analytics',
    '/quality-check',
    '/warehouse',
  ]

  const proxy = Object.fromEntries(
    proxyPaths.map((path) => [
      path,
      {
        target: proxyTarget,
        changeOrigin: true,
      },
    ]),
  )

  return {
    base,
    plugins: [
      react(),
      babel({ presets: [reactCompilerPreset()] }),
    ],
    build: {
      // Analytics/Recharts chunks can exceed the default advisory threshold.
      chunkSizeWarningLimit: 900,
      sourcemap: false,
    },
    server: {
      proxy,
    },
  }
})
