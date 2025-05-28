"""
統合スポークシステム - 設定管理・動的ローダー・マネージャー
"""

import importlib.util
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from sqlmodel import Session

from ..logger import AIAssistantLogger
from ..models import SpokeResponse
from .spoke_interface import BaseSpoke


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


class SpokeRegistry:
    """スポークの登録と管理を行うレジストリ"""

    def __init__(self):
        self._spokes: Dict[str, Type[BaseSpoke]] = {}
        self._spoke_configs: Dict[str, SpokeConfig] = {}
        self.logger = AIAssistantLogger("spoke_registry")

    def register_spoke(
        self, spoke_name: str, spoke_class: Type[BaseSpoke], config: SpokeConfig
    ):
        """スポークを登録"""
        self._spokes[spoke_name] = spoke_class
        self._spoke_configs[spoke_name] = config
        self.logger.info(f"Spoke registered: {spoke_name}")

    def get_spoke_class(self, spoke_name: str) -> Optional[Type[BaseSpoke]]:
        """スポーククラスを取得"""
        return self._spokes.get(spoke_name)

    def get_spoke_config(self, spoke_name: str) -> Optional[SpokeConfig]:
        """スポーク設定を取得"""
        return self._spoke_configs.get(spoke_name)

    def get_all_spokes(self) -> Dict[str, Type[BaseSpoke]]:
        """すべてのスポークを取得"""
        return self._spokes.copy()

    def get_all_configs(self) -> Dict[str, SpokeConfig]:
        """すべてのスポーク設定を取得"""
        return self._spoke_configs.copy()

    def get_action_to_spoke_mapping(self) -> Dict[str, str]:
        """アクションタイプからスポーク名へのマッピングを取得"""
        mapping = {}
        for spoke_name, config in self._spoke_configs.items():
            for action in config.actions:
                mapping[action.action_type] = spoke_name
        return mapping

    def get_all_actions(self) -> List[ActionDefinition]:
        """すべてのスポークからアクション定義を取得"""
        all_actions = []
        for config in self._spoke_configs.values():
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


class DynamicSpokeLoader:
    """動的にスポークを読み込むローダー"""

    def __init__(self, spokes_directory: str):
        self.spokes_directory = spokes_directory
        self.config_loader = SpokeConfigLoader(spokes_directory)
        self.registry = SpokeRegistry()
        self.logger = AIAssistantLogger("spoke_loader")

    def load_all_spokes(self) -> SpokeRegistry:
        """すべてのスポークを読み込み"""
        if not os.path.exists(self.spokes_directory):
            self.logger.warning(f"Spokes directory not found: {self.spokes_directory}")
            return self.registry

        # 設定を読み込み
        configs = self.config_loader.load_all_spokes()

        # 各スポークについてクラスを読み込み
        for spoke_name, config in configs.items():
            spoke_path = os.path.join(self.spokes_directory, spoke_name)
            if os.path.isdir(spoke_path):
                self._load_spoke(spoke_name, spoke_path, config)

        return self.registry

    def _load_spoke(self, spoke_name: str, spoke_path: str, config: SpokeConfig):
        """個別のスポークを読み込み"""
        try:
            spoke_file = os.path.join(spoke_path, "spoke.py")

            if not os.path.exists(spoke_file):
                self.logger.warning(f"spoke.py not found for spoke: {spoke_name}")
                return

            # スポーククラスを動的にインポート
            spoke_class = self._import_spoke_class(spoke_file, spoke_name)
            if spoke_class is None:
                return

            # レジストリに登録
            self.registry.register_spoke(spoke_name, spoke_class, config)

        except Exception as e:
            self.logger.error(f"Failed to load spoke {spoke_name}: {str(e)}")

    def _import_spoke_class(
        self, spoke_file: str, spoke_name: str
    ) -> Optional[Type[BaseSpoke]]:
        """スポーククラスを動的にインポート"""
        try:
            spec = importlib.util.spec_from_file_location(
                f"{spoke_name}_spoke", spoke_file
            )
            if spec is None or spec.loader is None:
                self.logger.error(f"Failed to create module spec for {spoke_name}")
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # スポーククラスを探す（命名規則に基づく）
            class_name = self._get_spoke_class_name(spoke_name)
            spoke_class = getattr(module, class_name, None)

            if spoke_class is None:
                self.logger.error(f"Spoke class {class_name} not found in {spoke_file}")
                return None

            if not issubclass(spoke_class, BaseSpoke):
                self.logger.error(f"Class {class_name} is not a subclass of BaseSpoke")
                return None

            return spoke_class

        except Exception as e:
            self.logger.error(
                f"Failed to import spoke class from {spoke_file}: {str(e)}"
            )
            return None

    def _get_spoke_class_name(self, spoke_name: str) -> str:
        """スポーク名からクラス名を生成"""
        # google_calendar -> GoogleCalendarSpoke
        parts = spoke_name.split("_")
        class_name = "".join(word.capitalize() for word in parts) + "Spoke"
        return class_name


class DynamicSpokeManager:
    """動的スポークマネージャー - スポークのインスタンス化と実行を管理"""

    def __init__(self, encryption_key: str, session: Optional[Session] = None):
        self.encryption_key = encryption_key
        self.session = session
        self.logger = AIAssistantLogger("spoke_manager")

        # スポークを読み込み
        spokes_dir = os.path.join(os.path.dirname(__file__), "spokes")
        loader = DynamicSpokeLoader(spokes_dir)
        self.registry = loader.load_all_spokes()

        # スポークインスタンスをキャッシュ
        self._spoke_instances: Dict[str, BaseSpoke] = {}

        # アクションタイプからスポーク名へのマッピング
        self._action_to_spoke = self.registry.get_action_to_spoke_mapping()

    def get_spoke_instance(self, spoke_name: str) -> Optional[BaseSpoke]:
        """スポークインスタンスを取得（キャッシュ付き）"""
        if spoke_name in self._spoke_instances:
            return self._spoke_instances[spoke_name]

        spoke_class = self.registry.get_spoke_class(spoke_name)
        if spoke_class is None:
            return None

        try:
            instance = spoke_class(self.encryption_key, self.session)
            self._spoke_instances[spoke_name] = instance
            return instance
        except Exception as e:
            self.logger.error(f"Failed to instantiate spoke {spoke_name}: {str(e)}")
            return None

    async def execute_action(
        self, action_type: str, parameters: Dict[str, Any]
    ) -> SpokeResponse:
        """アクションを実行"""
        spoke_name = self._action_to_spoke.get(action_type)
        if spoke_name is None:
            return SpokeResponse(
                success=False, error=f"No spoke found for action type: {action_type}"
            )

        spoke_instance = self.get_spoke_instance(spoke_name)
        if spoke_instance is None:
            return SpokeResponse(
                success=False, error=f"Failed to get spoke instance for: {spoke_name}"
            )

        try:
            return await spoke_instance.execute_action(action_type, parameters)
        except Exception as e:
            self.logger.error(f"Error executing action {action_type}: {str(e)}")
            return SpokeResponse(success=False, error=f"Execution error: {str(e)}")

    def get_all_supported_actions(self) -> List[str]:
        """すべてのサポートされているアクションタイプを取得"""
        return list(self._action_to_spoke.keys())

    def get_spoke_configs(self) -> Dict[str, SpokeConfig]:
        """すべてのスポーク設定を取得"""
        return self.registry.get_all_configs()

    def get_all_actions(self) -> List[ActionDefinition]:
        """すべてのアクション定義を取得"""
        return self.registry.get_all_actions()

    def get_actions_by_keywords(self, keywords: List[str]) -> List[ActionDefinition]:
        """キーワードに基づいてアクションを検索"""
        return self.registry.get_actions_by_keywords(keywords)
