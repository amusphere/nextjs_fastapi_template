from app.database import get_session
from app.models.auth import UserCreateModel, UserSignInModel, UserTokenModel
from app.utils.auth.email_password import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_new_user,
)
from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlmodel import Session

router = APIRouter(prefix="/auth")


@router.post("/signup", response_model=UserTokenModel)
async def create_user(
    data: UserCreateModel,
    session: Session = Depends(get_session),
):
    access_token = create_new_user(data, session)
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user",
        )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "refresh_token": None,
    }


@router.post("/signin", response_model=UserTokenModel)
async def sign_in(
    data: UserSignInModel = Form(...),
    session: Session = Depends(get_session),
):
    access_token = authenticate_user(
        email=data.email,
        password=data.password,
        session=session,
    )
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "refresh_token": None,
    }
