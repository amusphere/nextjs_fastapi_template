"""データベース関連のfixture"""

import pytest
from sqlmodel import Session, SQLModel, create_engine


# Test database engine (using SQLite in memory for tests)
@pytest.fixture(scope="session")
def test_engine():
    """テスト用のSQLiteインメモリデータベースエンジン"""
    engine = create_engine(
        "sqlite:///:memory:",
        echo=True,
        connect_args={"check_same_thread": False},  # マルチスレッド対応
    )

    # SQLModelメタデータからテーブルを作成
    SQLModel.metadata.create_all(engine)

    return engine


@pytest.fixture
def test_session(test_engine):
    """テスト用のデータベースセッション"""
    with Session(test_engine) as session:
        yield session
