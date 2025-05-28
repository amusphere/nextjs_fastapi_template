"""
スポーク設定管理とローダー
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ActionParameter:
    """アクションパラメータの定義"""

    type: str
    required: bool
    description: str
    format: Optional[str] = None
    default: Optional[str] = None


@dataclass
class ActionDefinition:
    """アクション定義"""

    action_type: str
    display_name: str
    description: str
    keywords: List[str]
    parameters: Dict[str, ActionParameter]
    examples: List[str]


@dataclass
class SpokeConfig:
    """スポーク設定"""

    spoke_name: str
    display_name: str
    description: str
    actions: List[ActionDefinition]
    date_time_conversion_rules: Optional[Dict[str, Any]] = None


class SpokeConfigLoader:
    """スポーク設定ローダー"""

    def __init__(self, spokes_dir: str):
        self.spokes_dir = Path(spokes_dir)
        self._configs: Dict[str, SpokeConfig] = {}

    def load_all_spokes(self) -> Dict[str, SpokeConfig]:
        """すべてのスポーク設定を読み込み"""
        self._configs.clear()

        for spoke_dir in self.spokes_dir.iterdir():
            if spoke_dir.is_dir() and not spoke_dir.name.startswith("."):
                config_file = spoke_dir / "actions.json"
                if config_file.exists():
                    try:
                        config = self._load_spoke_config(config_file)
                        self._configs[config.spoke_name] = config
                    except Exception as e:
                        print(f"Error loading spoke config from {config_file}: {e}")

        return self._configs

    def _load_spoke_config(self, config_file: Path) -> SpokeConfig:
        """スポーク設定ファイルを読み込み"""
        with open(config_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # アクション定義をパース
        actions = []
        for action_data in data.get("actions", []):
            parameters = {}
            for param_name, param_data in action_data.get("parameters", {}).items():
                parameters[param_name] = ActionParameter(
                    type=param_data.get("type", "string"),
                    required=param_data.get("required", False),
                    description=param_data.get("description", ""),
                    format=param_data.get("format"),
                    default=param_data.get("default"),
                )

            action = ActionDefinition(
                action_type=action_data.get("action_type", ""),
                display_name=action_data.get("display_name", ""),
                description=action_data.get("description", ""),
                keywords=action_data.get("keywords", []),
                parameters=parameters,
                examples=action_data.get("examples", []),
            )
            actions.append(action)

        return SpokeConfig(
            spoke_name=data.get("spoke_name", ""),
            display_name=data.get("display_name", ""),
            description=data.get("description", ""),
            actions=actions,
            date_time_conversion_rules=data.get("date_time_conversion_rules"),
        )

    def get_spoke_config(self, spoke_name: str) -> Optional[SpokeConfig]:
        """指定されたスポークの設定を取得"""
        return self._configs.get(spoke_name)

    def get_all_actions(self) -> List[ActionDefinition]:
        """すべてのスポークからアクション定義を取得"""
        all_actions = []
        for config in self._configs.values():
            all_actions.extend(config.actions)
        return all_actions

    def get_actions_by_keywords(self, keywords: List[str]) -> List[ActionDefinition]:
        """キーワードに基づいてアクションを検索"""
        matching_actions = []
        for action in self.get_all_actions():
            for keyword in keywords:
                if any(
                    keyword.lower() in action_keyword.lower()
                    for action_keyword in action.keywords
                ):
                    matching_actions.append(action)
                    break
        return matching_actions
