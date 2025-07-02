import os
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from app.utils.llm import llm_chat_completions_perse
from sqlmodel import Session

from .exceptions import InvalidParameterError, PromptAnalysisError
from .logger import AIAssistantLogger
from .models import NextAction, OperatorResponse
from .spokes.spoke_system import SpokeConfigLoader


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

    def _generate_actions_list(self) -> str:
        """利用可能なアクションのリストを生成（スポーク毎にグループ化）"""
        actions_list = []

        for config in self.spoke_configs.values():
            # スポーク名を追加
            actions_list.append(
                f"\n## {config.display_name}\nスポーク名: {config.spoke_name}\n説明: {config.description}\n"
            )
            actions_list.append(config.description)

            actions_list.append("\n### アクション名: 説明")

            # そのスポークのアクションを追加
            for action in config.actions:
                actions_list.append(f"- {action.action_type}: {action.description}")

        return "\n".join(actions_list)

    def generate_system_prompt(self) -> str:
        """システムプロンプトを動的に生成"""
        # 日本時間で現在時刻を取得
        jst = ZoneInfo("Asia/Tokyo")
        current_time = datetime.now(jst).isoformat()

        # 利用可能なアクションのリストを生成
        actions_list = self._generate_actions_list()

        system_prompt = f"""
あなたはユーザーのリクエストを解析し、適切なアクションを決定するAIアシスタントです。

利用可能なアクション:
{actions_list}

現在の日時: {current_time} (JST)
ユーザーID: {self.user_id}

## 重要な指示:
- parameters に user_id: {self.user_id} を必ず含めてください
- 相対的な日時表現（「明日」「来週」「今日」「次の金曜日」など）は具体的な日時に変換してください
- 日時に関することは基本的に日本時間（JST）で処理を行ってください
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
            # LLMにプロンプトを送信して応答を取得
            operator_response = llm_chat_completions_perse(
                prompts=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                response_format=OperatorResponse,
                temperature=0.7,
                max_tokens=1500,
            )

            # LLMの応答をログに記録
            self.logger.info(operator_response.model_dump_json())

            # 動的スポークシステムで有効なアクションタイプかどうかをチェック
            supported_actions = self.config_loader.get_all_action_types()
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
                        spoke_name="unknown",
                        action_type="unknown",
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
                        spoke_name="unknown",
                        action_type="unknown",
                        description=f"エラー: {str(e)}",
                    )
                ],
                analysis=f"プロンプト解析中にエラーが発生しました: {str(e)}",
                confidence=0.0,
            )
