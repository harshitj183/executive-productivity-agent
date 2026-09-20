"""
FastAPI application — serves both the API and the built React frontend.
In production (Railway/Render) the frontend dist folder is copied next to
the backend before deploy, so everything ships as one process.
"""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.routes import router

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Path to the built React app — ../frontend/dist relative to this file
DIST_DIR = Path(__file__).parent.parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Executive Productivity Agent starting up.")
    logger.info(f"Model: {os.getenv('GROQ_MODEL', 'qwen/qwen3.8-27b')}")
    logger.info(f"Frontend dist: {DIST_DIR} (exists={DIST_DIR.exists()})")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="Executive Productivity Agent",
    description="AI agent for executive commitment tracking and daily briefing.",
    version="1.0.0",
    lifespan=lifespan,
    # Hide docs in production to keep it clean
    docs_url="/api/docs",
    redoc_url=None,
)

# CORS — only needed during local dev (frontend on :5173, API on :8000)
# In production both are served from the same origin so CORS is irrelevant.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "https://executive-productivity-agent-h74i.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(router, prefix="/api")


# ── Serve React static files ──────────────────────────────────────────────────

if DIST_DIR.exists():
    # Serve static assets (JS/CSS/images)
    app.mount(
        "/assets",
        StaticFiles(directory=str(DIST_DIR / "assets")),
        name="assets",
    )

    @app.get("/favicon.svg")
    async def favicon():
        return FileResponse(str(DIST_DIR / "favicon.svg"))

    # Catch-all: any non-API route returns index.html (React Router SPA)
    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        index = DIST_DIR / "index.html"
        return FileResponse(str(index))

else:
    @app.get("/")
    async def root():
        return {
            "name": "Executive Productivity Agent API",
            "version": "1.0.0",
            "note": "Frontend not built. Run: cd frontend && npm run build",
            "api_docs": "/api/docs",
        }
