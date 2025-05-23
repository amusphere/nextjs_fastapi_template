from app.schema import User
from sqlalchemy import select
from sqlmodel import Session


def create_user(session: Session, data: dict) -> User:
    user = User(**data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user_br_column(session: Session, sub: str, column_name: str) -> User | None:
    stmt = select(User).where(getattr(User, column_name) == sub)
    return session.exec(stmt).scalar_one_or_none()
