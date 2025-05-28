"""
動的プロンプト生成器
"""

from datetime import datetime
from typing import Dict

from .spokes.spoke_config import SpokeConfig


class DynamicPromptGenerator:
    """スポーク設定に基づいて動的にプロンプトを生成"""

    def __init__(self, spoke_configs: Dict[str, SpokeConfig]):
        self.spoke_configs = spoke_configs

    def generate_system_prompt(self, user_id: int) -> str:
        """システムプロンプトを動的に生成"""
        current_time = datetime.now().isoformat()

        # 利用可能なアクションのリストを生成
        actions_list = self._generate_actions_list()

        # アクション判定ロジックを生成
        action_logic = self._generate_action_logic()

        # パラメータ例を生成
        parameter_examples = self._generate_parameter_examples(user_id)

        # 日時変換ルールを生成
        datetime_rules = self._generate_datetime_rules()

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
- 期間指定がない場合は、今日から1週間後までを検索範囲とします

{datetime_rules}

## アクション判定ロジック:
{action_logic}

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
{parameter_examples}
"""
        return system_prompt

    def _generate_actions_list(self) -> str:
        """利用可能なアクションのリストを生成"""
        actions = []
        for config in self.spoke_configs.values():
            for action in config.actions:
                actions.append(
                    f"{len(actions) + 1}. {action.action_type}: {action.description}"
                )
        return "\n".join(actions)

    def _generate_action_logic(self) -> str:
        """アクション判定ロジックを生成"""
        logic_lines = []
        for config in self.spoke_configs.values():
            for action in config.actions:
                keywords_str = '", "'.join(action.keywords)
                logic_lines.append(f'- "{keywords_str}" → {action.action_type}')
        return "\n".join(logic_lines)

    def _generate_parameter_examples(self, user_id: int) -> str:
        """パラメータ例を生成"""
        examples = []
        for config in self.spoke_configs.values():
            for action in config.actions:
                required_params = {}
                for param_name, param_def in action.parameters.items():
                    if param_def.required:
                        if param_name == "user_id":
                            required_params[param_name] = user_id
                        elif param_def.type == "string":
                            if param_def.format == "datetime":
                                required_params[param_name] = "2024-01-01T10:00:00"
                            else:
                                required_params[param_name] = "サンプル値"
                        elif param_def.type == "integer":
                            required_params[param_name] = 123
                        else:
                            required_params[param_name] = "値"

                if required_params:
                    examples.append(f"- {action.action_type}: {required_params}")

        return "\n".join(examples)

    def _generate_datetime_rules(self) -> str:
        """日時変換ルールを生成"""
        rules = []

        # すべてのスポークから日時変換ルールを収集
        all_relative_expressions = {}
        all_default_times = {}

        for config in self.spoke_configs.values():
            if config.date_time_conversion_rules:
                relative_expressions = config.date_time_conversion_rules.get(
                    "relative_expressions", {}
                )
                default_times = config.date_time_conversion_rules.get(
                    "default_times", {}
                )

                all_relative_expressions.update(relative_expressions)
                all_default_times.update(default_times)

        if all_relative_expressions:
            rules.append("## 日時変換の例:")
            for expression, value in all_relative_expressions.items():
                if value == "today":
                    rules.append(f'- "{expression}" → 今日の日付')
                elif value == "tomorrow":
                    rules.append(f'- "{expression}" → 翌日の日付')
                elif value == "next_week":
                    rules.append(f'- "{expression}" → 来週月曜日から日曜日まで')
                else:
                    rules.append(f'- "{expression}" → {value}')

        if all_default_times:
            rules.append("\n## デフォルト時間:")
            for time_desc, time_value in all_default_times.items():
                rules.append(f'- "{time_desc}" → {time_value}')

        return "\n".join(rules) if rules else ""
