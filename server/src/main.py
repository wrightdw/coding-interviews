"""Main FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers import sessions, execute, collaboration
from src.websocket import router as ws_router

app = FastAPI(
    title="Code Interview Platform API",
    description="Backend API for collaborative coding interviews",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sessions.router, prefix="/api", tags=["sessions"])
app.include_router(execute.router, prefix="/api", tags=["execution"])
app.include_router(collaboration.router, prefix="/api", tags=["collaboration"])
app.include_router(ws_router, tags=["websocket"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Code Interview Platform API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
