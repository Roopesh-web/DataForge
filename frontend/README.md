# DataForge Frontend

React + Vite SPA for the DataForge enterprise data platform.

**Stack:** React 19 · Vite 8 · React Router · Axios · Recharts · React Icons

## Prerequisites

- Node.js 20+
- DataForge FastAPI backend reachable from the browser (or via reverse proxy)

## Setup

```bash
cd frontend
cp .env.example .env
npm install
```

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | Production (separate API host) | Absolute API base URL, e.g. `https://api.example.com`. Leave empty for same-origin / Vite proxy. |
| `VITE_BASE` | Optional | Asset/router base path for subdirectory deploys, e.g. `/dataforge/`. Default `/`. |
| `VITE_DEV_PROXY_TARGET` | Dev only | Backend URL for the Vite proxy. Default `http://localhost:8000`. |

See `.env.example` for full comments.

**Important:** `VITE_*` values are embedded at **build time**. Rebuild after changing them.

## Development

```bash
npm run dev
```

App: `http://localhost:5173`

With `VITE_API_URL` empty, Vite proxies these paths to `VITE_DEV_PROXY_TARGET`:

- `/health`, `/openapi.json`, `/upload`, `/profile`, `/analytics`, `/quality-check`, `/warehouse`

Ensure the backend CORS allow-list includes your frontend origin if you set `VITE_API_URL` directly in development.

## Production build

```bash
# Separate API host (typical)
VITE_API_URL=https://api.example.com npm run build

# Same-origin API via reverse proxy
# (leave VITE_API_URL unset / empty)
npm run build

# Subdirectory deploy
VITE_BASE=/dataforge/ VITE_API_URL=https://api.example.com npm run build

npm run preview
```

Output: `frontend/dist/`

## Deployment

1. Build with the correct `VITE_API_URL` (and optional `VITE_BASE`).
2. Upload/serve the contents of `dist/`.
3. Configure the static host for **SPA fallback** so deep links (`/overview`, `/analytics`, …) return `index.html`:
   - **Nginx:** see `nginx.conf.example` (`try_files … /index.html`)
   - **Netlify / Cloudflare Pages:** `public/_redirects` is copied into `dist/`
   - **Apache:** `public/.htaccess` is copied into `dist/`
4. Confirm the backend allows the frontend origin in CORS when `VITE_API_URL` points at a different host.
5. Confirm upload size limits on the reverse proxy (example nginx allows 100MB).

### Checklist

- [ ] `VITE_API_URL` set for the target backend (or empty for same-origin proxy)
- [ ] `npm run build` succeeds
- [ ] `dist/` contains `index.html`, hashed assets, favicon, `_redirects` / `.htaccess`
- [ ] Hard-refresh `/` loads the app
- [ ] Direct navigation to `/upload` and `/settings` works (SPA fallback)
- [ ] Navbar shows **API Online** against the deployed backend
- [ ] Upload → Overview → Analytics flow works end-to-end

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start Vite dev server |
| `npm run build` | Production build |
| `npm run preview` | Preview production build locally |
| `npm run lint` | ESLint |

## Routes

| Path | Page |
|------|------|
| `/` | Dashboard |
| `/upload` | Upload |
| `/overview` | Dataset Overview |
| `/analytics` | Analytics |
| `/quality` | Data Quality |
| `/warehouse` | Warehouse |
| `/history` | History |
| `/settings` | Settings (read-only) |

## Architecture notes

- Pages are lazy-loaded for smaller initial bundles.
- API health is polled once via a shared `HealthProvider`.
- Dataset state lives in `DatasetContext`.
- No API base URL is hardcoded for production; configure `VITE_API_URL` at build time.
