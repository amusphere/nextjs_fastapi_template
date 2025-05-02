import logging
import os
import sys

import httpx
from app.database import engine
from app.repositories.user import get_user_by_sub
from app.schema import User
from clerk_backend_api import AuthenticateRequestOptions, Clerk
from fastapi import HTTPException, Request, status
from sqlmodel import Session

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


async def get_user_sub(request: Request) -> str | None:
    headers_dict = {}
    for key, value in request.headers.items():
        headers_dict[key] = value

    httpx_req = httpx.Request(
        method=request.method,
        url=str(request.url),
        headers=headers_dict,
    )

    authorized_parties = [
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
    ]

    sdk = Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))
    request_state = sdk.authenticate_request(
        httpx_req,
        AuthenticateRequestOptions(authorized_parties=authorized_parties),
    )

    if request_state.is_signed_in:
        return request_state.payload["sub"]
    else:
        logger.error("Not authenticated: %s", request_state.reason)
        return None


async def auth_user(request: Request) -> User:
    sub = await get_user_sub(request)
    if sub is None:
        logger.error("Authentication failed: user_sub is None")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated",
        )

    session = Session(engine)
    user = get_user_by_sub(session, sub)
    if user is None:
        logger.warning("User not found: %s", sub)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
