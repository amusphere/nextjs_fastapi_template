import os

from app.database import get_session
from app.models.user import UserModel, UserUpdateModel
from app.repositories.user import update_user
from app.schema import User
from app.services.auth import add_new_user, auth_user, user_sub
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

router = APIRouter(prefix="/users")

AUTH_SYSTEM = os.getenv("AUTH_SYSTEM")


@router.post("/create", response_model=UserModel)
async def create_user(sub: str = Depends(user_sub)):
    """This endpoint is used to create a new user from Clerk."""
    if AUTH_SYSTEM == "email_password":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email/Password authentication system does not support user creation.",
        )
    return add_new_user(sub)


@router.get("/me", response_model=UserModel)
async def get_current_user(user: User = Depends(auth_user)):
    return user


@router.put("/me", response_model=UserModel)
async def update_current_user(
    data: UserUpdateModel,
    user: User = Depends(auth_user),
    session: Session = Depends(get_session),
):
    user = session.merge(user)
    return update_user(session, user, data.model_dump())
