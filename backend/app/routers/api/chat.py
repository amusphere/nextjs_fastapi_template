from app.database import get_session
from app.models.chat import (
    ChatHistoryResponseModel,
    ChatMessageModel,
    ChatRequestModel,
    ChatResponseModel,
)
from app.repositories.chat_history import clear_messages, get_last_messages
from app.schema import User
from app.services.auth import auth_user
from app.services.chat import send_chat
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

router = APIRouter(prefix="/chat")


@router.post("", response_model=ChatResponseModel)
async def chat(
    data: ChatRequestModel,
    user: User = Depends(auth_user),
    session: Session = Depends(get_session),
    limit: int | None = Query(None, description="履歴に含める最大件数"),
):
    response = await send_chat(data.prompt, user=user, session=session, limit=limit)
    return {"response": response}


@router.get("/history", response_model=ChatHistoryResponseModel)
def get_history(
    limit: int = Query(30, ge=1, le=200, description="取得する履歴件数"),
    user: User = Depends(auth_user),
    session: Session = Depends(get_session),
):
    rows = get_last_messages(session, user, limit)
    messages: list[ChatMessageModel] = [
        ChatMessageModel(
            id=m.id, role=m.role, content=m.content, created_at=m.created_at
        )
        for m in rows
    ]
    return {"total": len(messages), "messages": messages}


@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
def clear_history(
    user: User = Depends(auth_user), session: Session = Depends(get_session)
):
    clear_messages(session, user)
    return
