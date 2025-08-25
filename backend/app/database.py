"""Database configuration and session management."""

from collections.abc import Generator
from os import getenv

from app.utils.test_database import get_test_engine, get_test_session
from dotenv import load_dotenv
from sqlmodel import Session, create_engine

load_dotenv()


def get_database_url() -> str:
    """
    Get the database URL from environment variables.

    Returns:
        str: The database connection URL

    Raises:
        ValueError: If DATABASE_URL environment variable is not set
    """
    database_url = getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    return database_url


def get_engine():
    """
    Get the SQLModel engine.

    In test environments, returns the test engine if available.
    Otherwise, creates a new engine using the database URL.

    Returns:
        Engine: The SQLModel engine instance
    """
    # テスト環境でテスト用エンジンが設定されている場合はそれを返す
    test_engine = get_test_engine()
    if test_engine is not None:
        return test_engine

    return create_engine(get_database_url(), future=True)


def get_session() -> Generator[Session, None, None]:
    """
    Get a SQLModel session.

    In test environments, yields the shared test session if available.
    Otherwise, creates a new session using the engine.

    Yields:
        Session: The SQLModel session instance
    """
    # テスト環境でテスト用セッションが設定されている場合はそれを返す
    test_session = get_test_session()
    if test_session is not None:
        yield test_session
        return

    engine = get_engine()
    with Session(engine) as session:
        yield session
