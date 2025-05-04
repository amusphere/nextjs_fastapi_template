from app.database import get_session
from app.models.user import UserModel
from app.repositories.user import get_user_by_sub
from app.schema import User
from app.services.auth import add_new_user, auth_user, user_sub
from fastapi import APIRouter, Depends
from sqlmodel import Session

router = APIRouter(prefix="/users")


@router.post("/create", response_model=UserModel)
async def create_user(
    sub: str = Depends(user_sub),
    session: Session = Depends(get_session),
):
    user = get_user_by_sub(session, sub, "clerk_sub")
    if user is None:
        user = add_new_user(session, sub)
    return user


@router.get("/me", response_model=UserModel)
async def get_current_user(user: User = Depends(auth_user)):
    return user
