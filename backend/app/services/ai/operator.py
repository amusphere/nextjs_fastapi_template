import os
import re
from typing import Optional

import openai
from sqlmodel import Session

from .exceptions import InvalidParameterError, PromptAnalysisError
from .logger import AIAssistantLogger
from .models import GenericActionParameters, NextAction, OperatorResponse
from .prompt_generator import DynamicPromptGenerator
from .spokes.spoke_system import DynamicSpokeManager, SpokeConfigLoader

# OpenAI APIクライアントの初期化
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# モデルの指定
model = "gpt-4.1"


class OperatorHub:
    """ハブアンドスポーク形式のオペレーターハブ"""

    def __init__(self, encryption_key: str, session: Optional[Session] = None):
        self.encryption_key = encryption_key
        self.session = session
        self.logger = AIAssistantLogger("operator_hub")

        # スポーク設定を動的にロード
        spokes_dir = os.path.join(os.path.dirname(__file__), "spokes")
        self.config_loader = SpokeConfigLoader(spokes_dir)
        self.spoke_configs = self.config_loader.load_all_spokes()

        # プロンプト生成器を初期化
        self.prompt_generator = DynamicPromptGenerator(self.spoke_configs)

        # 動的スポークマネージャーを初期化
        self.spoke_manager = DynamicSpokeManager(encryption_key, session)

    def _extract_user_id(self, prompt: str) -> int:
        """プロンプトからuser_idを抽出"""
        # [USER_ID: 123] の形式でuser_idが含まれている場合
        match = re.search(r"\[USER_ID:\s*(\d+)\]", prompt)
        if match:
            return int(match.group(1))

        # デフォルトは1（テスト用）
        return 1

    async def analyze_prompt(
        self,
        prompt: str,
    ) -> OperatorResponse:
        """プロンプトを解析してアクション計画を生成"""

        # プロンプトからuser_idを抽出
        user_id = self._extract_user_id(prompt)

        # 動的にシステムプロンプトを生成
        system_prompt = self.prompt_generator.generate_system_prompt(user_id)

        # ログにシステムプロンプトを記録
        self.logger.info(system_prompt)

        try:
            response = client.responses.parse(
                model=model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                text_format=OperatorResponse,
            )

            # 構造化された応答を取得（Pydanticモデルとして自動的にパースされる）
            operator_response = response.output_parsed

            # LLMの応答をログに記録
            self.logger.info(response.output_text)

            # 動的スポークシステムで有効なアクションタイプかどうかをチェック
            supported_actions = self.spoke_manager.get_all_supported_actions()
            for action in operator_response.actions:
                if (
                    action.action_type not in supported_actions
                    and action.action_type != "unknown"
                ):
                    self.logger.log_error(
                        InvalidParameterError(
                            f"Unknown action type: {action.action_type}"
                        ),
                        {"user_id": user_id, "action": action.model_dump()},
                    )
                    action.action_type = "unknown"

            return operator_response

        except PromptAnalysisError as e:
            self.logger.log_error(e, {"user_id": user_id, "prompt": prompt})
            return OperatorResponse(
                actions=[
                    NextAction(
                        action_type="unknown",
                        parameters=GenericActionParameters(),
                        description=str(e),
                    )
                ],
                analysis=str(e),
                confidence=0.0,
            )
        except Exception as e:
            error = PromptAnalysisError(
                f"プロンプト解析中にエラーが発生しました: {str(e)}"
            )
            self.logger.log_error(error, {"user_id": user_id, "prompt": prompt})
            return OperatorResponse(
                actions=[
                    NextAction(
                        action_type="unknown",
                        parameters=GenericActionParameters(),
                        description=f"エラー: {str(e)}",
                    )
                ],
                analysis=f"プロンプト解析中にエラーが発生しました: {str(e)}",
                confidence=0.0,
            )
