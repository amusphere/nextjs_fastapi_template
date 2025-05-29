import json
import os

import openai

# OpenAI APIのモデル名
model = "gpt-4.1"

# OpenAI APIクライアントの初期化
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def predict_parameters(
    spoke_name: str,
    action_type: str,
    description: str,
    parameters: dict,
    action_definition: dict,
) -> dict:
    """
    LLMにパラメータの推測を依頼する
    """
    try:
        # パラメータスキーマを作成
        parameters_schema = action_definition.get("parameters", {})

        # プロンプトを構築
        prompt = f"""
あなたは与えられた情報を基に、アクションに必要なパラメータを推測するAIアシスタントです。

以下の情報を基に、アクションに必要なパラメータを推測してください：

**スポーク名**: {spoke_name}
**アクションタイプ**: {action_type}
**ユーザーの説明**: {description}
**現在のパラメータ**: {parameters}

**アクション定義**:
{json.dumps(action_definition, indent=2, ensure_ascii=False)}

**必要なパラメータスキーマ**:
{json.dumps(parameters_schema, indent=2, ensure_ascii=False)}

以下のJSONフォーマットで応答してください：
{{
    "predicted_parameters": {{
        // 推測したパラメータの値をここに記載
        // 必須パラメータは必ず含める
        // オプションパラメータは適切と思われる場合のみ含める
    }},
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
        parsed_response = json.loads(response_content)

        return parsed_response.get("predicted_parameters", {})

    except Exception as e:
        raise Exception(f"Failed to predict parameters: {str(e)}")
