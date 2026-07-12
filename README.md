# DataForge

Enterprise data engineering platform for ingestion, profiling, analytics, data quality validation, and PostgreSQL warehousing.

**Stack:** FastAPI · Streamlit · PostgreSQL · Polars · SQLAlchemy

## 🚀 Live Demo

| Service | URL |
|---------|-----|
| 🌐 Frontend | https://data-forge-puce-one.vercel.app |
| ⚙️ Backend API | https://dataforge-production-ef36.up.railway.app |
| 📖 Swagger Docs | https://dataforge-production-ef36.up.railway.app/docs |
| ❤️ Health Check | https://dataforge-production-ef36.up.railway.app/health |

## Deployment

Frontend: Vercel

Backend: Railway

Database: PostgreSQL (Railway)

Production deployment is publicly accessible.

### Prerequisites

- Docker 24+
- Docker Compose v2+

### Quick Start

From the project root:

```bash
docker compose up --build
```

This starts all three services with named volumes, health checks, and internal networking.

| URL | Service |
|-----|---------|
| http://localhost:8501 | Streamlit dashboard |
| http://localhost:8000 | FastAPI backend |
| http://localhost:8000/docs | API documentation |
| http://localhost:8000/health | Backend health check |

### Environment Variables

Copy the example file and adjust as needed:

```bash
cp .env.example .env
```

Docker Compose reads `.env` automatically. Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | `dataforge` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `dataforge` | PostgreSQL password |
| `POSTGRES_DB` | `dataforge` | PostgreSQL database name |
| `BACKEND_PORT` | `8000` | Host port for FastAPI |
| `DASHBOARD_PORT` | `8501` | Host port for Streamlit |
| `DATAFORGE_API_TIMEOUT` | `120` | Dashboard API timeout (seconds) |

Inside Docker, the dashboard connects to the backend at `http://backend:8000` via the `dataforge-network` bridge network. The backend connects to PostgreSQL at hostname `postgres`.

### Named Volumes

| Volume | Mount | Purpose |
|--------|-------|---------|
| `dataforge_postgres_data` | `/var/lib/postgresql/data` | PostgreSQL data |
| `dataforge_uploads_data` | `/app/uploads` | Uploaded dataset files |
| `dataforge_logs_data` | `/app/logs` | Application logs |

### Health Checks

- **PostgreSQL:** `pg_isready`
- **FastAPI:** `GET /health`
- **Streamlit:** `GET /_stcore/health`

Services start in order: PostgreSQL → Backend → Dashboard.

### Verify Deployment

```bash
# Check service status
docker compose ps

# Backend health
curl http://localhost:8000/health

# Warehouse history (empty on first run)
curl http://localhost:8000/warehouse/history

# Dashboard health
curl http://localhost:8501/_stcore/health
```

Open http://localhost:8501 and confirm the sidebar shows **API Status: healthy**.

### Stop and Clean Up

```bash
# Stop services
docker compose down

# Stop and remove volumes (deletes database and uploads)
docker compose down -v
```

### Rebuild After Code Changes

```bash
docker compose up --build
```

## Local Development (without Docker)

See [dashboard/README.md](dashboard/README.md) for dashboard setup.

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Dashboard:

```bash
pip install -r dashboard/requirements.txt
streamlit run dashboard/app.py
```

## API Endpoints

- `GET /health`
- `POST /upload`
- `POST /profile`
- `POST /analytics`
- `POST /quality-check`
- `POST /warehouse/load`
- `GET /warehouse/history`
