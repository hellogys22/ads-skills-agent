"""Main FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from api.analytics import router as analytics_router
from api.auth import router as auth_router
from api.campaigns import router as campaigns_router
from api.content import router as content_router
from api.products import router as products_router
from api.webhooks import router as webhooks_router
from config import get_settings
from jobs.scheduler import setup_scheduler
from models.database import close_mongo_connection, create_indexes

settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── WebSocket connection manager ──────────────────────────────────────────────

class ConnectionManager:
    def __init__(self) -> None:
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: dict) -> None:
        dead: list[WebSocket] = []
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting up Ads Skills Agent API...")
    await create_indexes()
    scheduler = setup_scheduler()
    scheduler.start()
    logger.info("APScheduler started")
    yield
    scheduler.shutdown(wait=False)
    await close_mongo_connection()
    logger.info("Shutdown complete")


# ── App factory ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="Ads Skills Agent API",
    description="Digital marketing multi-agent system with Instagram, Facebook & YouTube automation.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(settings.frontend_url), "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(content_router)
app.include_router(analytics_router)
app.include_router(products_router)
app.include_router(campaigns_router)
app.include_router(webhooks_router)

# ── Static files ──────────────────────────────────────────────────────────────

try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    pass  # static/ directory may not exist in development


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.environment,
    }


@app.get("/", tags=["System"])
async def root():
    return {"message": "Ads Skills Agent API", "docs": "/docs"}


# ── WebSocket endpoint ────────────────────────────────────────────────────────

@app.websocket("/ws/updates")
async def websocket_updates(websocket: WebSocket):
    """Real-time update stream for connected dashboard clients."""
    await manager.connect(websocket)
    logger.info("WebSocket client connected (total: %d)", len(manager.active))
    try:
        while True:
            data = await websocket.receive_json()
            # Echo back with server acknowledgement
            await websocket.send_json({"ack": True, "received": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected (total: %d)", len(manager.active))


# ── Error handlers ────────────────────────────────────────────────────────────

@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def generic_error_handler(request, exc: Exception):
    logger.error("Unhandled error: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
    )
