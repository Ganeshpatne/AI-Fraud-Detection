"""
FastAPI application entrypoint.
AI Fraud Detection System v3.0
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import (
    APP_TITLE, APP_VERSION, CORS_ORIGINS, REPORTS_DIR
)
from backend.database import init_db
from backend.utils.logging_config import setup_logging

# Setup logging first
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup & shutdown lifecycle."""
    logger.info("Starting %s v%s", APP_TITLE, APP_VERSION)
    await init_db()
    logger.info("Database tables initialized.")
    yield
    logger.info("Shutting down %s", APP_TITLE)


# ─── Create app ────────────────────────────────────────────────
app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description="Production-grade AI-powered fraud detection platform with NVIDIA AI integration",
    lifespan=lifespan,
)

# ─── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Static files (reports) ───────────────────────────────────
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/reports", StaticFiles(directory=str(REPORTS_DIR)), name="reports")

# ─── Register routers ─────────────────────────────────────────
from backend.routes.auth import router as auth_router
from backend.routes.transactions import router as txn_router
from backend.routes.users import router as users_router
from backend.routes.fraud_intelligence import router as fraud_router
from backend.routes.analytics import router as analytics_router
from backend.routes.datasets import router as datasets_router
from backend.routes.ai_investigation import router as ai_investigation_router
from backend.routes.chatbot import router as chatbot_router

app.include_router(auth_router)
app.include_router(txn_router)
app.include_router(users_router)
app.include_router(fraud_router)
app.include_router(analytics_router)
app.include_router(datasets_router)
app.include_router(ai_investigation_router)
app.include_router(chatbot_router)

# ─── WebSocket endpoint ───────────────────────────────────────
from backend.services.websocket_manager import ws_manager


@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """Real-time fraud alert WebSocket endpoint."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive; client can also send messages
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


# ─── Health check ──────────────────────────────────────────────
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": APP_TITLE,
        "version": APP_VERSION,
    }


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {APP_TITLE}",
        "version": APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }
