from app.models.ai_assistant import AIRequestModel, AIResponseModel
from app.schema import User
from app.services.auth import auth_user
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ...database import get_session
from ...services.ai.orchestrator import process_ai_request

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


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
