import sys
import asyncio
from pathlib import Path

# Add root directory to python path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from backend.main import app
from backend.database import init_db

# Ensure SQLite DB & tables exist on serverless cold-start
@app.on_event("startup")
async def startup_event():
    try:
        await init_db()
    except Exception:
        pass

