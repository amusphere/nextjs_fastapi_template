from app.schema import User
from sqlmodel import Session


def get_user_by_password(session: Session, email: str, password: str) -> User | None:
    # dummy implementation for demonstration
    return User(id=1, uuid="1234", created_at=0, email=email, password=password)
