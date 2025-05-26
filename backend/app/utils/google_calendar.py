import base64
import os
from datetime import datetime
from typing import Optional

from cryptography.fernet import Fernet
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlmodel import Session

from ..repositories import google_oauth_token as oauth_repo
from ..schema import GoogleOAuthToken

# 環境変数から取得
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")


class GoogleCalendarService:
    def __init__(self, encryption_key: str, session: Session | None = None):
        # Convert hex string to bytes, then base64 encode for Fernet
        if len(encryption_key) == 64:  # Hex string (32 bytes * 2)
            key_bytes = bytes.fromhex(encryption_key)
            fernet_key = base64.urlsafe_b64encode(key_bytes)
            self.fernet = Fernet(fernet_key)
        else:
            # Assume it's already a proper Fernet key
            self.fernet = Fernet(encryption_key.encode())
        self.session = session

    def encrypt_token(self, token: str) -> str:
        """トークンを暗号化"""
        return self.fernet.encrypt(token.encode()).decode()

    def decrypt_token(self, encrypted_token: str) -> str:
        """トークンを復号化"""
        return self.fernet.decrypt(encrypted_token.encode()).decode()

    def store_oauth_tokens(
        self,
        user_id: int,
        credentials: Credentials,
        google_user_id: str = None,
        google_email: str = None,
    ) -> GoogleOAuthToken:
        """OAuth認証情報をデータベースに保存（アップサート方式）"""
        expires_at = None
        if credentials.expiry:
            expires_at = credentials.expiry.timestamp()

        return oauth_repo.upsert_oauth_token(
            user_id=user_id,
            access_token=self.encrypt_token(credentials.token),
            refresh_token=(
                self.encrypt_token(credentials.refresh_token)
                if credentials.refresh_token
                else None
            ),
            expires_at=expires_at,
            scope=" ".join(credentials.scopes) if credentials.scopes else None,
            google_user_id=google_user_id,
            google_email=google_email,
            session=self.session,
        )

    def get_credentials(self, user_id: int) -> Optional[Credentials]:
        """ユーザーのGoogle認証情報を取得"""
        oauth_token = oauth_repo.find_active_token_by_user_id(
            user_id=user_id, session=self.session
        )

        if not oauth_token:
            return None

        # 復号化してCredentialsオブジェクトを作成
        access_token = self.decrypt_token(oauth_token.access_token)
        refresh_token = None
        if oauth_token.refresh_token:
            refresh_token = self.decrypt_token(oauth_token.refresh_token)

        credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            scopes=oauth_token.scope.split() if oauth_token.scope else None,
        )

        # トークンの有効期限をチェック
        if oauth_token.expires_at:
            credentials.expiry = datetime.fromtimestamp(oauth_token.expires_at)

        # トークンが期限切れの場合、リフレッシュを試行
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            # 更新されたトークンを保存
            self.update_tokens(oauth_token.id, credentials)

        return credentials

    def update_tokens(self, token_id: int, credentials: Credentials):
        """トークンを更新"""
        expires_at = credentials.expiry.timestamp() if credentials.expiry else None

        oauth_repo.update_token_data(
            token_id=token_id,
            access_token=self.encrypt_token(credentials.token),
            refresh_token=(
                self.encrypt_token(credentials.refresh_token)
                if credentials.refresh_token
                else None
            ),
            expires_at=expires_at,
            session=self.session,
        )

    def get_calendar_service(self, user_id: int):
        """Google Calendar APIサービスを取得"""
        credentials = self.get_credentials(user_id)
        if not credentials:
            raise ValueError("Google認証情報が見つかりません")

        return build("calendar", "v3", credentials=credentials)

    def revoke_access(self, user_id: int):
        """ユーザーのアクセスを取り消し（レコードを削除）"""
        return oauth_repo.delete_all_active_tokens_by_user_id(
            user_id=user_id, session=self.session
        )
