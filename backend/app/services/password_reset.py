import logging
import os

from app.repositories.user import get_user_br_column, update_user_password
from app.utils.auth.email_password import (
    create_password_reset_token,
    verify_password_reset_token,
    get_password_hash,
)
from sqlmodel import Session

logger = logging.getLogger(__name__)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


def request_password_reset(email: str, session: Session) -> bool:
    user = get_user_br_column(session, email, "email")
    if not user:
        logger.error("Password reset requested for non-existent user: %s", email)
        return False
    token = create_password_reset_token(email)
    reset_url = f"{FRONTEND_URL}/auth/reset-password?token={token}"
    logger.info("Password reset URL for %s: %s", email, reset_url)
    print(f"Password reset URL for {email}: {reset_url}")
    return True


def reset_password(token: str, new_password: str, session: Session) -> bool:
    email = verify_password_reset_token(token)
    if not email:
        logger.error("Invalid password reset token")
        return False
    hashed = get_password_hash(new_password)
    return update_user_password(session, email, hashed)
