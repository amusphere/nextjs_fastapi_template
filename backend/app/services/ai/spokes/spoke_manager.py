"""
スポークマネージャー - スポークのインスタンス化と実行を管理
"""

import json
import os
from typing import Dict, List, Optional

import openai
from app.services.ai.logger import AIAssistantLogger
from app.services.ai.models import SpokeResponse
from app.services.ai.spokes.spoke_interface import BaseSpoke
from app.services.ai.spokes.spoke_system import (
    ActionDefinition,
    DynamicSpokeLoader,
    SpokeConfig,
)
from clerk_backend_api import NextAction
from sqlmodel import Session

# OpenAI設定
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
openai_model = "gpt-4.1"


class SpokeManager:
    """スポークマネージャー - スポークのインスタンス化と実行を管理"""

    def __init__(self, session: Optional[Session] = None):
        self.session = session
        self.logger = AIAssistantLogger("spoke_manager")

        # スポークを読み込み
        spokes_dir = os.path.dirname(__file__)  # spoke_manager.pyと同じディレクトリ
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
            instance = spoke_class(self.session)
            self._spoke_instances[spoke_name] = instance
            return instance
        except Exception as e:
            self.logger.error(f"Failed to instantiate spoke {spoke_name}: {str(e)}")
            return None

    async def execute_action(self, action: NextAction) -> SpokeResponse:
        """アクションを実行"""
        spoke_name = self._action_to_spoke.get(action.action_type)
        if spoke_name is None:
            return SpokeResponse(
                success=False,
                error=f"No spoke found for action type: {action.action_type}",
            )

        spoke_instance = self.get_spoke_instance(spoke_name)
        if spoke_instance is None:
            return SpokeResponse(
                success=False, error=f"Failed to get spoke instance for: {spoke_name}"
            )

        # アクション定義を取得
        action_definition = self.get_action_definition(action.action_type)
        if action_definition is None:
            return SpokeResponse(
                success=False,
                error=f"Action definition not found for: {action.action_type}",
            )

        # アクションパラメータを辞書に変換
        parameters = action.get_parameters_dict()

        # LLMにパラメータ推測を依頼
        try:
            predicted_parameters = await self.predict_parameters(
                spoke_name=spoke_name,
                action_type=action.action_type,
                description=action.description,
                parameters=parameters,
                action_definition=action_definition,
            )

            if predicted_parameters:
                # 推測されたパラメータを使用
                parameters = predicted_parameters
            else:
                # 推測が空の場合は元のパラメータを使用
                self.logger.warning(
                    f"No parameters predicted for {action.action_type}, using original parameters."
                )

        except Exception as e:
            # パラメータ推測に失敗した場合は元のパラメータを使用
            self.logger.warning(
                f"Parameter prediction failed for {action.action_type}: {str(e)}"
            )

        self.logger.info(
            f"Executing action {action.spoke_name}.{action.action_type} with parameters: {json.dumps(parameters, ensure_ascii=False)}"
        )

        try:
            return await spoke_instance.execute_action(action.action_type, parameters)
        except Exception as e:
            self.logger.error(f"Error executing action {action.action_type}: {str(e)}")
            return SpokeResponse(success=False, error=f"Execution error: {str(e)}")

    async def predict_parameters(
        self,
        spoke_name: str,
        action_type: str,
        description: str,
        parameters: dict,
        action_definition: dict,
    ) -> dict:
        """
        LLMにパラメータの推測を依頼する
        """
        try:
            # パラメータスキーマを作成
            parameters_schema = action_definition.get("parameters", {})

            # プロンプトを構築
            prompt = f"""
あなたは与えられた情報を基に、アクションに必要なパラメータを推測するAIアシスタントです。

以下の情報を基に、アクションに必要なパラメータを推測してください：

**スポーク名**: {spoke_name}
**アクションタイプ**: {action_type}
**ユーザーの説明**: {description}
**現在のパラメータ**: {parameters}

**アクション定義**:
{json.dumps(action_definition, indent=2, ensure_ascii=False)}

**必要なパラメータスキーマ**:
{json.dumps(parameters_schema, indent=2, ensure_ascii=False)}

以下のJSONフォーマットで応答してください：
{{
    "predicted_parameters": {{
        // 推測したパラメータの値をここに記載
        // 必須パラメータは必ず含める
        // オプションパラメータは適切と思われる場合のみ含める
    }},
}}

注意事項：
- 必須パラメータ（required: true）は必ず推測して含めてください
- 日時フォーマットが指定されている場合は、ISO8601形式（例：2024-01-01T10:00:00Z）で出力してください
- user_idなどのIDパラメータは、具体的な値が分からない場合は null にしてください
- 不明なパラメータは推測せず、null または省略してください
"""

            # OpenAI APIを呼び出し
            response = openai_client.chat.completions.create(
                model=openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "あなたは正確で有用なパラメータ推測を行うAIアシスタントです。",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1000,
                temperature=0.3,  # より確定的な応答のために低めに設定
            )

            # JSONレスポンスをパース
            response_content = response.choices[0].message.content
            parsed_response = json.loads(response_content)

            return parsed_response.get("predicted_parameters", {})

        except Exception as e:
            self.logger.error(f"Failed to predict parameters: {str(e)}")
            return {}

    def get_all_supported_actions(self) -> List[str]:
        """すべてのサポートされているアクションタイプを取得"""
        return list(self._action_to_spoke.keys())

    def get_spoke_configs(self) -> Dict[str, SpokeConfig]:
        """すべてのスポーク設定を取得"""
        return self.registry.get_all_configs()

    def get_all_actions(self) -> List[ActionDefinition]:
        """すべてのアクション定義を取得"""
        return self.registry.get_all_actions()

    def get_action_definition(self, action_type: str) -> Optional[Dict[str, any]]:
        """指定されたアクションタイプの定義を取得"""
        for config in self.registry.get_all_configs().values():
            for action in config.actions:
                if action.action_type == action_type:
                    # ActionDefinitionをJSONシリアライズ可能な辞書に変換
                    return {
                        "action_type": action.action_type,
                        "display_name": action.display_name,
                        "description": action.description,
                        "parameters": {
                            param_name: {
                                "type": param.type,
                                "required": param.required,
                                "description": param.description,
                                "format": param.format,
                                "default": param.default,
                            }
                            for param_name, param in action.parameters.items()
                        },
                    }
        return None
