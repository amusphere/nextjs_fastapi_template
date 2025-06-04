import sys
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

import pytest
from app.database import get_session
from app.utils.auth.email_password import create_access_token, create_sub
from main import app

# Add the parent directory to the Python path so we can import from main
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import all fixtures from the fixtures directory
from tests.fixtures.database import *  # noqa: F401, F403
from tests.fixtures.users import *  # noqa: F401, F403


@pytest.fixture
def test_client(test_session, test_engine):
    """テスト用のFastAPIクライアント"""
    import os

    from fastapi.testclient import TestClient

    def get_test_session():
        yield test_session

    # 環境変数を一時的にテスト用SQLiteに変更
    original_db_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"

    # 依存性をオーバーライド
    app.dependency_overrides[get_session] = get_test_session

    # Sessionクラス自体をパッチして、常に同じテスト用sessionを返すようにする
    class MockSession:
        def __init__(self, *args, **kwargs):
            pass

        def __getattr__(self, name):
            # test_sessionの属性やメソッドを転送
            return getattr(test_session, name)

        def close(self):
            # テスト中はセッションを閉じない
            pass

        def __enter__(self):
            return test_session

        def __exit__(self, *args):
            pass

    def mock_session_new(*args, **kwargs):
        return MockSession()

    # get_engine関数をパッチしてテスト用エンジンを返すようにする
    with patch("app.database.get_engine", return_value=test_engine):
        with patch(
            "app.utils.auth.email_password.get_engine", return_value=test_engine
        ):
            with patch("app.utils.auth.clerk.get_engine", return_value=test_engine):
                # Sessionの作成自体をパッチしてテスト用sessionを返すようにする
                with patch(
                    "app.utils.auth.email_password.Session",
                    side_effect=mock_session_new,
                ):
                    with patch(
                        "app.utils.auth.clerk.Session", side_effect=mock_session_new
                    ):
                        with TestClient(app) as client:
                            yield client

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
