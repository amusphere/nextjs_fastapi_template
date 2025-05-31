import hashlib
import os
import secrets
from datetime import datetime, timedelta

from app.repositories.password_reset import (
    create_token,
    get_active_token_by_hash,
)
from app.repositories.user import get_user_br_column
from app.utils.auth.email_password import get_password_hash
from fastapi import HTTPException, status
from sqlmodel import Session

TOKEN_EXPIRE_MINUTES = 1440
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def request_password_reset(email: str, session: Session) -> None:
    user = get_user_br_column(session, email, "email")
    if not user:
        return
    plain_token = secrets.token_urlsafe(32)
    token_hash = _hash_token(plain_token)
    expires_at = datetime.now() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    create_token(session, user.id, token_hash, expires_at)
    reset_url = f"{FRONTEND_URL}/auth/reset-password?token={plain_token}"
    print(f"Password reset URL for {email}: {reset_url}")


def reset_password(token: str, new_password: str, session: Session) -> None:
    token_hash = _hash_token(token)
    token_entry = get_active_token_by_hash(session, token_hash)
    if not token_entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token",
        )
    if token_entry.expires_at < datetime.now().timestamp():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expired",
        )
    user = token_entry.user
    user.password = get_password_hash(new_password)
    session.add(user)
    session.delete(token_entry)
    session.commit()
