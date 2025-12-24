"""
FastAPI Application Entry Point
Escalation Tracker - Internal Escalation Intelligence Platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import (
    auth_router,
    users_router,
    clients_router,
    escalations_router,
    notes_router,
    analytics_router
)
from app.core.websocket import manager
from jose import jwt

settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="Escalation Tracker API",
    description="""
    Internal escalation intelligence platform for managing client complaints.
    
    ## Features
    - **Email Ingestion**: Automatic complaint capture from Outlook
    - **AI Analysis**: Gemini-powered complaint classification and sentiment analysis
    - **Assignment**: Manager-controlled assignment of escalations to resolvers
    - **Tracking**: Full lifecycle tracking with 60-day SLA
    - **Analytics**: Dashboard, client, and team performance metrics
    
    ## Roles
    - **Admin**: Full system access
    - **Manager**: Oversees escalations, approves assignments, views analytics
    - **Viewer**: Read-only visibility; becomes resolver when assigned
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - configure for your frontend URL in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(clients_router)
app.include_router(escalations_router)
app.include_router(notes_router)
app.include_router(analytics_router)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    if not token:
        await websocket.close(code=1008)
        return
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=1008)
            return
    except Exception:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
