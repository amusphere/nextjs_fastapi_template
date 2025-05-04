from app.database import get_session
from app.models.auth import UserCreateModel, UserSignInModel, UserTokenModel
from fastapi import APIRouter, Depends, Form
from sqlmodel import Session

router = APIRouter(prefix="/auth")


@router.post("/signup", response_model=UserTokenModel)
async def create_user(
    data: UserCreateModel,
    session: Session = Depends(get_session),
):
    return {
        "access_token": "dummy_access_token",
        "token_type": "bearer",
        "expires_in": 3600,
        "refresh_token": "dummy_refresh_token",
    }


@router.post("/signin", response_model=UserTokenModel)
async def sign_in(
    data: UserSignInModel = Form(...),
    # session: Session = Depends(get_session),
):
    # user = get_user_by_password(session, data.email, data.password)
    # if user is None:
    # raise HTTPException(status_code=400, detail="Invalid credentials")
    return {
        "access_token": "dummy_access_token",
        "token_type": "bearer",
        "expires_in": 3600,
        "refresh_token": "dummy_refresh_token",
    }
