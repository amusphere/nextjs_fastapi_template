import logging
import os
import sys

from app.database import engine
from app.schema import User
from fastapi import HTTPException, Request, status
from sqlmodel import Session

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

clerk_secret_key = os.getenv("CLERK_SECRET_KEY")
if clerk_secret_key is not None:
    from app.utils.auth.clerk import create_new_user, get_auth_sub, get_authed_user
else:
    raise ValueError(
        "CLERK_SECRET_KEY environment variable is not set. Please set it to use Clerk authentication."
    )


async def user_sub(request: Request) -> str | None:
    return await get_auth_sub(request)


async def auth_user(request: Request) -> User:
    user = await get_authed_user(request)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


def add_new_user(session: Session, sub: str) -> User:
    user = create_new_user(session, sub)

    if user is None:
        logger.error("User not found in Clerk: %s", sub)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in Clerk",
        )

    return user
