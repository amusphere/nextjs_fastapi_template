import sys
from datetime import timedelta
from pathlib import Path

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
def test_client(test_session):
    """テスト用のFastAPIクライアント"""
    from fastapi.testclient import TestClient

    def get_test_session():
        yield test_session

    app.dependency_overrides[get_session] = get_test_session

    with TestClient(app) as client:
        yield client

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
