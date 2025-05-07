from app.models.user import UserModel
from app.schema import User
from app.services.auth import add_new_user, auth_user, user_sub
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/users")


@router.post("/create", response_model=UserModel)
async def create_user(sub: str = Depends(user_sub)):
    return add_new_user(sub)


@router.get("/me", response_model=UserModel)
async def get_current_user(user: User = Depends(auth_user)):
    return user
