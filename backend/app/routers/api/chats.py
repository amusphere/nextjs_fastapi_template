from app.models.chat import ChatPromptRequest, ChatPromptResponse
from app.schema import User
from app.services.auth import auth_user
from app.services.llm import send_prompt_to_llm
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/chats")


@router.post("/prompt", response_model=ChatPromptResponse)
async def send_prompt_endpoint(
    request: ChatPromptRequest,
    _: User = Depends(auth_user),
):
    """
    LLMにプロンプトを送信して応答を取得する

    - **prompt**: LLMに送信するプロンプト文字列
    - **messages**: 会話履歴（オプション）
    - **model**: 使用するモデル（デフォルト: gpt-4.1）
    - **max_tokens**: 最大トークン数（デフォルト: 1000）
    - **temperature**: 応答のランダム性（デフォルト: 0.7）
    """
    try:
        response = await send_prompt_to_llm(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process prompt: {str(e)}",
        )
