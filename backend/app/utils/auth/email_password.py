import logging
import os
import sys
from datetime import datetime, timedelta

import jwt
from app.models.auth import UserCreateModel
from app.repositories.user import get_user_br_column
from app.schema import User
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlmodel import Session

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY")
# Fallback for local/dev/test environments where SECRET_KEY is not provided.
if not SECRET_KEY:
    # Allow alternative var name if provided
    SECRET_KEY = os.getenv("JWT_SECRET")
if not SECRET_KEY:
    SECRET_KEY = "insecure-dev-secret"
    logger.warning(
        "SECRET_KEY is not set; using insecure default for dev/test. Set SECRET_KEY in env."
    )
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/signin")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_sub(user: User) -> dict:
    return {
        "sub": user.email,
    }


def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(email: str, password: str, session: Session) -> str | None:
    user = get_user_br_column(session, email, "email")
    if not user:
        logger.error("User not found: %s", email)
        return None
    if not verify_password(password, user.password):
        logger.error("Incorrect password for user: %s", email)
        return None
    access_token = create_access_token(
        data=create_sub(user),
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return access_token


async def get_auth_sub(token: str = Depends(oauth2_scheme)) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
    except Exception as e:
        logger.error("JWT Error: %s", e)
        return None

    if sub is None:
        logger.error("Not authenticated: %s", payload)
        return None

    return sub


async def get_authed_user(sub: str) -> User | None:
    from app.utils.database_utils import get_db_session

    with get_db_session() as session:
        user = get_user_br_column(session, sub, "email")
        return user


def create_new_user(data: UserCreateModel, session: Session) -> str | None:
    user = get_user_br_column(session, data.email, "email")
    if user:
        logger.error("User already exists: %s", data.email)
        return None

    user = User(
        email=data.email,
        name=data.username,
        password=get_password_hash(data.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    sub_data = create_sub(user)
    access_token = create_access_token(
        data=sub_data,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return access_token
