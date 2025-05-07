import os

from app.schema import User
from fastapi import Depends, HTTPException, status

AUTH_SYSTEM = os.getenv("AUTH_SYSTEM")

if AUTH_SYSTEM == "clerk":
    from app.utils.auth.clerk import create_new_user, get_auth_sub, get_authed_user
else:
    from app.utils.auth.email_password import (
        create_new_user,
        get_auth_sub,
        get_authed_user,
    )


async def user_sub(sub=Depends(get_auth_sub)) -> str | None:
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return sub


async def auth_user(sub=Depends(get_auth_sub)) -> User:
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
    return user
