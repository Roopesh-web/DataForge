# DataForge Frontend

React + Vite SPA for the DataForge enterprise data platform.

**Stack:** React 19 · Vite 8 · React Router · Axios · Recharts · React Icons

## Prerequisites

- Node.js 20+
- DataForge FastAPI backend running (default `http://localhost:8000`)

## Setup

```bash
cd frontend
npm install
```

Optional environment (see `.env.example`):

```bash
# Leave unset in local Vite dev to use the same-origin proxy (avoids CORS).
# VITE_API_URL=http://localhost:8000
```

## Development

```bash
npm run dev
```

App: `http://localhost:5173`

Vite proxies these backend paths to `http://localhost:8000`:

- `/health`
- `/openapi.json`
- `/upload`
- `/profile`
- `/analytics`
- `/quality-check`
- `/warehouse`

## Production build

```bash
npm run build
npm run preview
```

Output is written to `frontend/dist`.

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start Vite dev server |
| `npm run build` | Production build |
| `npm run preview` | Preview production build |
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

## Notes

- Pages are lazy-loaded for smaller initial bundles.
- API health is polled once via a shared `HealthProvider` (navbar + settings).
- Dataset state lives in `DatasetContext` (upload, profile, analytics, quality, warehouse).
- Do not point the browser at the FastAPI origin from Vite without CORS; prefer the proxy in development.
