import logging
import os
import sys

from app.schema import User
from fastapi import Depends, HTTPException, status

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

clerk_secret_key = os.getenv("CLERK_SECRET_KEY")
if clerk_secret_key is not None:
    from app.utils.auth.clerk import create_new_user, get_auth_sub, get_authed_user
else:
    from app.utils.auth.email_password import (
        create_new_user,
        get_auth_sub,
        get_authed_user,
    )


async def user_sub(sub = Depends(get_auth_sub)) -> str | None:
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return sub


async def auth_user(sub = Depends(get_auth_sub)) -> User:
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    user = await get_authed_user(sub)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


def add_new_user(sub: str) -> User:
    user = create_new_user(sub)

    if user is None:
        logger.error("User not found in Clerk: %s", sub)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in Clerk",
        )

    return user
