from pydantic import BaseModel


class AIRequestModel(BaseModel):
    """AIリクエストモデル"""

    prompt: str
    max_tokens: int | None = 1000
    temperature: float | None = 0.7


class AIResponseModel(BaseModel):
    """AIレスポンスモデル"""

    success: bool
    operator_response: dict | None = None
    execution_results: list = []
    summary: dict
    error: str | None = None
