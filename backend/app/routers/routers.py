from app.routers.api.health import router as health_router
from app.routers.api.users import router as users_router
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(users_router)
