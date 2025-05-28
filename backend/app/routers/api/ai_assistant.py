from typing import Optional

from app.schema import User
from app.services.auth import auth_user
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

from ...database import get_session
from ...services.ai.orchestrator import process_ai_request

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


class AIRequestModel(BaseModel):
    """AIリクエストモデル"""

    prompt: str
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7


class AIResponseModel(BaseModel):
    """AIレスポンスモデル"""

    success: bool
    operator_response: Optional[dict] = None
    execution_results: list = []
    summary: dict
    error: Optional[str] = None


@router.post("/process", response_model=AIResponseModel)
async def process_ai_request_endpoint(
    request: AIRequestModel,
    session: Session = Depends(get_session),
    user: User = Depends(auth_user),
):
    """AIアシスタントにリクエストを送信して処理結果を取得"""
    try:
        # ユーザーIDをプロンプトに含める処理
        # プロンプトにuser_idを自動的に含めるように調整
        enhanced_prompt = f"[USER_ID: {user.id}] {request.prompt}"

        result = await process_ai_request(
            prompt=enhanced_prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            session=session,
        )

        return AIResponseModel(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process AI request: {str(e)}",
        )


@router.get("/actions")
async def get_available_actions():
    """利用可能なアクションタイプを取得"""
    from ...services.ai.models import ActionType

    actions = [
        {"action_type": action.value, "description": _get_action_description(action)}
        for action in ActionType
        if action != ActionType.UNKNOWN
    ]

    return {"available_actions": actions}


def _get_action_description(action_type) -> str:
    """アクションタイプの説明を取得"""
    descriptions = {
        "get_calendar_events": "指定期間のカレンダーイベントを取得します",
        "create_calendar_event": "新しいカレンダーイベントを作成します",
        "update_calendar_event": "既存のカレンダーイベントを更新します",
        "delete_calendar_event": "カレンダーイベントを削除します",
    }
    return descriptions.get(action_type.value, "説明なし")
