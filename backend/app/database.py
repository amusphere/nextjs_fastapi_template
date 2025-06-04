from os import getenv

from dotenv import load_dotenv
from sqlmodel import Session, create_engine

load_dotenv()

# テスト用のエンジンとセッションを保存するグローバル変数
_test_engine = None
_test_session = None


def set_test_engine(engine):
    """テスト用エンジンを設定する（テスト時のみ使用）"""
    global _test_engine
    _test_engine = engine


def set_test_session(session):
    """テスト用セッションを設定する（テスト時のみ使用）"""
    global _test_session
    _test_session = session


def clear_test_engine():
    """テスト用エンジンをクリアする（テスト終了時）"""
    global _test_engine, _test_session
    _test_engine = None
    _test_session = None


def is_testing():
    """テスト環境かどうかを判定"""
    import sys

    return "pytest" in sys.modules


def get_database_url():
    """Get the database URL from environment variables."""
    DATABASE_URL = getenv("DATABASE_URL")
    return DATABASE_URL


def get_engine():
    """Get the SQLModel engine."""
    # テスト環境でテスト用エンジンが設定されている場合はそれを返す
    global _test_engine
    testing = is_testing()
    has_test_engine = _test_engine is not None

    if testing and has_test_engine:
        return _test_engine

    return create_engine(get_database_url(), future=True)


def get_session():
    """Get a SQLModel session."""
    # テスト環境でテスト用セッションが設定されている場合はそれを返す
    global _test_session
    testing = is_testing()
    has_test_session = _test_session is not None

    if testing and has_test_session:
        yield _test_session
        return

    engine = get_engine()
    with Session(engine) as session:
        yield session
