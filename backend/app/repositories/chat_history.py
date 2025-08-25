from app.schema import ChatMessage, User
from sqlmodel import Session, select


def add_message(session: Session, user: User, role: str, content: str) -> ChatMessage:
    """チャットメッセージを保存します。"""
    message = ChatMessage(user_id=user.id, role=role, content=content)
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


def get_last_messages(session: Session, user: User, limit: int) -> list[ChatMessage]:
    """直近のメッセージを新しい順で limit 件取得し、古い順に並べ替えて返します。"""
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.user_id == user.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    rows = session.exec(stmt).all()
    return list(reversed(rows))


def clear_messages(session: Session, user: User) -> int:
    """ユーザの全メッセージを削除して件数を返す。"""
    stmt = select(ChatMessage).where(ChatMessage.user_id == user.id)
    rows = session.exec(stmt).all()
    for m in rows:
        session.delete(m)
    session.commit()
    return len(rows)
