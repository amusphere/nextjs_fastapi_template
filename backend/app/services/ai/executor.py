import os
from typing import Any, Dict, List, Optional
from datetime import datetime
from sqlmodel import Session

from .models import (
    ActionType,
    NextAction,
    OperatorResponse,
    SpokeResponse,
    CalendarEventsRequest,
    CalendarEventCreateRequest,
    CalendarEventUpdateRequest,
    CalendarEventDeleteRequest,
    CalendarEvent
)
from .spokes.google_calendar import GoogleCalendarSpoke


class ActionExecutor:
    """アクションを実際に実行するエグゼキューター"""

    def __init__(self, encryption_key: str, session: Optional[Session] = None):
        self.encryption_key = encryption_key
        self.session = session
        self.google_calendar_spoke = GoogleCalendarSpoke(encryption_key, session)

    async def execute_action(self, action: NextAction) -> SpokeResponse:
        """個別のアクションを実行"""
        try:
            if action.action_type == ActionType.GET_CALENDAR_EVENTS:
                return await self._execute_get_calendar_events(action.parameters)

            elif action.action_type == ActionType.CREATE_CALENDAR_EVENT:
                return await self._execute_create_calendar_event(action.parameters)

            elif action.action_type == ActionType.UPDATE_CALENDAR_EVENT:
                return await self._execute_update_calendar_event(action.parameters)

            elif action.action_type == ActionType.DELETE_CALENDAR_EVENT:
                return await self._execute_delete_calendar_event(action.parameters)

            else:
                return SpokeResponse(
                    success=False,
                    error=f"Unknown action type: {action.action_type}"
                )

        except Exception as e:
            return SpokeResponse(
                success=False,
                error=f"Execution error: {str(e)}"
            )

    async def execute_actions(self, actions: List[NextAction]) -> List[SpokeResponse]:
        """複数のアクションを優先度順に実行"""
        # 優先度でソート（数値が小さいほど高優先度）
        sorted_actions = sorted(actions, key=lambda x: x.priority)

        results = []
        for action in sorted_actions:
            result = await self.execute_action(action)
            results.append(result)

            # 重要なエラーが発生した場合は実行を停止
            if not result.success and action.priority == 1:
                break

        return results

    async def _execute_get_calendar_events(self, parameters: Dict[str, Any]) -> SpokeResponse:
        """カレンダーイベント取得を実行"""
        try:
            # パラメータの検証と変換
            user_id = parameters.get("user_id")
            if not user_id:
                return SpokeResponse(
                    success=False,
                    error="user_id is required"
                )

            start_date_str = parameters.get("start_date")
            end_date_str = parameters.get("end_date")

            if not start_date_str or not end_date_str:
                return SpokeResponse(
                    success=False,
                    error="start_date and end_date are required"
                )

            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))

            calendar_id = parameters.get("calendar_id", "primary")
            max_results = parameters.get("max_results", 100)

            request = CalendarEventsRequest(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                calendar_id=calendar_id,
                max_results=max_results
            )

            return await self.google_calendar_spoke.get_events(request)

        except ValueError as e:
            return SpokeResponse(
                success=False,
                error=f"Invalid date format: {str(e)}"
            )
        except Exception as e:
            return SpokeResponse(
                success=False,
                error=f"Parameter error: {str(e)}"
            )

    async def _execute_create_calendar_event(self, parameters: Dict[str, Any]) -> SpokeResponse:
        """カレンダーイベント作成を実行"""
        try:
            user_id = parameters.get("user_id")
            if not user_id:
                return SpokeResponse(
                    success=False,
                    error="user_id is required"
                )

            # 必須フィールドの確認
            summary = parameters.get("summary")
            start_time_str = parameters.get("start_time")
            end_time_str = parameters.get("end_time")

            if not all([summary, start_time_str, end_time_str]):
                return SpokeResponse(
                    success=False,
                    error="summary, start_time, and end_time are required"
                )

            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))

            event = CalendarEvent(
                summary=summary,
                description=parameters.get("description"),
                start_time=start_time,
                end_time=end_time,
                location=parameters.get("location"),
                attendees=parameters.get("attendees"),
                recurrence=parameters.get("recurrence")
            )

            calendar_id = parameters.get("calendar_id", "primary")

            request = CalendarEventCreateRequest(
                user_id=user_id,
                event=event,
                calendar_id=calendar_id
            )

            return await self.google_calendar_spoke.create_event(request)

        except ValueError as e:
            return SpokeResponse(
                success=False,
                error=f"Invalid date format: {str(e)}"
            )
        except Exception as e:
            return SpokeResponse(
                success=False,
                error=f"Parameter error: {str(e)}"
            )

    async def _execute_update_calendar_event(self, parameters: Dict[str, Any]) -> SpokeResponse:
        """カレンダーイベント更新を実行"""
        try:
            user_id = parameters.get("user_id")
            event_id = parameters.get("event_id")

            if not user_id or not event_id:
                return SpokeResponse(
                    success=False,
                    error="user_id and event_id are required"
                )

            # 必須フィールドの確認
            summary = parameters.get("summary")
            start_time_str = parameters.get("start_time")
            end_time_str = parameters.get("end_time")

            if not all([summary, start_time_str, end_time_str]):
                return SpokeResponse(
                    success=False,
                    error="summary, start_time, and end_time are required"
                )

            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))

            event = CalendarEvent(
                summary=summary,
                description=parameters.get("description"),
                start_time=start_time,
                end_time=end_time,
                location=parameters.get("location"),
                attendees=parameters.get("attendees"),
                recurrence=parameters.get("recurrence")
            )

            calendar_id = parameters.get("calendar_id", "primary")

            request = CalendarEventUpdateRequest(
                user_id=user_id,
                event_id=event_id,
                event=event,
                calendar_id=calendar_id
            )

            return await self.google_calendar_spoke.update_event(request)

        except ValueError as e:
            return SpokeResponse(
                success=False,
                error=f"Invalid date format: {str(e)}"
            )
        except Exception as e:
            return SpokeResponse(
                success=False,
                error=f"Parameter error: {str(e)}"
            )

    async def _execute_delete_calendar_event(self, parameters: Dict[str, Any]) -> SpokeResponse:
        """カレンダーイベント削除を実行"""
        try:
            user_id = parameters.get("user_id")
            event_id = parameters.get("event_id")

            if not user_id or not event_id:
                return SpokeResponse(
                    success=False,
                    error="user_id and event_id are required"
                )

            calendar_id = parameters.get("calendar_id", "primary")

            request = CalendarEventDeleteRequest(
                user_id=user_id,
                event_id=event_id,
                calendar_id=calendar_id
            )

            return await self.google_calendar_spoke.delete_event(request)

        except Exception as e:
            return SpokeResponse(
                success=False,
                error=f"Parameter error: {str(e)}"
            )


async def execute_operator_response(
    operator_response: OperatorResponse,
    encryption_key: Optional[str] = None,
    session: Optional[Session] = None
) -> List[SpokeResponse]:
    """オペレーターレスポンスに基づいてアクションを実行

    Args:
        operator_response: オペレーターからの応答
        encryption_key: 暗号化キー
        session: データベースセッション

    Returns:
        List[SpokeResponse]: 各アクションの実行結果
    """
    if not encryption_key:
        encryption_key = os.getenv("ENCRYPTION_KEY", "")

    executor = ActionExecutor(encryption_key, session)
    return await executor.execute_actions(operator_response.actions)
