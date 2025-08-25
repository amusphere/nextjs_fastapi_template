"""
Test environment database configuration.

This module provides functionality to override database connections
during testing to use in-memory SQLite databases instead of production
databases. This ensures test isolation and prevents test data from
affecting production systems.
"""

import sys

from sqlalchemy import Engine
from sqlmodel import Session

# テスト用のエンジンとセッションを保存するグローバル変数
_test_engine: Engine | None = None
_test_session: Session | None = None


def is_testing() -> bool:
    """
    Check if the current environment is a testing environment.

    Returns:
        bool: True if pytest is running, False otherwise
    """
    return "pytest" in sys.modules


def set_test_engine(engine: Engine) -> None:
    """
    Set the test engine to be used during testing.

    Args:
        engine: The SQLAlchemy engine instance for testing
    """
    global _test_engine
    _test_engine = engine


def set_test_session(session: Session) -> None:
    """
    Set the test session to be used during testing.

    Args:
        session: The SQLModel session instance for testing
    """
    global _test_session
    _test_session = session


def clear_test_config() -> None:
    """
    Clear test configuration.

    This should be called after tests complete to clean up
    the global test state.
    """
    global _test_engine, _test_session
    _test_engine = None
    _test_session = None


def get_test_engine() -> Engine | None:
    """
    Get the test engine if in testing environment.

    Returns:
        Optional[Engine]: The test engine if available and in test mode, None otherwise
    """
    return _test_engine if is_testing() else None


def get_test_session() -> Session | None:
    """
    Get the test session if in testing environment.

    Returns:
        Optional[Session]: The test session if available and in test mode, None otherwise
    """
    return _test_session if is_testing() else None
