from typing import List, Optional

from sqlmodel import Session

from .exceptions import ActionExecutionError
from .logger import AIAssistantLogger
from .models import (
    NextAction,
    SpokeResponse,
)
from .spokes.spoke_manager import SpokeManager


class ActionExecutor:
    """アクションを実際に実行するエグゼキューター"""

    def __init__(self, session: Optional[Session] = None):
        self.session = session
        self.spoke_manager = SpokeManager(session)
        self.logger = AIAssistantLogger("action_executor")

    async def execute_action(self, action: NextAction) -> SpokeResponse:
        """個別のアクションを実行"""
        # ログ記録
        self.logger.log_action_execution(next_action=action)

        try:
            # 動的スポークマネージャーを使用してアクションを実行
            result = await self.spoke_manager.execute_action(action)
            return result
        except Exception as e:
            error = ActionExecutionError(f"Execution error: {str(e)}")
            self.logger.log_error(
                error,
                {
                    "spoke_name": action.spoke_name,
                    "action_type": action.action_type,
                    "parameters": action.parameters,
                },
            )
            return SpokeResponse(success=False, error=str(error))

    async def execute_actions(self, actions: List[NextAction]) -> List[SpokeResponse]:
        """複数のアクションを優先度順に実行"""
        # 優先度でソート（数値が小さいほど高優先度）
        sorted_actions = sorted(actions, key=lambda x: x.priority)

        results = []
        for action in sorted_actions:
            result = await self.execute_action(action)
            results.append(result)

            # 重要なエラーが発生した場合は実行を停止
            if not result.success and action.priority == 1:
                break

        return results
