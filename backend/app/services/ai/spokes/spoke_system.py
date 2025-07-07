"""
統合スポークシステム - 設定管理・動的ローダー・マネージャー
"""

import importlib.util
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Type

from app.schema import User
from app.services.ai.logger import AIAssistantLogger
from app.services.ai.spokes.spoke_interface import BaseSpoke


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
    parameters: Dict[str, ActionParameter]


@dataclass
class SpokeConfig:
    """スポーク設定"""

    spoke_name: str
    display_name: str
    description: str
    actions: List[ActionDefinition]


class SpokeConfigLoader:
    """スポーク設定ローダー"""

    def __init__(self, spokes_dir: str):
        self.spokes_dir = Path(spokes_dir)
        self._configs: Dict[str, SpokeConfig] = {}
        self.logger = AIAssistantLogger("spoke_config_loader")

    def load_all_spokes(self) -> Dict[str, SpokeConfig]:
        """すべてのスポーク設定を読み込み"""
        self._configs.clear()

        # 除外するディレクトリ
        excluded_dirs = {"__pycache__", ".git", "node_modules", "venv", ".venv"}

        for spoke_dir in self.spokes_dir.iterdir():
            # ディレクトリかつ、除外リストにない場合のみ処理
            if (
                spoke_dir.is_dir()
                and not spoke_dir.name.startswith(".")
                and spoke_dir.name not in excluded_dirs
            ):

                config_file = spoke_dir / "actions.json"
                if config_file.exists():
                    try:
                        config = self._load_spoke_config(config_file)
                        self._configs[config.spoke_name] = config
                    except Exception as e:
                        self.logger.error(
                            f"Error loading spoke config from {config_file}: {e}"
                        )
                else:
                    self.logger.warning(f"No actions.json found in: {spoke_dir}")

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
                parameters=parameters,
            )
            actions.append(action)

        return SpokeConfig(
            spoke_name=data.get("spoke_name", ""),
            display_name=data.get("display_name", ""),
            description=data.get("description", ""),
            actions=actions,
        )

    def get_spoke_config(self, spoke_name: str) -> Optional[SpokeConfig]:
        """指定されたスポークの設定を取得"""
        return self._configs.get(spoke_name)

    def get_all_action_types(self) -> List[str]:
        """すべてのスポークから利用可能なアクションタイプを取得"""
        action_types = set()
        for config in self._configs.values():
            for action in config.actions:
                action_types.add(action.action_type)
        return sorted(action_types)


class SpokeRegistry:
    """スポークの登録と管理を行うレジストリ"""

    def __init__(self):
        self._spokes: Dict[str, Type[BaseSpoke]] = {}
        self._spoke_configs: Dict[str, SpokeConfig] = {}
        self.logger = AIAssistantLogger("spoke_registry")

    def register_spoke(
        self,
        spoke_name: str,
        spoke_class: Type[BaseSpoke],
        config: SpokeConfig,
    ):
        """スポークを登録"""
        self._spokes[spoke_name] = spoke_class
        self._spoke_configs[spoke_name] = config

    def get_spoke_class(
        self,
        spoke_name: str,
        current_user: User,
    ) -> Optional[Type[BaseSpoke]]:
        """スポーククラスを取得"""
        return self._spokes.get(spoke_name)

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

    def get_action_definition(
        self, spoke_name: str, action_type: str
    ) -> Optional[ActionDefinition]:
        """指定されたスポークのアクション定義を取得"""
        config = self._spoke_configs.get(spoke_name)
        if config:
            for action in config.actions:
                if action.action_type == action_type:
                    return action
        return None


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
            else:
                self.logger.warning(f"Spoke directory not found: {spoke_path}")

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
                self.logger.error(f"Failed to import spoke class for: {spoke_name}")
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
                # モジュール内の利用可能なクラスをログ出力
                available_classes = [
                    name for name in dir(module) if not name.startswith("_")
                ]
                self.logger.info(f"Available classes in module: {available_classes}")
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
