from datetime import datetime, timedelta
from uuid import uuid4

from sqlmodel import Session, select

from app.schema import PasswordResetToken


DEFAULT_EXPIRES_SECONDS = 60 * 60  # 1 hour


def create_password_reset_token(
    session: Session, user_id: int, expires_in: int = DEFAULT_EXPIRES_SECONDS
) -> PasswordResetToken:
    token = uuid4().hex
    expires_at = datetime.now().timestamp() + expires_in
    token_entry = PasswordResetToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
    )
    session.add(token_entry)
    session.commit()
    session.refresh(token_entry)
    return token_entry


def get_user_by_token(session: Session, token: str):
    stmt = select(PasswordResetToken).where(PasswordResetToken.token == token)
    token_entry = session.exec(stmt).one_or_none()
    if token_entry is None:
        return None
    if token_entry.expires_at < datetime.now().timestamp():
        return None
    user = token_entry.user
    return user
