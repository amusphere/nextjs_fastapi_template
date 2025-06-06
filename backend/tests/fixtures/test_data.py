"""Test data constants and factories."""

from datetime import datetime
from uuid import uuid4

from passlib.context import CryptContext

# パスワードハッシュ化用の設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# テスト用のデフォルトパスワード
DEFAULT_TEST_PASSWORD = "test_password_123"
DEFAULT_TEST_PASSWORD_HASH = pwd_context.hash(DEFAULT_TEST_PASSWORD)


class TestUserFactory:
    """テストユーザー作成用のファクトリークラス"""

    @staticmethod
    def create_user_data(
        email: str = "test@example.com",
        name: str = "Test User",
        password: str = DEFAULT_TEST_PASSWORD,
        clerk_sub: str | None = None,
    ) -> dict:
        """ユーザーデータの辞書を作成"""
        return {
            "uuid": uuid4(),
            "email": email,
            "password": pwd_context.hash(password),
            "name": name,
            "created_at": datetime.now().timestamp(),
            "clerk_sub": clerk_sub,
        }


class TestConstants:
    """テスト用定数"""

    # API エンドポイントのベースURL
    API_BASE = "/api"
    USERS_BASE = f"{API_BASE}/users"
    AUTH_BASE = f"{API_BASE}/auth"
    CHAT_BASE = f"{API_BASE}/chat"
    HEALTH_BASE = f"{API_BASE}/health"

    # テスト用メールアドレス
    DEFAULT_EMAIL = "test@example.com"
    AUTHENTICATED_EMAIL = "authenticated@example.com"
    ADMIN_EMAIL = "admin@example.com"
