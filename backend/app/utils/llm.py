import os

import openai

DEFAULT_MODEL = "gpt-5-nano"


def get_client() -> openai.OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not configured")
    return openai.OpenAI(api_key=api_key)


def generate_response(
    messages: list[dict[str, str]],
    model: str = DEFAULT_MODEL,
) -> str:
    """Responses API でのテキスト生成。

    - 引数の messages は {role, content} のリスト（従来の Chat Completions と同形）
    - Responses API の input にマッピングして呼び出します
    """
    client = get_client()

    # Chat Completions 互換の messages を Responses API の input 形式へ変換
    input_items = [
        {"role": m.get("role", "user"), "content": m.get("content", "")}
        for m in messages
    ]

    resp = client.responses.create(
        model=model,
        input=input_items,
    )

    # 可能なら output_text を優先的に使用
    text = getattr(resp, "output_text", None)
    if isinstance(text, str) and text.strip():
        return text.strip()

    # フォールバック（SDK 構造の差異に備える）
    try:
        outputs = getattr(resp, "output", []) or []
        if outputs:
            contents = getattr(outputs[0], "content", []) or []
            for c in contents:
                t = getattr(getattr(c, "text", None), "value", None)
                if t:
                    return t.strip()
    except Exception:
        pass

    # 最終フォールバック
    return ""
