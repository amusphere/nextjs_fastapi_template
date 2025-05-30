from app.routers.api.auth import router as auth_router
from app.routers.api.health import router as health_router
from app.routers.api.users import router as users_router
from app.routers.api.chat import router as chat_router
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(health_router, prefix="/api", tags=["health"])
api_router.include_router(auth_router, prefix="/api", tags=["auth"])
api_router.include_router(users_router, prefix="/api", tags=["users"])
api_router.include_router(chat_router, prefix="/api", tags=["chat"])
