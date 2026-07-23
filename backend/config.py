"""
Application configuration management.
Loads settings from environment variables with sensible defaults.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ─── Base Paths ────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "backend" / "reports"
MODELS_DIR = BASE_DIR / "backend" / "ml_models"
DATA_DIR = BASE_DIR / "data"
DATASETS_DIR = BASE_DIR / "backend" / "datasets"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
for d in [REPORTS_DIR, MODELS_DIR, DATA_DIR, DATASETS_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ─── Database ──────────────────────────────────────────────────
# Use SQLite by default for easy local development; set DATABASE_URL for PostgreSQL
_SQLITE_PATH = BASE_DIR / "fraud_detection.db"
USE_SQLITE = os.getenv("USE_SQLITE", "true").lower() == "true"

if USE_SQLITE:
    DATABASE_URL = f"sqlite+aiosqlite:///{_SQLITE_PATH}"
    DATABASE_URL_SYNC = f"sqlite:///{_SQLITE_PATH}"
else:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/fraud_detection"
    )
    DATABASE_URL_SYNC = os.getenv(
        "DATABASE_URL_SYNC",
        "postgresql://postgres:postgres@localhost:5432/fraud_detection"
    )

# ─── Redis / Celery ───────────────────────────────────────────
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

# ─── NVIDIA AI API ─────────────────────────────────────────────
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_API_BASE_URL = os.getenv(
    "NVIDIA_API_BASE_URL",
    "https://integrate.api.nvidia.com/v1"
)
NVIDIA_MODEL = os.getenv(
    "NVIDIA_MODEL",
    "meta/llama-3.1-8b-instruct"
)

# ─── OAuth Settings ───────────────────────────────────────────
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")

# ─── JWT Authentication ───────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "fraud-detection-secret-key-change-in-prod")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

# ─── App Settings ──────────────────────────────────────────────
APP_TITLE = "AI Fraud Detection System"
APP_VERSION = "3.0.0"
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# ─── CORS ──────────────────────────────────────────────────────
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
).split(",")
