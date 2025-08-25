import os

from app.repositories.chat_history import (
    add_message,
    get_last_messages,
)
from app.schema import User
from app.utils.llm import generate_response
from sqlmodel import Session

DEFAULT_HISTORY_LIMIT = int(os.getenv("CHAT_HISTORY_LIMIT", "30"))


async def send_chat(
    prompt: str, user: User, session: Session, limit: int | None = None
) -> str:
    """履歴を含めて LLM に投げ、ユーザ/アシスタント両方を保存。"""
    ctx_limit = limit or DEFAULT_HISTORY_LIMIT

    # 直近メッセージを取得（古い→新しい順）
    history = get_last_messages(session, user, ctx_limit)

    messages = [{"role": m.role, "content": m.content} for m in history] + [
        {"role": "user", "content": prompt}
    ]

    try:
        response_text = generate_response(messages=messages)
    except Exception as e:
        print(f"Error during response generation: {e}")
        return "An error occurred while processing your request."

    # 保存（ユーザの入力とアシスタントの応答）
    add_message(session, user, role="user", content=prompt)
    add_message(session, user, role="assistant", content=response_text)

    return response_text
