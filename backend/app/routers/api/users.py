from app.database import get_session
from app.models.user import UserModel
from app.schema import User
from app.services.auth import auth_user, get_user_sub
from app.services.user import create_new_user, get_user_info
from fastapi import APIRouter, Depends
from sqlmodel import Session

router = APIRouter(prefix="/users")


@router.post("/create", response_model=UserModel)
async def create_user(
    sub: str = Depends(get_user_sub),
    session: Session = Depends(get_session),
):
    user = get_user_info(session, sub)
    if user is None:
        user = create_new_user(session, sub)
    return user


@router.get("/me", response_model=UserModel)
async def get_current_user(user: User = Depends(auth_user)):
    return user
