# DataForge Dashboard

Production-ready Streamlit dashboard for the DataForge platform. The dashboard communicates exclusively with the existing FastAPI backend via:

- `POST /upload`
- `POST /profile`
- `POST /analytics`
- `GET /health`

## Prerequisites

1. **DataForge backend running** on `http://localhost:8000`
2. **Python 3.12+**
3. **PostgreSQL** configured for the backend (if using full backend startup)

## Installation

From the project root:

```bash
cd dashboard
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Optional environment variables (create a `.env` in the project root or export them):

```bash
DATAFORGE_API_URL=http://localhost:8000
DATAFORGE_API_TIMEOUT=120
```

## Run the Backend

In a separate terminal, from the `backend` directory:

```bash
cd backend
source ../.venv/bin/activate   # or your backend virtualenv
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verify the API:

```bash
curl http://localhost:8000/health
```

## Run the Dashboard

From the project root:

```bash
streamlit run dashboard/app.py
```

Or from the `dashboard` directory:

```bash
streamlit run app.py
```

The dashboard opens at **http://localhost:8501**.

## Usage Workflow

1. Open **File Upload** in the sidebar.
2. Upload a CSV, Excel (`.xlsx`), or JSON file.
3. Click **Upload to DataForge**.
4. Click **Profile Dataset** and/or **Run Analytics**.
5. Navigate to **Dataset Overview** for summary cards, schema, and missing values.
6. Open **Analytics Explorer** for statistics, correlations, outliers, and charts.

## Features

- Wide layout with sidebar navigation
- KPI summary cards
- Profile and analytics actions with loading spinners
- Success and error alerts
- Tabs and expanders for structured exploration
- Charts: histogram, box plot, correlation heatmap, missing values bar chart, category distribution

## Project Structure

```
dashboard/
├── app.py              # Streamlit application entry point
├── api_client.py       # FastAPI HTTP client
├── charts.py           # Plotly chart builders
├── config.py           # Dashboard configuration
├── requirements.txt    # Dashboard dependencies
└── README.md           # This file
```

## Troubleshooting

| Issue | Solution |
|---|---|
| API unreachable in sidebar | Ensure backend is running on `DATAFORGE_API_URL` |
| Upload fails with MIME error | Use `.csv`, `.xlsx`, or `.json` with correct content type |
| Missing values chart empty | Run **Profile Dataset** before opening chart tabs |
| Analytics charts empty | Run **Run Analytics** after uploading a file |
