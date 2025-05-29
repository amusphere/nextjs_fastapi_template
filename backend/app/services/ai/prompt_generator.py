"""
動的プロンプト生成器
"""

from datetime import datetime
from typing import Dict

from .spokes.spoke_system import SpokeConfig


class DynamicPromptGenerator:
    """スポーク設定に基づいて動的にプロンプトを生成"""

    def __init__(self, spoke_configs: Dict[str, SpokeConfig]):
        self.spoke_configs = spoke_configs

    def generate_system_prompt(self, user_id: int) -> str:
        """システムプロンプトを動的に生成"""
        current_time = datetime.now().isoformat()

        # 利用可能なアクションのリストを生成
        actions_list = self._generate_actions_list()

        system_prompt = f"""
あなたはユーザーのリクエストを解析し、適切なアクションを決定するAIアシスタントです。

利用可能なアクション:
{actions_list}

現在の日時: {current_time}
ユーザーID: {user_id}

## 重要な指示:
- 相対的な日時表現（「明日」「来週」「今日」「次の金曜日」など）は具体的な日時に変換してください
- 時間が指定されていない場合は、適切なデフォルト時間を設定してください
- user_idは自動的に{user_id}を使用してください
"""
        return system_prompt

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
