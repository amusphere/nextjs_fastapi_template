"""データベース関連のfixture"""

import pytest
from sqlmodel import Session, SQLModel, create_engine

# テーブル定義をインポートしてメタデータに登録
from app.schema import User, PasswordResetToken  # noqa: F401


# Test database engine (using SQLite in memory for tests)
@pytest.fixture(scope="session")
def test_engine():
    """テスト用のSQLiteインメモリデータベースエンジン"""
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,  # テスト時はログを抑制
        connect_args={"check_same_thread": False},  # マルチスレッド対応
    )

    # SQLModelメタデータからテーブルを作成
    SQLModel.metadata.create_all(engine)

    return engine


@pytest.fixture
def test_session(test_engine):
    """テスト用のデータベースセッション

    各テストでクリーンな状態を保持するため、ネストしたトランザクションを使用
    """
    connection = test_engine.connect()

    # 外側のトランザクションを開始
    transaction = connection.begin()

    # セッションを作成
    session = Session(bind=connection)

    try:
        yield session
    finally:
        session.close()
        # ロールバックでデータをクリーンアップ
        transaction.rollback()
        connection.close()
