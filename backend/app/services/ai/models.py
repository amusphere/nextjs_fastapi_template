import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class NextAction(BaseModel):
    """次に実行すべきアクション"""

    model_config = ConfigDict(extra="forbid")

    spoke_name: str  # スポーク名
    action_type: str  # スポークのアクションタイプ
    parameters: str = Field(default="{}")  # アクションのパラメータ（JSON文字列）
    priority: int = Field(default=1, ge=1)  # 1が最高優先度
    description: str  # アクションの説明

    @field_validator("parameters", mode="before")
    @classmethod
    def validate_parameters(cls, v):
        if isinstance(v, dict):
            return json.dumps(v)
        return v

    def get_parameters_dict(self) -> Dict[str, Any]:
        """パラメータを辞書として取得"""
        try:
            return json.loads(self.parameters)
        except json.JSONDecodeError:
            return {}


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
