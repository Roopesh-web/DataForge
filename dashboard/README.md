# DataForge Dashboard

Production-ready Streamlit dashboard for the DataForge platform. The dashboard communicates exclusively with the existing FastAPI backend via:

- `POST /upload`
- `POST /profile`
- `POST /analytics`
- `POST /quality-check`
- `POST /warehouse/load`
- `GET /warehouse/history`
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

1. Open **Home** for KPI cards, recent upload history, and the dataset timeline.
2. Go to **Upload** and upload a CSV, Excel (`.xlsx`), or JSON file.
3. Click **Upload to DataForge**, then use quick actions for Profile, Analytics, or Quality.
4. Navigate to **Dataset Overview** for summary cards, schema, and missing values.
5. Open **Analytics** for statistics, correlations, outliers, and charts.
6. Open **Data Quality** to run validation checks and review quality score, passed rules, and failed rules.
7. Open **Warehouse** to load datasets into PostgreSQL and review load history.
8. Open **History** for full upload and activity timelines.
9. Use **Settings** and **About** for connection info and platform details.

## Features

- Dark enterprise theme with improved typography and card styling
- Nine-page sidebar navigation: Home, Upload, Dataset Overview, Analytics, Data Quality, Warehouse, History, Settings, About
- Home page KPI cards: total datasets, rows processed, average quality score, warehouse tables
- Recent upload history table and dataset activity timeline
- Responsive Plotly charts with dark theme, improved colors, and spacing
- Footer: DataForge v1.0 · FastAPI · Streamlit · PostgreSQL
- Profile and analytics actions with loading spinners
- Success and error alerts
- Tabs and expanders for structured exploration
- Charts: histogram, box plot, correlation heatmap, missing values bar chart, category distribution, dataset timeline

## Project Structure

```
dashboard/
├── app.py              # Streamlit application entry point
├── api_client.py       # FastAPI HTTP client
├── charts.py           # Plotly chart builders
├── config.py           # Dashboard configuration
├── state.py            # Session state and dashboard metrics
├── ui.py               # UI components, styling, and layout helpers
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
| Quality page empty | Run **Quality Check** after uploading a file |
