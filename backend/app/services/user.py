from app.repositories.user import create_user, get_user_by_sub
from app.schema import User
from sqlmodel import Session


def get_user_info(session: Session, sub: str) -> User | None:
    return get_user_by_sub(session, sub)


def create_new_user(session: Session, sub: str) -> User:
    return create_user(session, {"clerk_sub": sub})
