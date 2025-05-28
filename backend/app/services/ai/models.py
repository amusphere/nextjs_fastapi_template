from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class NextAction(BaseModel):
    """次に実行すべきアクション"""

    action_type: str  # 動的にスポークから読み込まれるアクションタイプ
    parameters: Dict[str, Any]
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
