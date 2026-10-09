import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.ai_learning.router import router as ai_router
from app.auth.router import router as auth_router
from app.catalog.router import router as catalog_router
from app.play.router import router as play_router
from app.projects.router import router as projects_router
from app.settings.router import router as settings_router

load_dotenv()

app = FastAPI(title="2D Engine", version="2.0.0")

# Origins allowed to call this API from a browser (comma separated).
_origins = os.environ.get("FRONTEND_ORIGINS", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins.split(",") if o.strip()],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(ai_router)
app.include_router(play_router)
app.include_router(settings_router)
app.include_router(catalog_router)


@app.get("/health")
def health():
    return {"ok": True}
