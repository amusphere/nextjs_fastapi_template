from typing import Any, Dict, List, Optional

from app.utils.llm import llm_chat_completions
from sqlmodel import Session

from .executor import ActionExecutor
from .models import OperatorResponse, SpokeResponse
from .operator import OperatorHub


class AIOrchestrator:
    """AIアシスタントのオーケストレーター（統合レイヤー）"""

    def __init__(
        self,
        user_id: int,
        session: Optional[Session] = None,
    ):
        self.session = session
        self.operator_hub = OperatorHub(user_id, session)

    async def process_request(
        self,
        prompt: str,
    ) -> Dict[str, Any]:
        """ユーザーリクエストを処理して結果を返す

        Args:
            prompt: ユーザーのプロンプト
            temperature: LLMの温度パラメータ

        Returns:
            Dict containing:
                - operator_response: オペレーターの解析結果
                - execution_results: 各アクションの実行結果
                - summary: 実行サマリー
        """
        try:
            # Step 1: プロンプトを解析してアクション計画を取得
            operator_response: OperatorResponse = (
                await self.operator_hub.analyze_prompt(prompt=prompt)
            )

            # Step 2: アクション計画を実行
            executor = ActionExecutor(self.session)
            execution_results: List[SpokeResponse] = await executor.execute_actions(
                operator_response.actions
            )

            # Step 3: 実行結果をサマリー
            summary = self._create_execution_summary(
                prompt, operator_response, execution_results
            )

            return {
                "success": True,
                "operator_response": {
                    "analysis": operator_response.analysis,
                    "confidence": operator_response.confidence,
                    "actions_planned": len(operator_response.actions),
                },
                "execution_results": [
                    {
                        "success": result.success,
                        "data": result.data,
                        "error": result.error,
                        "metadata": result.metadata,
                    }
                    for result in execution_results
                ],
                "summary": summary,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Processing error: {str(e)}",
                "operator_response": None,
                "execution_results": [],
                "summary": {
                    "total_actions": 0,
                    "successful_actions": 0,
                    "failed_actions": 1,
                    "overall_status": "failed",
                },
            }

    def _create_execution_summary(
        self,
        prompt: str,
        operator_response: OperatorResponse,
        execution_results: List[SpokeResponse],
    ) -> Dict[str, Any]:
        """実行サマリーを作成"""
        total_actions = len(execution_results)
        successful_actions = sum(1 for result in execution_results if result.success)
        failed_actions = total_actions - successful_actions

        # 全体の成功率を計算
        success_rate = successful_actions / total_actions if total_actions > 0 else 0

        # 実行ステータスを決定
        if success_rate == 1.0:
            overall_status = "completed"
        elif success_rate > 0.5:
            overall_status = "partially_completed"
        elif success_rate > 0:
            overall_status = "mostly_failed"
        else:
            overall_status = "failed"

        # 主要な結果データを抽出
        results_data = []
        for i, result in enumerate(execution_results):
            action = (
                operator_response.actions[i]
                if i < len(operator_response.actions)
                else None
            )
            results_data.append(
                {
                    "action_type": action.action_type if action else "unknown",
                    "success": result.success,
                    "description": action.description if action else "Unknown action",
                    "data_available": result.data is not None,
                    "error": result.error,
                    "data": (
                        result.data
                        if result.success and result.data is not None
                        else None
                    ),
                }
            )

        # ユーザーの元の質問に対する適切な返答を生成
        results_text = llm_chat_completions(
            prompts=[
                {
                    "role": "system",
                    "content": """あなたは親切で知識豊富なAIアシスタントです。ユーザーの質問に対して実行した処理の結果を基に、自然で分かりやすい日本語で直接的な回答をしてください。

重要なガイドライン：
- ユーザーの元の質問に対する明確で具体的な回答を提供する
- 実行結果から得られた情報を整理して分かりやすく提示する
- 成功した場合は結果を具体的に示し、失敗した場合は理由と対処法を説明する
- 技術的な詳細は避け、ユーザーにとって価値のある情報に焦点を当てる
- 自然で親しみやすい口調で、簡潔かつ明確に回答する
- JSON形式ではなく、自然な文章で回答する""",
                },
                {
                    "role": "user",
                    "content": f"""ユーザーの質問: "{prompt}"

実行した処理の結果:
- 実行したアクション数: {total_actions}
- 成功したアクション: {successful_actions}
- 失敗したアクション: {failed_actions}
- 全体のステータス: {overall_status}
- 処理の信頼度: {operator_response.confidence}

オペレーターの分析: {operator_response.analysis}

各アクションの詳細結果:
{chr(10).join([f"- {item['action_type']}: {'成功' if item['success'] else '失敗'} - {item['description']}" + (f" (エラー: {item['error']})" if item['error'] else "") for item in results_data])}

実際に取得されたデータ:
{chr(10).join([f"- {item['description']}: {item['data']}" for item in results_data if item['success'] and item['data'] is not None])}

この情報を基に、ユーザーの質問「{prompt}」に対する適切で自然な返答を生成してください。ユーザーが求めている具体的な情報や回答を中心に、分かりやすく説明してください。""",
                },
            ],
            temperature=0.7,
            max_tokens=800,
        )

        return {
            "total_actions": total_actions,
            "successful_actions": successful_actions,
            "failed_actions": failed_actions,
            "success_rate": round(success_rate, 2),
            "overall_status": overall_status,
            "confidence": operator_response.confidence,
            "results_data": results_data,
            "results_text": results_text,
        }
