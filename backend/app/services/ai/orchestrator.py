import os
from typing import Any, Dict, List, Optional

from sqlmodel import Session

from .executor import execute_operator_response
from .models import OperatorResponse, SpokeResponse
from .operator import OperatorHub


class AIOrchestrator:
    """AIアシスタントのオーケストレーター（統合レイヤー）"""

    def __init__(
        self,
        encryption_key: Optional[str] = None,
        session: Optional[Session] = None,
    ):
        self.encryption_key = encryption_key or os.getenv("ENCRYPTION_KEY", "")
        self.session = session
        self.operator_hub = OperatorHub(self.encryption_key, session)

    async def process_request(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """ユーザーリクエストを処理して結果を返す

        Args:
            prompt: ユーザーのプロンプト
            max_tokens: LLMの最大トークン数
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
                await self.operator_hub.analyze_prompt(
                    prompt=prompt, max_tokens=max_tokens, temperature=temperature
                )
            )

            # Step 2: アクション計画を実行
            execution_results: List[SpokeResponse] = await execute_operator_response(
                operator_response=operator_response,
                encryption_key=self.encryption_key,
                session=self.session,
            )

            # Step 3: 実行結果をサマリー
            summary = self._create_execution_summary(
                operator_response, execution_results
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
                }
            )

        return {
            "total_actions": total_actions,
            "successful_actions": successful_actions,
            "failed_actions": failed_actions,
            "success_rate": round(success_rate, 2),
            "overall_status": overall_status,
            "confidence": operator_response.confidence,
            "results_data": results_data,
        }


async def process_ai_request(
    prompt: str,
    max_tokens: int = 1000,
    temperature: float = 0.7,
    encryption_key: Optional[str] = None,
    session: Optional[Session] = None,
) -> Dict[str, Any]:
    """AIリクエストを処理する便利関数

    Args:
        prompt: ユーザーのプロンプト
        max_tokens: LLMの最大トークン数
        temperature: LLMの温度パラメータ
        encryption_key: 暗号化キー
        session: データベースセッション

    Returns:
        処理結果の辞書
    """
    orchestrator = AIOrchestrator(encryption_key, session)
    return await orchestrator.process_request(prompt, max_tokens, temperature)
