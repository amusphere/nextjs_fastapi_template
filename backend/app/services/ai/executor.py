import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlmodel import Session

from .exceptions import ActionExecutionError
from .logger import AIAssistantLogger
from .models import (
    ActionType,
    CalendarEvent,
    CalendarEventCreateRequest,
    CalendarEventDeleteRequest,
    CalendarEventsRequest,
    CalendarEventUpdateRequest,
    NextAction,
    OperatorResponse,
    SpokeResponse,
)
from .spokes.google_calendar.spoke import GoogleCalendarSpoke


class ActionExecutor:
    """アクションを実際に実行するエグゼキューター"""

    def __init__(self, encryption_key: str, session: Optional[Session] = None):
        self.encryption_key = encryption_key
        self.session = session
        self.google_calendar_spoke = GoogleCalendarSpoke(encryption_key, session)
        self.logger = AIAssistantLogger("action_executor")

    async def execute_action(self, action: NextAction) -> SpokeResponse:
        """個別のアクションを実行"""
        start_time = time.time()

        try:
            # アクションタイプに基づいて適切なメソッドを呼び出し
            action_methods = {
                ActionType.GET_CALENDAR_EVENTS: self._execute_get_calendar_events,
                ActionType.CREATE_CALENDAR_EVENT: self._execute_create_calendar_event,
                ActionType.UPDATE_CALENDAR_EVENT: self._execute_update_calendar_event,
                ActionType.DELETE_CALENDAR_EVENT: self._execute_delete_calendar_event,
            }

            method = action_methods.get(action.action_type)
            if not method:
                error_msg = f"Unknown action type: {action.action_type}"
                self.logger.log_action_execution(
                    action_type=action.action_type.value,
                    user_id=action.parameters.get("user_id", 0),
                    success=False,
                    error=error_msg,
                )
                return SpokeResponse(success=False, error=error_msg)

            result = await method(action.parameters)

            # ログ記録
            duration = time.time() - start_time
            self.logger.log_action_execution(
                action_type=action.action_type.value,
                user_id=action.parameters.get("user_id", 0),
                success=result.success,
                duration=duration,
                error=result.error if not result.success else None,
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            error = ActionExecutionError(f"Execution error: {str(e)}")
            self.logger.log_error(
                error,
                {
                    "action_type": action.action_type.value,
                    "user_id": action.parameters.get("user_id", 0),
                    "duration": duration,
                },
            )
            return SpokeResponse(success=False, error=str(error))

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

    def _validate_required_params(
        self, parameters: Dict[str, Any], required_fields: List[str]
    ) -> Optional[str]:
        """必須パラメータを検証"""
        missing_fields = [
            field for field in required_fields if not parameters.get(field)
        ]
        if missing_fields:
            return f"Required fields missing: {', '.join(missing_fields)}"
        return None

    def _parse_datetime(self, datetime_str: str) -> datetime:
        """日時文字列をdatetimeオブジェクトに変換"""
        return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))

    async def _execute_get_calendar_events(
        self, parameters: Dict[str, Any]
    ) -> SpokeResponse:
        """カレンダーイベント取得を実行"""
        try:
            # 必須パラメータの検証
            validation_error = self._validate_required_params(
                parameters, ["user_id", "start_date", "end_date"]
            )
            if validation_error:
                return SpokeResponse(success=False, error=validation_error)

            user_id = parameters["user_id"]
            start_date = self._parse_datetime(parameters["start_date"])
            end_date = self._parse_datetime(parameters["end_date"])
            calendar_id = parameters.get("calendar_id", "primary")
            max_results = parameters.get("max_results", 100)

            request = CalendarEventsRequest(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                calendar_id=calendar_id,
                max_results=max_results,
            )

            return await self.google_calendar_spoke.get_events(request)

        except ValueError as e:
            return SpokeResponse(success=False, error=f"Invalid date format: {str(e)}")
        except Exception as e:
            return SpokeResponse(success=False, error=f"Parameter error: {str(e)}")

    async def _execute_create_calendar_event(
        self, parameters: Dict[str, Any]
    ) -> SpokeResponse:
        """カレンダーイベント作成を実行"""
        try:
            # 必須パラメータの検証
            validation_error = self._validate_required_params(
                parameters, ["user_id", "summary", "start_time", "end_time"]
            )
            if validation_error:
                return SpokeResponse(success=False, error=validation_error)

            user_id = parameters["user_id"]
            start_time = self._parse_datetime(parameters["start_time"])
            end_time = self._parse_datetime(parameters["end_time"])

            event = CalendarEvent(
                summary=parameters["summary"],
                description=parameters.get("description"),
                start_time=start_time,
                end_time=end_time,
                location=parameters.get("location"),
                attendees=parameters.get("attendees"),
                recurrence=parameters.get("recurrence"),
            )

            request = CalendarEventCreateRequest(
                user_id=user_id,
                event=event,
                calendar_id=parameters.get("calendar_id", "primary"),
            )

            return await self.google_calendar_spoke.create_event(request)

        except ValueError as e:
            return SpokeResponse(success=False, error=f"Invalid date format: {str(e)}")
        except Exception as e:
            return SpokeResponse(success=False, error=f"Parameter error: {str(e)}")

    async def _execute_update_calendar_event(
        self, parameters: Dict[str, Any]
    ) -> SpokeResponse:
        """カレンダーイベント更新を実行"""
        try:
            # 必須パラメータの検証
            validation_error = self._validate_required_params(
                parameters, ["user_id", "event_id", "summary", "start_time", "end_time"]
            )
            if validation_error:
                return SpokeResponse(success=False, error=validation_error)

            user_id = parameters["user_id"]
            event_id = parameters["event_id"]
            start_time = self._parse_datetime(parameters["start_time"])
            end_time = self._parse_datetime(parameters["end_time"])

            event = CalendarEvent(
                summary=parameters["summary"],
                description=parameters.get("description"),
                start_time=start_time,
                end_time=end_time,
                location=parameters.get("location"),
                attendees=parameters.get("attendees"),
                recurrence=parameters.get("recurrence"),
            )

            request = CalendarEventUpdateRequest(
                user_id=user_id,
                event_id=event_id,
                event=event,
                calendar_id=parameters.get("calendar_id", "primary"),
            )

            return await self.google_calendar_spoke.update_event(request)

        except ValueError as e:
            return SpokeResponse(success=False, error=f"Invalid date format: {str(e)}")
        except Exception as e:
            return SpokeResponse(success=False, error=f"Parameter error: {str(e)}")

    async def _execute_delete_calendar_event(
        self, parameters: Dict[str, Any]
    ) -> SpokeResponse:
        """カレンダーイベント削除を実行"""
        try:
            # 必須パラメータの検証
            validation_error = self._validate_required_params(
                parameters, ["user_id", "event_id"]
            )
            if validation_error:
                return SpokeResponse(success=False, error=validation_error)

            request = CalendarEventDeleteRequest(
                user_id=parameters["user_id"],
                event_id=parameters["event_id"],
                calendar_id=parameters.get("calendar_id", "primary"),
            )

            return await self.google_calendar_spoke.delete_event(request)

        except Exception as e:
            return SpokeResponse(success=False, error=f"Parameter error: {str(e)}")


async def execute_operator_response(
    operator_response: OperatorResponse,
    encryption_key: Optional[str] = None,
    session: Optional[Session] = None,
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
