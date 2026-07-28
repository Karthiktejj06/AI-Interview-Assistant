import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database.connection import init_db
from backend.routers import auth, resume, interview, report, analytics

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown events handler.
    """
    logger.info(f"Starting {settings.APP_NAME} Backend...")
    # Initialize database tables
    init_db()
    yield
    logger.info(f"Shutting down {settings.APP_NAME} Backend.")

app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise AI Interview Assistant Backend API built with FastAPI, SQLite, and Google Gemini API.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Policy configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static uploads directory for resumes and pdf reports
app.mount("/static", StaticFiles(directory=settings.UPLOAD_DIR), name="static")

# Include API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(resume.router, prefix=settings.API_V1_STR)
app.include_router(interview.router, prefix=settings.API_V1_STR)
app.include_router(report.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Health Check"])
def root():
    return {
        "app": settings.APP_NAME,
        "status": "healthy",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/v1/health", tags=["Health Check"])
def health_check():
    return {
        "status": "online",
        "environment": settings.APP_ENV,
        "database": "connected"
    }
