import os
from typing import Optional

import openai
from app.models.chat import ChatPromptRequest, ChatPromptResponse

# グローバルクライアントインスタンス
_client: Optional[openai.OpenAI] = None


def _get_openai_client() -> openai.OpenAI:
    """遅延初期化でOpenAIクライアントを取得"""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("OPENAI_API_KEY environment variable is not set")
        _client = openai.OpenAI(api_key=api_key)
    return _client


async def send_prompt_to_llm(request: ChatPromptRequest) -> ChatPromptResponse:
    """
    LLMにプロンプトを送信して応答を取得する
    """
    try:
        client = _get_openai_client()

        # メッセージ履歴を構築
        messages = []

        # 既存のメッセージ履歴を追加
        for msg in request.messages:
            messages.append({"role": msg.role, "content": msg.content})

        # 新しいユーザープロンプトを追加
        messages.append({"role": "user", "content": request.prompt})

        # OpenAI APIを呼び出し
        response = client.chat.completions.create(
            model=request.model,
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )

        # レスポンスを構築
        return ChatPromptResponse(
            response=response.choices[0].message.content,
            model=response.model,
            tokens_used=response.usage.total_tokens if response.usage else None,
        )

    except Exception as e:
        raise Exception(f"Failed to send prompt to LLM: {str(e)}")
