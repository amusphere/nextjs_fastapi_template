import logging
import sys

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/signin")


async def get_token(token: str = Depends(oauth2_scheme)):
    return token


async def get_user_sub(request: Request) -> str | None:
    pass
