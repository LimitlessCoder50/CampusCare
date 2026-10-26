from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api_v1 import api_router
from app.core.database import get_supabase_client
import logging

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("campuscare")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]")
    if "your-project-id" in settings.SUPABASE_URL:
        logger.warning(
            "⚠️  SUPABASE_URL is currently using a placeholder value. "
            "Please update backend/.env with your actual Supabase project credentials."
        )
    yield
    # Shutdown actions
    logger.info("Shutting down CampusCare API.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for CampusCare: Web-Based Campus Asset Reporting and Ticketing System, connected to Supabase.",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS if isinstance(settings.ALLOWED_ORIGINS, list) else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pathlib import Path
from starlette.staticfiles import StaticFiles

# Include v1 endpoints
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount frontend static directory if exists
frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/portal", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


@app.get("/", tags=["General"], summary="Root API health and information")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "portal_url": "/portal/",
        "status": "online",
        "tables_supported": [
            "public.users (student, faculty)",
            "public.maintenance_personnel (department, category, employment_status)",
            "public.admin (school_id, role=admin)",
        ],
    }


@app.get("/health", tags=["General"], summary="Health and Supabase connection status")
def health_check():
    configured = (
        bool(settings.SUPABASE_URL)
        and "your-project-id" not in settings.SUPABASE_URL
        and bool(settings.SUPABASE_KEY)
        and "your-anon-public-key" not in settings.SUPABASE_KEY
    )
    return {
        "status": "healthy",
        "supabase_configured": configured,
        "supabase_url": settings.SUPABASE_URL if configured else "Not configured (using placeholder)",
    }
