from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routers import onboard, upload, extract, recommend, report

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Credit Underwriting Platform - MVP",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(onboard.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")
app.include_router(extract.router, prefix="/api/v1")
app.include_router(recommend.router, prefix="/api/v1")
app.include_router(report.router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization warning: {e}")


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "onboard": "/api/v1/onboard",
            "upload": "/api/v1/upload",
            "extract": "/api/v1/extract",
            "recommend": "/api/v1/recommend",
            "report": "/api/v1/report"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
