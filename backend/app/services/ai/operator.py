import os
from datetime import datetime
from typing import Optional

import openai
from sqlmodel import Session

from .exceptions import InvalidParameterError, PromptAnalysisError
from .logger import AIAssistantLogger
from .models import GenericActionParameters, NextAction, OperatorResponse
from .spokes.spoke_system import DynamicSpokeManager, SpokeConfigLoader

# OpenAI APIクライアントの初期化
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# モデルの指定
model = "gpt-4.1"


class OperatorHub:
    """ハブアンドスポーク形式のオペレーターハブ"""

    def __init__(
        self,
        user_id: int,
        session: Optional[Session] = None,
    ):
        self.user_id = user_id
        self.session = session
        self.logger = AIAssistantLogger("operator_hub")

        # スポーク設定を動的にロード
        spokes_dir = os.path.join(os.path.dirname(__file__), "spokes")
        self.config_loader = SpokeConfigLoader(spokes_dir)
        self.spoke_configs = self.config_loader.load_all_spokes()

        # 動的スポークマネージャーを初期化
        self.spoke_manager = DynamicSpokeManager(session)

    def _generate_actions_list(self) -> str:
        """利用可能なアクションのリストを生成（スポーク毎にグループ化）"""
        actions_list = []

        for config in self.spoke_configs.values():
            # スポーク名を追加
            actions_list.append(f"\n## {config.display_name} ({config.spoke_name})")
            actions_list.append(config.description)

            # そのスポークのアクションを追加
            for action in config.actions:
                actions_list.append(f"- {action.action_type}: {action.description}")

        return "\n".join(actions_list)

    def generate_system_prompt(self) -> str:
        """システムプロンプトを動的に生成"""
        current_time = datetime.now().isoformat()

        # 利用可能なアクションのリストを生成
        actions_list = self._generate_actions_list()

        system_prompt = f"""
あなたはユーザーのリクエストを解析し、適切なアクションを決定するAIアシスタントです。

利用可能なアクション:
{actions_list}

現在の日時: {current_time}
ユーザーID: {self.user_id}

## 重要な指示:
- 相対的な日時表現（「明日」「来週」「今日」「次の金曜日」など）は具体的な日時に変換してください
- 時間が指定されていない場合は、適切なデフォルト時間を設定してください
- user_idは自動的に{self.user_id}を使用してください
"""
        return system_prompt

    async def analyze_prompt(
        self,
        prompt: str,
    ) -> OperatorResponse:
        """プロンプトを解析してアクション計画を生成"""

        # 動的にシステムプロンプトを生成
        system_prompt = self.generate_system_prompt()

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
                        {"user_id": self.user_id, "action": action.model_dump()},
                    )
                    action.action_type = "unknown"

            return operator_response

        except PromptAnalysisError as e:
            self.logger.log_error(e, {"user_id": self.user_id, "prompt": prompt})
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
            self.logger.log_error(error, {"user_id": self.user_id, "prompt": prompt})
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
