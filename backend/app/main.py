from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as analyze_router
from app.core.config import settings


def build_allowed_origins() -> list[str]:
    origins = [origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()]
    # Always allow localhost for development
    localhost_origins = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173", "http://127.0.0.1:3000"]
    for lo in localhost_origins:
        if lo not in origins:
            origins.append(lo)
    return origins


app = FastAPI(title="AI Interview Analyzer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=build_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)

app.include_router(analyze_router, prefix="/api")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


STATIC_DIR = Path(__file__).resolve().parent / "static"
ASSETS_DIR = STATIC_DIR / "assets"

if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")


@app.get("/", include_in_schema=False)
async def serve_root() -> FileResponse:
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=503, detail="Frontend build artifacts are missing")
    return FileResponse(index_file)


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str) -> FileResponse:
    target = STATIC_DIR / full_path
    if target.is_file():
        return FileResponse(target)

    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=503, detail="Frontend build artifacts are missing")
    return FileResponse(index_file)
