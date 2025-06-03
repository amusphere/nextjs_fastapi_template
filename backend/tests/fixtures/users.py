"""ユーザーテーブル関連のfixture"""

from datetime import datetime
from uuid import uuid4

import pytest
from app.schema import User


@pytest.fixture
def test_user(test_session):
    """基本的なテスト用ユーザーを作成するfixture"""
    user = User(
        uuid=uuid4(),
        email="test@example.com",
        password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiSyppHMWjuC",  # "password"をハッシュ化
        name="Test User",
        created_at=datetime.now().timestamp(),
        clerk_sub=None,
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user


@pytest.fixture
def authenticated_user(test_session):
    """認証済みユーザーを作成するfixture（JWT トークン用）"""
    user = User(
        uuid=uuid4(),
        email="authenticated@example.com",
        password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiSyppHMWjuC",
        name="Authenticated User",
        created_at=datetime.now().timestamp(),
        clerk_sub=None,
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user
