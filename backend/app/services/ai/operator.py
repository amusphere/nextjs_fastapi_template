import json
import os
from typing import Optional
from sqlmodel import Session

from .models import ActionType, NextAction, OperatorResponse
from .spokes.google_calendar.spoke import GoogleCalendarSpoke
from .spoke_config import SpokeConfigLoader
from .prompt_generator import DynamicPromptGenerator
from ..llm import client


class OperatorHub:
    """ハブアンドスポーク形式のオペレーターハブ"""

    def __init__(self, encryption_key: str, session: Optional[Session] = None):
        self.encryption_key = encryption_key
        self.session = session

        # スポーク設定を動的にロード
        spokes_dir = os.path.join(os.path.dirname(__file__), 'spokes')
        self.config_loader = SpokeConfigLoader(spokes_dir)
        self.spoke_configs = self.config_loader.load_all_spokes()

        # プロンプト生成器を初期化
        self.prompt_generator = DynamicPromptGenerator(self.spoke_configs)

        # スポークインスタンスを初期化
        self.google_calendar_spoke = GoogleCalendarSpoke(encryption_key, session)

    def _extract_user_id(self, prompt: str) -> int:
        """プロンプトからuser_idを抽出"""
        import re

        # [USER_ID: 123] の形式でuser_idが含まれている場合
        match = re.search(r'\[USER_ID:\s*(\d+)\]', prompt)
        if match:
            return int(match.group(1))

        # デフォルトは1（テスト用）
        return 1

    async def analyze_prompt(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> OperatorResponse:
        """プロンプトを解析してアクション計画を生成"""

        # プロンプトからuser_idを抽出
        user_id = self._extract_user_id(prompt)

        # 動的にシステムプロンプトを生成
        system_prompt = self.prompt_generator.generate_system_prompt(user_id)

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                response_format={"type": "json_object"}
            )

            # JSONレスポンスをパース
            response_data = json.loads(response.choices[0].message.content)

            # NextActionオブジェクトに変換
            actions = []
            for action_data in response_data.get("actions", []):
                action = NextAction(
                    action_type=ActionType(action_data.get("action_type", "unknown")),
                    parameters=action_data.get("parameters", {}),
                    priority=action_data.get("priority", 1),
                    description=action_data.get("description", "")
                )
                actions.append(action)

            return OperatorResponse(
                actions=actions,
                analysis=response_data.get("analysis", ""),
                confidence=response_data.get("confidence", 0.5)
            )

        except json.JSONDecodeError as e:
            return OperatorResponse(
                actions=[NextAction(
                    action_type=ActionType.UNKNOWN,
                    parameters={},
                    description=f"JSONパースエラー: {str(e)}"
                )],
                analysis="LLMの応答をJSONとして解析できませんでした",
                confidence=0.0
            )
        except Exception as e:
            return OperatorResponse(
                actions=[NextAction(
                    action_type=ActionType.UNKNOWN,
                    parameters={},
                    description=f"エラー: {str(e)}"
                )],
                analysis=f"プロンプト解析中にエラーが発生しました: {str(e)}",
                confidence=0.0
            )

    @classmethod
    async def create_and_analyze(
        cls,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        encryption_key: Optional[str] = None,
        session: Optional[Session] = None
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