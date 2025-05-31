from app.schema import User
from sqlalchemy import select
from sqlmodel import Session


def get_user_br_column(session: Session, sub: str, column_name: str) -> User | None:
    stmt = select(User).where(getattr(User, column_name) == sub)
    return session.exec(stmt).scalar_one_or_none()


def update_user(session: Session, user: User, data: dict) -> User:
    for field, value in data.items():
        if hasattr(user, field) and value is not None:
            setattr(user, field, value)
    session.commit()
    session.refresh(user)
    return user
