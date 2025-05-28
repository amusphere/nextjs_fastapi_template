import json
import os
import re
from typing import Optional

import openai
from sqlmodel import Session

from .exceptions import InvalidParameterError, PromptAnalysisError
from .logger import AIAssistantLogger
from .models import NextAction, OperatorResponse
from .prompt_generator import DynamicPromptGenerator
from .spokes.spoke_system import DynamicSpokeManager, SpokeConfigLoader

# OpenAI APIクライアントの初期化
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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
        self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7
    ) -> OperatorResponse:
        """プロンプトを解析してアクション計画を生成"""
        import time

        start_time = time.time()

        # プロンプトからuser_idを抽出
        user_id = self._extract_user_id(prompt)

        # 動的にシステムプロンプトを生成
        system_prompt = self.prompt_generator.generate_system_prompt(user_id)

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                response_format={"type": "json_object"},
            )

            # JSONレスポンスをパース
            response_content = response.choices[0].message.content
            if not response_content:
                raise PromptAnalysisError("LLMからの応答が空です")

            response_data = json.loads(response_content)

            # 必要なフィールドの検証
            if "actions" not in response_data:
                raise PromptAnalysisError("応答にactionsフィールドがありません")

            # NextActionオブジェクトに変換
            actions = []
            for action_data in response_data.get("actions", []):
                try:
                    action_type_str = action_data.get("action_type", "unknown")
                    # 動的スポークシステムで有効なアクションタイプかどうかをチェック
                    supported_actions = self.spoke_manager.get_all_supported_actions()
                    if action_type_str not in supported_actions and action_type_str != "unknown":
                        self.logger.log_error(
                            InvalidParameterError(
                                f"Unknown action type: {action_type_str}"
                            ),
                            {"user_id": user_id, "action_data": action_data},
                        )
                        action_type_str = "unknown"

                    action = NextAction(
                        action_type=action_type_str,
                        parameters=action_data.get("parameters", {}),
                        priority=action_data.get("priority", 1),
                        description=action_data.get("description", ""),
                    )
                    actions.append(action)
                except Exception as e:
                    self.logger.log_error(
                        e, {"user_id": user_id, "action_data": action_data}
                    )
                    continue

            # パフォーマンス測定
            duration = time.time() - start_time
            confidence = response_data.get("confidence", 0.5)

            # ログ記録
            self.logger.log_prompt_analysis(
                prompt=prompt,
                user_id=user_id,
                confidence=confidence,
                actions_count=len(actions),
                duration=duration,
            )

            return OperatorResponse(
                actions=actions,
                analysis=response_data.get("analysis", ""),
                confidence=confidence,
            )

        except json.JSONDecodeError as e:
            error = PromptAnalysisError(f"JSONパースエラー: {str(e)}")
            self.logger.log_error(error, {"user_id": user_id, "prompt": prompt})
            return OperatorResponse(
                actions=[
                    NextAction(
                        action_type="unknown",
                        parameters={},
                        description=f"JSONパースエラー: {str(e)}",
                    )
                ],
                analysis="LLMの応答をJSONとして解析できませんでした",
                confidence=0.0,
            )
        except PromptAnalysisError as e:
            self.logger.log_error(e, {"user_id": user_id, "prompt": prompt})
            return OperatorResponse(
                actions=[
                    NextAction(
                        action_type="unknown",
                        parameters={},
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
                        parameters={},
                        description=f"エラー: {str(e)}",
                    )
                ],
                analysis=f"プロンプト解析中にエラーが発生しました: {str(e)}",
                confidence=0.0,
            )

    @classmethod
    async def create_and_analyze(
        cls,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        encryption_key: Optional[str] = None,
        session: Optional[Session] = None,
    ) -> OperatorResponse:
        """OperatorHubを作成してプロンプトを解析する便利メソッド

        Args:
            prompt: 解析するプロンプト
            max_tokens: LLMの最大トークン数
            temperature: LLMの温度パラメータ
            encryption_key: 暗号化キー
            session: データベースセッション

        Returns:
            OperatorResponse: 次に実行すべきアクションのリスト
        """
        if not encryption_key:
            encryption_key = os.getenv("ENCRYPTION_KEY", "")

        hub = cls(encryption_key, session)
        return await hub.analyze_prompt(prompt, max_tokens, temperature)
