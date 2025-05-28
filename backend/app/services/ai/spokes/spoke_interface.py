"""
スポーク共通インターフェース
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from sqlmodel import Session

from ..models import SpokeResponse


class BaseSpoke(ABC):
    """全てのスポークが実装すべき基底クラス"""

    def __init__(self, encryption_key: str, session: Optional[Session] = None):
        self.encryption_key = encryption_key
        self.session = session

    @abstractmethod
    async def execute_action(
        self, action_type: str, parameters: Dict[str, Any]
    ) -> SpokeResponse:
        """アクションを実行する

        Args:
            action_type: 実行するアクションタイプ
            parameters: アクションパラメータ

        Returns:
            SpokeResponse: 実行結果
        """
        pass

    @classmethod
    @abstractmethod
    def get_supported_actions(cls) -> list[str]:
        """このスポークがサポートするアクションタイプのリストを返す"""
        pass
