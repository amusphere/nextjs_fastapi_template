"""
AIアシスタント用のログシステム
"""
import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional


class AIAssistantLogger:
    """AIアシスタント専用ロガー"""

    def __init__(self, name: str = "ai_assistant"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # コンソールハンドラー
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def log_prompt_analysis(
        self,
        prompt: str,
        user_id: int,
        confidence: float,
        actions_count: int,
        duration: float = None
    ):
        """プロンプト解析のログ"""
        self.logger.info(
            f"Prompt analysis completed - "
            f"User: {user_id}, "
            f"Actions: {actions_count}, "
            f"Confidence: {confidence:.2f}, "
            f"Duration: {duration:.2f}s" if duration else f"Duration: N/A"
        )

    def log_action_execution(
        self,
        action_type: str,
        user_id: int,
        success: bool,
        duration: float = None,
        error: str = None
    ):
        """アクション実行のログ"""
        status = "SUCCESS" if success else "FAILED"
        log_message = (
            f"Action execution {status} - "
            f"Type: {action_type}, "
            f"User: {user_id}"
        )

        if duration:
            log_message += f", Duration: {duration:.2f}s"

        if error:
            log_message += f", Error: {error}"

        if success:
            self.logger.info(log_message)
        else:
            self.logger.error(log_message)

    def log_calendar_operation(
        self,
        operation: str,
        user_id: int,
        event_count: int = None,
        event_id: str = None,
        success: bool = True
    ):
        """カレンダー操作のログ"""
        log_message = f"Calendar {operation} - User: {user_id}"

        if event_count is not None:
            log_message += f", Events: {event_count}"

        if event_id:
            log_message += f", EventID: {event_id}"

        if success:
            self.logger.info(log_message)
        else:
            self.logger.error(log_message)

    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """エラーログ"""
        log_message = f"Error occurred: {type(error).__name__}: {str(error)}"

        if context:
            log_message += f", Context: {json.dumps(context, default=str)}"

        self.logger.error(log_message, exc_info=True)

    def log_performance_metrics(self, metrics: Dict[str, Any]):
        """パフォーマンスメトリクスのログ"""
        self.logger.info(f"Performance metrics: {json.dumps(metrics, default=str)}")


# グローバルロガーインスタンス
ai_logger = AIAssistantLogger()
