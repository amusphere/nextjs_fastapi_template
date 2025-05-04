import logging
import os
import sys

import httpx
from app.database import engine
from app.repositories.user import get_user_by_sub
from app.schema import User
from clerk_backend_api import AuthenticateRequestOptions, Clerk
from clerk_backend_api import User as ClerkUser
from fastapi import Request
from sqlmodel import Session

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


async def get_auth_sub(request: Request) -> str | None:
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


async def get_authed_user(request: Request) -> User | None:
    sub = await get_auth_sub(request)
    if sub is None:
        return None

    session = Session(engine)
    user = get_user_by_sub(session, sub, "clerk_sub")
    return user


def create_new_user(session: Session, sub: str) -> User:
    sdk = Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))
    clerk_user: ClerkUser = sdk.users.get(user_id=sub)

    email = None
    for email_address in clerk_user.email_addresses:
        if email_address.id == clerk_user.primary_email_address_id:
            email = email_address.email_address
            break

    user = User(
        email=email,
        name=clerk_user.username,
        clerk_sub=sub,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
