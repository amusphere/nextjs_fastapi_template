"""ユーザーテーブル関連のfixture"""

import pytest
from app.schema import User

from .test_data import TestConstants, TestUserFactory


@pytest.fixture
def test_user(test_session):
    """基本的なテスト用ユーザーを作成するfixture"""
    user_data = TestUserFactory.create_user_data(
        email=TestConstants.DEFAULT_EMAIL, name="Test User"
    )
    user = User(**user_data)
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user


@pytest.fixture
def authenticated_user(test_session):
    """認証済みユーザーを作成するfixture（JWT トークン用）"""
    user_data = TestUserFactory.create_user_data(
        email=TestConstants.AUTHENTICATED_EMAIL, name="Authenticated User"
    )
    user = User(**user_data)
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user


@pytest.fixture
def clerk_user(test_session):
    """Clerk認証用のテストユーザー"""
    user_data = TestUserFactory.create_user_data(
        email="clerk@example.com", name="Clerk User", clerk_sub="clerk_test_sub_123"
    )
    user = User(**user_data)
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user
