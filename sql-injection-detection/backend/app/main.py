from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.api import detect, demo, analytics, logs, models, admin, stress_test

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
    version="1.0.0",
    description="Advanced SQL Injection Detection & Prevention System with ML and XAI"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(detect.router, prefix=f"{settings.API_V1_PREFIX}/detect", tags=["Detection"])
app.include_router(demo.router, prefix=f"{settings.API_V1_PREFIX}/demo", tags=["Demo"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_PREFIX}/analytics", tags=["Analytics"])
app.include_router(logs.router, prefix=f"{settings.API_V1_PREFIX}/logs", tags=["Logs"])
app.include_router(models.router, prefix=f"{settings.API_V1_PREFIX}/models", tags=["Models"])
app.include_router(admin.router, prefix=f"{settings.API_V1_PREFIX}/admin", tags=["Admin"])
app.include_router(stress_test.router, prefix=f"{settings.API_V1_PREFIX}/stress-test", tags=["Stress Test"])

@app.get("/")
async def root():
    return {
        "message": "SQL Injection Detection API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "api": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
