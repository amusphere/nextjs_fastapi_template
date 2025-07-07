"""
スポークマネージャー - スポークのインスタンス化と実行を管理
"""

import os
from typing import Dict, Optional

from app.schema import User
from app.services.ai.logger import AIAssistantLogger
from app.services.ai.models import NextAction, SpokeResponse
from app.services.ai.spokes.spoke_interface import BaseSpoke
from app.services.ai.spokes.spoke_system import DynamicSpokeLoader
from sqlmodel import Session


class SpokeManager:
    """スポークマネージャー - スポークのインスタンス化と実行を管理"""

    def __init__(self, session: Optional[Session] = None):
        self.session = session
        self.logger = AIAssistantLogger("spoke_manager")

        # スポークを読み込み
        spokes_dir = os.path.dirname(__file__)  # spoke_manager.pyと同じディレクトリ
        loader = DynamicSpokeLoader(spokes_dir)
        self.registry = loader.load_all_spokes()

        # スポークインスタンスをキャッシュ
        self._spoke_instances: Dict[str, BaseSpoke] = {}

        # アクションタイプからスポーク名へのマッピング
        self._action_to_spoke = self.registry.get_action_to_spoke_mapping()

    def get_spoke_instance(
        self,
        spoke_name: str,
        current_user: User,
    ) -> Optional[BaseSpoke]:
        """スポークインスタンスを取得（キャッシュ付き）"""
        cache_key = f"{spoke_name}_{current_user.id}"
        if cache_key in self._spoke_instances:
            return self._spoke_instances[cache_key]

        spoke_class = self.registry.get_spoke_class(spoke_name, current_user)
        if spoke_class is None:
            self.logger.error(f"Spoke class not found for: {spoke_name}")
            return None

        try:
            instance = spoke_class(self.session, current_user)
            self._spoke_instances[cache_key] = instance
            return instance
        except Exception as e:
            self.logger.error(f"Failed to instantiate spoke {spoke_name}: {str(e)}")
            return None

    async def execute_action(
        self,
        action: NextAction,
        current_user: User,
    ) -> SpokeResponse:
        """アクションを実行"""
        spoke_name = self._action_to_spoke.get(action.action_type)
        if spoke_name is None:
            return SpokeResponse(
                success=False,
                error=f"No spoke found for action type: {action.action_type}",
            )

        action_definition = self.registry.get_action_definition(
            spoke_name, action.action_type
        )
        if action_definition is None:
            return SpokeResponse(
                success=False,
                error=f"Action definition not found for {spoke_name}.{action.action_type}",
            )

        spoke_instance = self.get_spoke_instance(spoke_name, current_user)
        if spoke_instance is None:
            return SpokeResponse(
                success=False, error=f"Failed to get spoke instance for: {spoke_name}"
            )

        try:
            return await spoke_instance.execute_action(
                action=action,
                action_definition=action_definition.__dict__,
            )
        except Exception as e:
            self.logger.error(f"Error executing action {action.action_type}: {str(e)}")
            return SpokeResponse(success=False, error=f"Execution error: {str(e)}")
