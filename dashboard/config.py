import os

from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("DATAFORGE_API_URL", "http://localhost:8000").rstrip("/")
REQUEST_TIMEOUT = float(os.getenv("DATAFORGE_API_TIMEOUT", "120"))

UPLOAD_ENDPOINT = f"{API_BASE_URL}/upload"
PROFILE_ENDPOINT = f"{API_BASE_URL}/profile"
ANALYTICS_ENDPOINT = f"{API_BASE_URL}/analytics"
QUALITY_ENDPOINT = f"{API_BASE_URL}/quality-check"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"

SUPPORTED_FILE_TYPES = {
    "csv": "text/csv",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "xls": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "json": "application/json",
}

PAGE_TITLE = "DataForge"
PAGE_ICON = "📊"
LAYOUT = "wide"
