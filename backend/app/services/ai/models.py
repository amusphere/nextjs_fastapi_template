from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GenericActionParameters(BaseModel):
    user_id: int | None = None
    event_id: str | None = None
    summary: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    description: str | None = None
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class NextAction(BaseModel):
    """次に実行すべきアクション"""

    action_type: str  # 動的にスポークから読み込まれるアクションタイプ
    parameters: GenericActionParameters
    priority: int = Field(default=1, ge=1)  # 1が最高優先度
    description: str  # アクションの説明


class OperatorResponse(BaseModel):
    """オペレーターからの応答"""

    actions: List[NextAction]
    analysis: str  # プロンプト解析結果の説明
    confidence: float = Field(ge=0.0, le=1.0)  # 判断の信頼度 (0.0-1.0)


class SpokeResponse(BaseModel):
    """スポークからの応答"""

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
