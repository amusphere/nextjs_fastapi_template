"""
AIアシスタント用のログシステム
"""

import json
import logging
from typing import Any, Dict

from app.services.ai.models import NextAction


class AIAssistantLogger:
    """AIアシスタント専用ロガー"""

    def __init__(self, name: str = "ai_assistant"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # コンソールハンドラー
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def log_action_execution(
        self,
        next_action: NextAction,
        success: bool,
        error: str = None,
    ):
        """アクション実行のログ"""
        status = "SUCCESS" if success else "FAILED"
        log_message = (
            f"Action execution {status} - "
            f"Spoke: {next_action.spoke_name}, "
            f"Type: {next_action.action_type}, "
            f"User: {next_action.parameters.user_id or 'unknown'}, "
        )

        if error:
            log_message += f", Error: {error}"

        if success:
            self.logger.info(log_message)
        else:
            self.logger.error(log_message)

    def error(self, message: str):
        """一般的なエラーログ"""
        self.logger.error(message)

    def info(self, message: str):
        """一般的な情報ログ"""
        self.logger.info(message)

    def warning(self, message: str):
        """一般的な警告ログ"""
        self.logger.warning(message)

    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """エラーログ"""
        log_message = f"Error occurred: {type(error).__name__}: {str(error)}"

        if context:
            log_message += f", Context: {json.dumps(context, default=str)}"

        self.logger.error(log_message, exc_info=True)


# グローバルロガーインスタンス
ai_logger = AIAssistantLogger()
