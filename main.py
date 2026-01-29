"""
CryptoSwarm - Local Automated Crypto Trading Server
Main FastAPI application entry point.
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn

from config import settings
from app.database import init_db, get_db
from app.models.models import User
from app.utils.auth import create_default_user
from app.routers import auth, bots, trades, logs, swarm

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Local automated crypto trading server with AI-interpreted rules",
    version="1.0.0",
    debug=settings.debug
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(auth.router)
app.include_router(bots.router)
app.include_router(trades.router)
app.include_router(logs.router)
app.include_router(swarm.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database and create default user on startup."""
    init_db()
    
    # Create default admin user if no users exist
    db = next(get_db())
    try:
        create_default_user(db)
        print("Database initialized successfully")
        print("Default admin user created (username: admin, password: admin123)")
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Root endpoint - serves the main web UI.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    Dashboard page for viewing bots and performance.
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "1.0.0"
    }


@app.get("/status")
async def status():
    """
    System status endpoint.
    """
    from app.utils.kraken import kraken_client
    
    return {
        "app": settings.app_name,
        "version": "1.0.0",
        "kraken_initialized": kraken_client.is_initialized(),
        "ai_provider": settings.default_ai_provider,
        "evolution_enabled": settings.enable_evolution
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
