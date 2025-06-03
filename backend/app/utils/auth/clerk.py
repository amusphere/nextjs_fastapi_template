import logging
import os
import sys

import httpx
from app.database import get_engine
from app.repositories.user import get_user_br_column
from app.schema import User
from clerk_backend_api import AuthenticateRequestOptions, Clerk
from clerk_backend_api import User as ClerkUser
from fastapi import Depends, Request
from fastapi.security import HTTPBearer
from sqlmodel import Session

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
AUTHORIZED_PARTIES = [
    os.getenv("FRONTEND_URL", "http://localhost:3000"),
]

security = HTTPBearer()


async def get_auth_sub(request: Request, credentials=Depends(security)) -> str | None:
    httpx_req = httpx.Request(
        method=request.method,
        url=str(request.url),
        headers={
            "Authorization": f"Bearer {credentials.credentials}",
        },
    )

    sdk = Clerk(bearer_auth=CLERK_SECRET_KEY)
    request_state = sdk.authenticate_request(
        httpx_req,
        AuthenticateRequestOptions(authorized_parties=AUTHORIZED_PARTIES),
    )

    if request_state.is_signed_in:
        return request_state.payload["sub"]
    else:
        logger.error("Not authenticated: %s", request_state.reason)
        return None


async def get_authed_user(sub: str) -> User | None:
    session = Session(get_engine())
    user = get_user_br_column(session, sub, "clerk_sub")
    session.close()
    return user


def create_new_user(sub: str) -> User:
    sdk = Clerk(bearer_auth=CLERK_SECRET_KEY)
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
    session = Session(get_engine())
    session.add(user)
    session.commit()
    session.refresh(user)
    session.close()
    return user
