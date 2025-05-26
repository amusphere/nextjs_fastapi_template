import os

import openai
from app.models.chat import ChatPromptRequest, ChatPromptResponse

# OpenAI APIのモデル名
model = "gpt-4.1"

# OpenAI APIクライアントの初期化
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def send_prompt_to_llm(request: ChatPromptRequest) -> ChatPromptResponse:
    """
    LLMにプロンプトを送信して応答を取得する
    """
    try:
        # メッセージ履歴を構築
        messages = []

        # 新しいユーザープロンプトを追加
        messages.append({"role": "user", "content": request.prompt})

        # OpenAI APIを呼び出し
        response = client.chat.completions.create(
            model=model,
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
