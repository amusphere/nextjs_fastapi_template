"""
スポーク共通インターフェース
"""

from abc import ABC
from typing import Any, Dict, Optional

from app.services.ai.models import SpokeResponse
from sqlmodel import Session


class BaseSpoke(ABC):
    """スポーク基底クラス"""

    def __init__(self, session: Optional[Session] = None):
        self.session = session

    async def execute_action(
        self, action_type: str, parameters: Dict[str, Any]
    ) -> SpokeResponse:
        """アクションを実行する"""
        try:
            # アクション名をメソッド名に変換 (例: get_calendar_events -> action_get_calendar_events)
            method_name = f"action_{action_type}"


            # メソッドが存在するかチェック
            if not hasattr(self, method_name):
                return SpokeResponse(
                    success=False, error=f"Unsupported action type: {action_type}"
                )

            return await getattr(self, method_name)(parameters)

        except Exception as e:
            return SpokeResponse(
                success=False, error=f"Error executing action {action_type}: {str(e)}"
            )

    @classmethod
    def get_supported_actions(cls) -> list[str]:
        """このスポークがサポートするアクションタイプのリストを返す"""
        # action_で始まるメソッドを自動的に検出
        actions = []
        for attr_name in dir(cls):
            if attr_name.startswith("action_") and callable(getattr(cls, attr_name)):
                # action_プレフィックスを除去してアクション名を取得
                action_name = attr_name[7:]  # "action_"の長さは7文字
                actions.append(action_name)
        return sorted(actions)  # ソートして一貫性を保つ
