import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlmodel import Session

from .exceptions import ActionExecutionError
from .logger import AIAssistantLogger
from .models import (
    NextAction,
    OperatorResponse,
    SpokeResponse,
)
from .spokes.spoke_system import DynamicSpokeManager


class ActionExecutor:
    """アクションを実際に実行するエグゼキューター"""

    def __init__(self, encryption_key: str, session: Optional[Session] = None):
        self.encryption_key = encryption_key
        self.session = session
        self.spoke_manager = DynamicSpokeManager(encryption_key, session)
        self.logger = AIAssistantLogger("action_executor")

    async def execute_action(self, action: NextAction) -> SpokeResponse:
        """個別のアクションを実行"""
        start_time = time.time()

        try:
            # 動的スポークマネージャーを使用してアクションを実行
            result = await self.spoke_manager.execute_action(
                action.action_type.value, action.parameters
            )

            # ログ記録
            duration = time.time() - start_time
            self.logger.log_action_execution(
                action_type=action.action_type.value,
                user_id=action.parameters.get("user_id", 0),
                success=result.success,
                duration=duration,
                error=result.error if not result.success else None,
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            error = ActionExecutionError(f"Execution error: {str(e)}")
            self.logger.log_error(
                error,
                {
                    "action_type": action.action_type.value,
                    "user_id": action.parameters.get("user_id", 0),
                    "duration": duration,
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

    def _validate_required_params(
        self, parameters: Dict[str, Any], required_fields: List[str]
    ) -> Optional[str]:
        """必須パラメータを検証"""
        missing_fields = [
            field for field in required_fields if not parameters.get(field)
        ]
        if missing_fields:
            return f"Required fields missing: {', '.join(missing_fields)}"
        return None

    def _parse_datetime(self, datetime_str: str) -> datetime:
        """日時文字列をdatetimeオブジェクトに変換"""
        return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))


async def execute_operator_response(
    operator_response: OperatorResponse,
    encryption_key: Optional[str] = None,
    session: Optional[Session] = None,
) -> List[SpokeResponse]:
    """オペレーターレスポンスに基づいてアクションを実行

    Args:
        operator_response: オペレーターからの応答
        encryption_key: 暗号化キー
        session: データベースセッション

    Returns:
        List[SpokeResponse]: 各アクションの実行結果
    """
    if not encryption_key:
        encryption_key = os.getenv("ENCRYPTION_KEY", "")

    executor = ActionExecutor(encryption_key, session)
    return await executor.execute_actions(operator_response.actions)
