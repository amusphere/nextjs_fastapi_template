import os
import sys
from datetime import timedelta
from pathlib import Path

import pytest
from app.database import get_session
from app.utils.auth.email_password import create_access_token, create_sub
from app.utils.test_database import clear_test_config, set_test_engine, set_test_session
from fastapi.testclient import TestClient
from main import app

# Add the parent directory to the Python path so we can import from main
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import all fixtures from the fixtures directory
from tests.fixtures.database import *  # noqa: F403
from tests.fixtures.users import *  # noqa: F403


@pytest.fixture
def test_client(test_session, test_engine):
    """テスト用のFastAPIクライアント"""

    def get_test_session():
        yield test_session

    # 環境変数を一時的にテスト用SQLiteに変更
    original_db_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"

    # テスト用エンジンとセッションを設定
    set_test_engine(test_engine)
    set_test_session(test_session)

    # 依存性をオーバーライド
    app.dependency_overrides[get_session] = get_test_session

    try:
        with TestClient(app) as client:
            yield client
    finally:
        # クリーンアップ
        clear_test_config()

        # 環境変数を元に戻す
        if original_db_url is not None:
            os.environ["DATABASE_URL"] = original_db_url
        elif "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]

        app.dependency_overrides.clear()


@pytest.fixture
def authenticated_client(test_client, authenticated_user):
    """認証済みユーザーのJWTトークンを持つテストクライアントを作成するfixture"""
    # JWTトークンを作成
    token_data = create_sub(authenticated_user)
    access_token = create_access_token(
        data=token_data, expires_delta=timedelta(minutes=30)
    )

    # デフォルトのヘッダーに認証トークンを設定
    test_client.headers = {
        **getattr(test_client, "headers", {}),
        "Authorization": f"Bearer {access_token}",
    }

    return test_client
