import json
import os

import openai
from app.services.ai.models import (
    ParameterPredictionRequest,
    ParameterPredictionResponse,
)

# OpenAI APIのモデル名
model = "gpt-4.1"

# OpenAI APIクライアントの初期化
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def predict_parameters(
    request: ParameterPredictionRequest,
) -> ParameterPredictionResponse:
    """
    LLMにパラメータの推測を依頼する
    """
    try:
        # パラメータスキーマを作成
        parameters_schema = request.action_definition.get("parameters", {})

        # プロンプトを構築
        prompt = f"""
あなたは与えられた情報を基に、アクションに必要なパラメータを推測するAIアシスタントです。

以下の情報を基に、アクションに必要なパラメータを推測してください：

**スポーク名**: {request.spoke_name}
**アクションタイプ**: {request.action_type}
**ユーザーの説明**: {request.description}
**現在のパラメータ**: {request.parameters}

**アクション定義**:
{json.dumps(request.action_definition, indent=2, ensure_ascii=False)}

**必要なパラメータスキーマ**:
{json.dumps(parameters_schema, indent=2, ensure_ascii=False)}

以下のJSONフォーマットで応答してください：
{{
    "predicted_parameters": {{
        // 推測したパラメータの値をここに記載
        // 必須パラメータは必ず含める
        // オプションパラメータは適切と思われる場合のみ含める
    }},
    "reasoning": "パラメータを推測した理由を詳しく説明",
    "confidence": 0.85 // 推測の信頼度（0.0-1.0）
}}

注意事項：
- 必須パラメータ（required: true）は必ず推測して含めてください
- 日時フォーマットが指定されている場合は、ISO8601形式（例：2024-01-01T10:00:00Z）で出力してください
- user_idなどのIDパラメータは、具体的な値が分からない場合は null にしてください
- 不明なパラメータは推測せず、null または省略してください
"""

        # OpenAI APIを呼び出し
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "あなたは正確で有用なパラメータ推測を行うAIアシスタントです。",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=1000,
            temperature=0.3,  # より確定的な応答のために低めに設定
        )

        # JSONレスポンスをパース
        response_content = response.choices[0].message.content

        try:
            parsed_response = json.loads(response_content)

            return ParameterPredictionResponse(
                predicted_parameters=parsed_response.get("predicted_parameters", {}),
                reasoning=parsed_response.get("reasoning", ""),
                confidence=parsed_response.get("confidence", 0.5),
            )
        except json.JSONDecodeError:
            # JSONパースに失敗した場合は、空のパラメータで返す
            return ParameterPredictionResponse(
                predicted_parameters={},
                reasoning=f"LLMレスポンスのJSONパースに失敗: {response_content}",
                confidence=0.0,
            )

    except Exception as e:
        raise Exception(f"Failed to predict parameters: {str(e)}")
