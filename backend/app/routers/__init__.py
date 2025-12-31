"""
Routers Package
API route handlers.
"""
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.clients import router as clients_router
from app.routers.escalations import router as escalations_router
from app.routers.notes import router as notes_router
from app.routers.analytics import router as analytics_router
from app.routers.departments import router as departments_router

__all__ = [
    "auth_router",
    "users_router",
    "clients_router",
    "escalations_router",
    "notes_router",
    "analytics_router",
    "departments_router"
]
