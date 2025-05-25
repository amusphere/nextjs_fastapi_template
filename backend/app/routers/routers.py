from app.routers.api.auth import router as auth_router
from app.routers.api.google_oauth import router as google_oauth_router
from app.routers.api.health import router as health_router
from app.routers.api.users import router as users_router
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(health_router, prefix="/api", tags=["api"])
api_router.include_router(auth_router, prefix="/api", tags=["api"])
api_router.include_router(users_router, prefix="/api", tags=["api"])
api_router.include_router(google_oauth_router, prefix="/api", tags=["api"])
