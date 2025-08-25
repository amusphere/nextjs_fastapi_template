"""データベースセッション管理のユーティリティ関数"""

from collections.abc import Generator
from contextlib import contextmanager

from app.database import get_session
from sqlmodel import Session


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    データベースセッションを安全に管理するコンテキストマネージャー

    テスト環境では共有セッションを使用し、本番環境では新しいセッションを作成します。

    Yields:
        Session: データベースセッション

    Example:
        ```python
        with get_db_session() as session:
            user = session.get(User, user_id)
        ```
    """
    session_gen = get_session()
    session = next(session_gen)
    try:
        yield session
    finally:
        try:
            # ジェネレーターを適切にクローズ
            next(session_gen, None)
        except (StopIteration, GeneratorExit):
            # 正常なジェネレーターの終了
            pass
        except Exception:
            # その他の例外は無視（セッションクローズの失敗は処理を止めない）
            pass
