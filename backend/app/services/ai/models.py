from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class NextAction(BaseModel):
    """次に実行すべきアクション"""

    model_config = ConfigDict(extra="forbid")

    spoke_name: str  # スポーク名
    action_type: str  # スポークのアクションタイプ
    parameters: Dict[str, Any] = Field(default_factory=dict)  # アクションのパラメータ
    priority: int = Field(default=1, ge=1)  # 1が最高優先度
    description: str  # アクションの説明


class OperatorResponse(BaseModel):
    """オペレーターからの応答"""

    model_config = ConfigDict(extra="forbid")

    actions: List[NextAction]
    analysis: str  # プロンプト解析結果の説明
    confidence: float = Field(ge=0.0, le=1.0)  # 判断の信頼度 (0.0-1.0)


class SpokeResponse(BaseModel):
    """スポークからの応答"""

    model_config = ConfigDict(extra="forbid")

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
