from datetime import datetime
from typing import Optional

from sqlmodel import Session, select

from app.schema import PasswordResetToken


def create_token(
    session: Session,
    user_id: int,
    token_hash: str,
    expires_at: datetime,
) -> PasswordResetToken:
    token = PasswordResetToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at.timestamp(),
    )
    session.add(token)
    session.commit()
    session.refresh(token)
    return token


def get_active_token_by_hash(
    session: Session, token_hash: str
) -> Optional[PasswordResetToken]:
    stmt = select(PasswordResetToken).where(
        PasswordResetToken.token_hash == token_hash,
        PasswordResetToken.used.is_(False),
    )
    return session.exec(stmt).first()


def mark_token_used(session: Session, token: PasswordResetToken) -> None:
    token.used = True
    session.add(token)
    session.commit()
