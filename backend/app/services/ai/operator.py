import json
from typing import Optional
from datetime import datetime
from sqlmodel import Session

from .models import ActionType, NextAction, OperatorResponse
from .spokes.google_calendar import GoogleCalendarSpoke
from ..llm import client


class OperatorHub:
    """ハブアンドスポーク形式のオペレーターハブ"""

    def __init__(self, encryption_key: str, session: Optional[Session] = None):
        self.encryption_key = encryption_key
        self.session = session
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

        system_prompt = f"""
        あなたはユーザーのリクエストを解析し、適切なアクションを決定するAIアシスタントです。

        利用可能なアクション:
        1. get_calendar_events: カレンダーの予定を取得
        2. create_calendar_event: カレンダーに新しい予定を作成
        3. update_calendar_event: 既存の予定を更新
        4. delete_calendar_event: 予定を削除

        現在の日時: {datetime.now().isoformat()}
        ユーザーID: {user_id}

        ## 重要な指示:
        - 相対的な日時表現（「明日」「来週」「今日」「次の金曜日」など）は具体的な日時に変換してください
        - 時間が指定されていない場合は、適切なデフォルト時間を設定してください
        - user_idは自動的に{user_id}を使用してください
        - 期間指定がない場合は、今日から1週間後までを検索範囲とします

        ## 日時変換の例:
        - "明日" → 翌日の日付
        - "来週" → 来週月曜日から日曜日まで
        - "今日の予定" → 今日の0:00から23:59まで
        - "午後2時" → 今日または指定日の14:00

        ## アクション判定ロジック:
        - "予定を確認", "スケジュール", "何がある" → get_calendar_events
        - "予定を作成", "登録", "追加", "予約" → create_calendar_event
        - "予定を変更", "修正", "更新" → update_calendar_event
        - "予定を削除", "キャンセル", "消去" → delete_calendar_event

        以下のJSON形式で応答してください:
        {{
            "actions": [
                {{
                    "action_type": "アクションタイプ",
                    "parameters": {{
                        "user_id": {user_id},
                        "必要なパラメータ": "値"
                    }},
                    "priority": 1,
                    "description": "このアクションの説明"
                }}
            ],
            "analysis": "プロンプト解析結果の説明",
            "confidence": 0.9
        }}

        パラメータの例:
        - get_calendar_events: {{"user_id": {user_id}, "start_date": "2024-01-01T00:00:00", "end_date": "2024-01-07T23:59:59"}}
        - create_calendar_event: {{"user_id": {user_id}, "summary": "会議", "start_time": "2024-01-01T10:00:00", "end_time": "2024-01-01T11:00:00"}}
        - update_calendar_event: {{"user_id": {user_id}, "event_id": "event123", "summary": "更新された会議"}}
        - delete_calendar_event: {{"user_id": {user_id}, "event_id": "event123"}}
        """

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
        import os

        if not encryption_key:
            encryption_key = os.getenv("ENCRYPTION_KEY", "")

        hub = cls(encryption_key, session)
        return await hub.analyze_prompt(prompt, max_tokens, temperature)