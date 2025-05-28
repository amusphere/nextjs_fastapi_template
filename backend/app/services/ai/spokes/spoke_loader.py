"""
動的スポーク読み込みシステム
"""

import importlib.util
import json
import os
from typing import Any, Dict, List, Optional, Type

from sqlmodel import Session

from ..logger import AIAssistantLogger
from ..models import SpokeResponse
from .spoke_interface import BaseSpoke


class SpokeRegistry:
    """スポークの登録と管理を行うレジストリ"""

    def __init__(self):
        self._spokes: Dict[str, Type[BaseSpoke]] = {}
        self._spoke_configs: Dict[str, dict] = {}
        self.logger = AIAssistantLogger("spoke_registry")

    def register_spoke(
        self, spoke_name: str, spoke_class: Type[BaseSpoke], config: dict
    ):
        """スポークを登録"""
        self._spokes[spoke_name] = spoke_class
        self._spoke_configs[spoke_name] = config
        self.logger.info(f"Spoke registered: {spoke_name}")

    def get_spoke_class(self, spoke_name: str) -> Optional[Type[BaseSpoke]]:
        """スポーククラスを取得"""
        return self._spokes.get(spoke_name)

    def get_spoke_config(self, spoke_name: str) -> Optional[dict]:
        """スポーク設定を取得"""
        return self._spoke_configs.get(spoke_name)

    def get_all_spokes(self) -> Dict[str, Type[BaseSpoke]]:
        """すべてのスポークを取得"""
        return self._spokes.copy()

    def get_all_configs(self) -> Dict[str, dict]:
        """すべてのスポーク設定を取得"""
        return self._spoke_configs.copy()

    def get_action_to_spoke_mapping(self) -> Dict[str, str]:
        """アクションタイプからスポーク名へのマッピングを取得"""
        mapping = {}
        for spoke_name, config in self._spoke_configs.items():
            if "actions" in config:
                for action in config["actions"]:
                    action_type = action.get("action_type")
                    if action_type:
                        mapping[action_type] = spoke_name
        return mapping


class DynamicSpokeLoader:
    """動的にスポークを読み込むローダー"""

    def __init__(self, spokes_directory: str):
        self.spokes_directory = spokes_directory
        self.registry = SpokeRegistry()
        self.logger = AIAssistantLogger("spoke_loader")

    def load_all_spokes(self) -> SpokeRegistry:
        """すべてのスポークを読み込み"""
        if not os.path.exists(self.spokes_directory):
            self.logger.warning(f"Spokes directory not found: {self.spokes_directory}")
            return self.registry

        for item in os.listdir(self.spokes_directory):
            spoke_path = os.path.join(self.spokes_directory, item)
            if os.path.isdir(spoke_path) and not item.startswith("__"):
                self._load_spoke(item, spoke_path)

        return self.registry

    def _load_spoke(self, spoke_name: str, spoke_path: str):
        """個別のスポークを読み込み"""
        try:
            # actions.json を読み込み
            actions_file = os.path.join(spoke_path, "actions.json")
            spoke_file = os.path.join(spoke_path, "spoke.py")

            if not os.path.exists(actions_file):
                self.logger.warning(f"actions.json not found for spoke: {spoke_name}")
                return

            if not os.path.exists(spoke_file):
                self.logger.warning(f"spoke.py not found for spoke: {spoke_name}")
                return

            # 設定を読み込み
            with open(actions_file, "r", encoding="utf-8") as f:
                config = json.load(f)

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

    def get_spoke_configs(self) -> Dict[str, dict]:
        """すべてのスポーク設定を取得"""
        return self.registry.get_all_configs()
