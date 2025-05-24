from datetime import datetime
from typing import Optional

from sqlmodel import Session, select

from ..database import get_session
from ..schema import GoogleOAuthToken


def find_active_token_by_user_id(
    user_id: int, session: Optional[Session] = None
) -> Optional[GoogleOAuthToken]:
    """ユーザーIDでアクティブなトークンを検索"""
    with session or get_session() as s:
        return s.exec(
            select(GoogleOAuthToken).where(
                GoogleOAuthToken.user_id == user_id,
                GoogleOAuthToken.is_active,
            )
        ).first()


def find_all_active_tokens_by_user_id(
    user_id: int, session: Optional[Session] = None
) -> list[GoogleOAuthToken]:
    """ユーザーIDでアクティブなトークンを全て検索"""
    with session or get_session() as s:
        return s.exec(
            select(GoogleOAuthToken).where(
                GoogleOAuthToken.user_id == user_id,
                GoogleOAuthToken.is_active,
            )
        ).all()


def create_oauth_token(
    oauth_token: GoogleOAuthToken, session: Optional[Session] = None
) -> GoogleOAuthToken:
    """新しいOAuthトークンを作成"""
    with session or get_session() as s:
        s.add(oauth_token)
        s.commit()
        s.refresh(oauth_token)
        return oauth_token


def update_oauth_token(
    oauth_token: GoogleOAuthToken, session: Optional[Session] = None
) -> GoogleOAuthToken:
    """既存のOAuthトークンを更新"""
    oauth_token.updated_at = datetime.now().timestamp()
    with session or get_session() as s:
        s.add(oauth_token)
        s.commit()
        s.refresh(oauth_token)
        return oauth_token


def update_token_data(
    token_id: int,
    access_token: str,
    refresh_token: Optional[str] = None,
    expires_at: Optional[float] = None,
    session: Optional[Session] = None,
) -> Optional[GoogleOAuthToken]:
    """トークンデータを更新"""
    with session or get_session() as s:
        oauth_token = s.get(GoogleOAuthToken, token_id)
        if oauth_token:
            oauth_token.access_token = access_token
            if refresh_token:
                oauth_token.refresh_token = refresh_token
            oauth_token.expires_at = expires_at
            oauth_token.updated_at = datetime.now().timestamp()

            s.add(oauth_token)
            s.commit()
            s.refresh(oauth_token)
            return oauth_token
        return None


def delete_oauth_token_by_id(token_id: int, session: Optional[Session] = None) -> bool:
    """IDでトークンを物理削除"""
    with session or get_session() as s:
        oauth_token = s.get(GoogleOAuthToken, token_id)
        if oauth_token:
            s.delete(oauth_token)
            s.commit()
            return True
        return False


def delete_all_active_tokens_by_user_id(
    user_id: int, session: Optional[Session] = None
) -> int:
    """ユーザーのアクティブなトークンを全て物理削除"""
    with session or get_session() as s:
        tokens = find_all_active_tokens_by_user_id(user_id, s)
        count = len(tokens)
        for token in tokens:
            s.delete(token)
        s.commit()
        return count


def deactivate_all_tokens_by_user_id(
    user_id: int, session: Optional[Session] = None
) -> int:
    """ユーザーのアクティブなトークンを全て無効化"""
    with session or get_session() as s:
        tokens = find_all_active_tokens_by_user_id(user_id, s)
        count = len(tokens)
        for token in tokens:
            token.is_active = False
            s.add(token)
        s.commit()
        return count


def upsert_oauth_token(
    user_id: int,
    access_token: str,
    refresh_token: Optional[str] = None,
    expires_at: Optional[float] = None,
    scope: Optional[str] = None,
    google_user_id: Optional[str] = None,
    google_email: Optional[str] = None,
    session: Optional[Session] = None,
) -> GoogleOAuthToken:
    """OAuth トークンをアップサート（存在すれば更新、なければ作成）"""
    with session or get_session() as s:
        existing_token = find_active_token_by_user_id(user_id, s)

        if existing_token:
            # 既存のトークンを更新
            existing_token.access_token = access_token
            existing_token.refresh_token = refresh_token
            existing_token.expires_at = expires_at
            existing_token.scope = scope
            existing_token.google_user_id = google_user_id
            existing_token.google_email = google_email
            existing_token.updated_at = datetime.now().timestamp()

            s.add(existing_token)
            s.commit()
            s.refresh(existing_token)
            return existing_token
        else:
            # 新しいトークンを作成
            oauth_token = GoogleOAuthToken(
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
                scope=scope,
                google_user_id=google_user_id,
                google_email=google_email,
            )
            return create_oauth_token(oauth_token, s)


def replace_oauth_token(
    user_id: int,
    access_token: str,
    refresh_token: Optional[str] = None,
    expires_at: Optional[float] = None,
    scope: Optional[str] = None,
    google_user_id: Optional[str] = None,
    google_email: Optional[str] = None,
    session: Optional[Session] = None,
) -> GoogleOAuthToken:
    """OAuth トークンを置換（既存を削除して新規作成）"""
    with session or get_session() as s:
        # 既存のトークンを削除
        delete_all_active_tokens_by_user_id(user_id, s)

        # 新しいトークンを作成
        oauth_token = GoogleOAuthToken(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            scope=scope,
            google_user_id=google_user_id,
            google_email=google_email,
        )
        return create_oauth_token(oauth_token, s)
