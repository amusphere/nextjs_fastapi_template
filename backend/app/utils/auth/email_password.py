import logging
import sys

from app.database import engine
from app.repositories.user import get_user_br_column
from app.schema import User
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/signin")


async def get_auth_sub(token: str = Depends(oauth2_scheme)) -> str | None:
    return token


async def get_authed_user(sub: str) -> User | None:
    session = Session(engine)
    user = get_user_br_column(session, sub, "email")
    session.close()
    return user


def create_new_user(sub: str) -> User:
    pass
