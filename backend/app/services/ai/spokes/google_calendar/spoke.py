from datetime import datetime
from typing import Any, Dict, Optional

from app.services.ai.models import SpokeResponse
from app.services.ai.spokes.spoke_interface import BaseSpoke
from app.services.google_oauth import GoogleOauthService
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlmodel import Session


class GoogleCalendarSpoke(BaseSpoke):
    """Google Calendar操作を提供するスポーク"""

    def __init__(self, session: Optional[Session] = None):
        super().__init__(session=session)
        try:
            self.oauth_service = GoogleOauthService(session)
        except ValueError as e:
            # 環境変数が設定されていない場合の処理
            self.oauth_service = None
            self._initialization_error = str(e)

    def _get_calendar_service(self, user_id: int):
        """Google Calendar APIサービスを取得"""
        if self.oauth_service is None:
            raise ValueError(f"Google OAuth Service initialization failed: {getattr(self, '_initialization_error', 'Unknown error')}")

        credentials = self.oauth_service.get_credentials(user_id)
        if not credentials:
            raise ValueError("Google認証情報が見つかりません")
        return build("calendar", "v3", credentials=credentials)

    async def execute_action(
        self, action_type: str, parameters: Dict[str, Any]
    ) -> SpokeResponse:
        """アクションを実行する"""
        try:
            # アクション名をメソッド名に変換 (例: get_calendar_events -> action_get_calendar_events)
            method_name = f"action_{action_type}"

            # メソッドが存在するかチェック
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                if callable(method):
                    return await method(parameters)

            return SpokeResponse(
                success=False, error=f"Unsupported action type: {action_type}"
            )

        except Exception as e:
            return SpokeResponse(
                success=False, error=f"Error executing action {action_type}: {str(e)}"
            )

    @classmethod
    def get_supported_actions(cls) -> list[str]:
        """このスポークがサポートするアクションタイプのリストを返す"""
        # action_で始まるメソッドを自動的に検出
        actions = []
        for attr_name in dir(cls):
            if attr_name.startswith("action_") and callable(getattr(cls, attr_name)):
                # action_プレフィックスを除去してアクション名を取得
                action_name = attr_name[7:]  # "action_"の長さは7文字
                actions.append(action_name)
        return sorted(actions)  # ソートして一貫性を保つ

    # =================
    # アクション関数群
    # =================

    async def action_get_calendar_events(
        self, parameters: Dict[str, Any]
    ) -> SpokeResponse:
        """カレンダーイベント取得アクション"""
        try:
            # パラメータから日付を解析
            start_date = datetime.fromisoformat(
                parameters["start_date"].replace("Z", "+00:00")
            )
            end_date = datetime.fromisoformat(
                parameters["end_date"].replace("Z", "+00:00")
            )
            calendar_id = parameters.get("calendar_id", "primary")
            max_results = parameters.get("max_results", 100)

            # Google Calendar APIサービスを取得
            service = self._get_calendar_service(parameters["user_id"])

            # イベントを取得
            events_result = (
                service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=start_date.isoformat(),
                    timeMax=end_date.isoformat(),
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            events = events_result.get("items", [])

            # CalendarEventモデルに変換
            calendar_events = []
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                end = event["end"].get("dateTime", event["end"].get("date"))

                # 日付のみの場合の処理
                if "T" not in start:
                    start += "T00:00:00Z"
                if "T" not in end:
                    end += "T23:59:59Z"

                attendees = []
                if "attendees" in event:
                    attendees = [
                        attendee.get("email", "") for attendee in event["attendees"]
                    ]

                calendar_event = {
                    "id": event.get("id"),
                    "summary": event.get("summary", ""),
                    "description": event.get("description"),
                    "start_time": datetime.fromisoformat(start.replace("Z", "+00:00")),
                    "end_time": datetime.fromisoformat(end.replace("Z", "+00:00")),
                    "location": event.get("location"),
                    "attendees": attendees if attendees else None,
                    "recurrence": event.get("recurrence"),
                }
                calendar_events.append(calendar_event)

            return SpokeResponse(
                success=True,
                data=calendar_events,
                metadata={
                    "total_events": len(calendar_events),
                    "period": f"{start_date.date()} to {end_date.date()}",
                },
            )

        except HttpError as e:
            return SpokeResponse(
                success=False,
                error=f"Google Calendar API error: {e.reason}",
                metadata={"status_code": e.resp.status},
            )
        except ValueError as e:
            return SpokeResponse(success=False, error=f"Authentication error: {str(e)}")
        except Exception as e:
            return SpokeResponse(success=False, error=f"Unexpected error: {str(e)}")

    async def action_create_calendar_event(
        self, parameters: Dict[str, Any]
    ) -> SpokeResponse:
        """カレンダーイベント作成アクション"""
        try:
            service = self._get_calendar_service(parameters["user_id"])
            calendar_id = parameters.get("calendar_id", "primary")

            # イベントデータを構築
            event_body = {
                "summary": parameters["summary"],
                "start": {
                    "dateTime": datetime.fromisoformat(
                        parameters["start_time"].replace("Z", "+00:00")
                    ).isoformat(),
                    "timeZone": "Asia/Tokyo",
                },
                "end": {
                    "dateTime": datetime.fromisoformat(
                        parameters["end_time"].replace("Z", "+00:00")
                    ).isoformat(),
                    "timeZone": "Asia/Tokyo",
                },
            }

            if parameters.get("description"):
                event_body["description"] = parameters["description"]

            if parameters.get("location"):
                event_body["location"] = parameters["location"]

            if parameters.get("attendees"):
                event_body["attendees"] = [
                    {"email": email} for email in parameters["attendees"]
                ]

            if parameters.get("recurrence"):
                event_body["recurrence"] = parameters["recurrence"]

            # イベントを作成
            created_event = (
                service.events()
                .insert(calendarId=calendar_id, body=event_body)
                .execute()
            )

            return SpokeResponse(
                success=True,
                data={
                    "event_id": created_event.get("id"),
                    "html_link": created_event.get("htmlLink"),
                },
                metadata={"calendar_id": calendar_id},
            )

        except HttpError as e:
            return SpokeResponse(
                success=False,
                error=f"Google Calendar API error: {e.reason}",
                metadata={"status_code": e.resp.status},
            )
        except ValueError as e:
            return SpokeResponse(success=False, error=f"Authentication error: {str(e)}")
        except Exception as e:
            return SpokeResponse(success=False, error=f"Unexpected error: {str(e)}")

    async def action_update_calendar_event(
        self, parameters: Dict[str, Any]
    ) -> SpokeResponse:
        """カレンダーイベント更新アクション"""
        try:
            service = self._get_calendar_service(parameters["user_id"])
            calendar_id = parameters.get("calendar_id", "primary")
            event_id = parameters["event_id"]

            # 既存のイベントを取得
            existing_event = (
                service.events().get(calendarId=calendar_id, eventId=event_id).execute()
            )

            # イベントデータを更新
            existing_event["summary"] = parameters["summary"]
            existing_event["start"] = {
                "dateTime": datetime.fromisoformat(
                    parameters["start_time"].replace("Z", "+00:00")
                ).isoformat(),
                "timeZone": "Asia/Tokyo",
            }
            existing_event["end"] = {
                "dateTime": datetime.fromisoformat(
                    parameters["end_time"].replace("Z", "+00:00")
                ).isoformat(),
                "timeZone": "Asia/Tokyo",
            }

            if parameters.get("description") is not None:
                existing_event["description"] = parameters["description"]

            if parameters.get("location") is not None:
                existing_event["location"] = parameters["location"]

            if parameters.get("attendees") is not None:
                existing_event["attendees"] = [
                    {"email": email} for email in parameters["attendees"]
                ]

            if parameters.get("recurrence") is not None:
                existing_event["recurrence"] = parameters["recurrence"]

            # イベントを更新
            updated_event = (
                service.events()
                .update(
                    calendarId=calendar_id,
                    eventId=event_id,
                    body=existing_event,
                )
                .execute()
            )

            return SpokeResponse(
                success=True,
                data={
                    "event_id": updated_event.get("id"),
                    "html_link": updated_event.get("htmlLink"),
                },
                metadata={"calendar_id": calendar_id},
            )

        except HttpError as e:
            return SpokeResponse(
                success=False,
                error=f"Google Calendar API error: {e.reason}",
                metadata={"status_code": e.resp.status},
            )
        except ValueError as e:
            return SpokeResponse(success=False, error=f"Authentication error: {str(e)}")
        except Exception as e:
            return SpokeResponse(success=False, error=f"Unexpected error: {str(e)}")

    async def action_delete_calendar_event(
        self, parameters: Dict[str, Any]
    ) -> SpokeResponse:
        """カレンダーイベント削除アクション"""
        try:
            service = self._get_calendar_service(parameters["user_id"])
            calendar_id = parameters.get("calendar_id", "primary")
            event_id = parameters["event_id"]

            # イベントを削除
            service.events().delete(calendarId=calendar_id, eventId=event_id).execute()

            return SpokeResponse(
                success=True,
                data={"deleted_event_id": event_id},
                metadata={"calendar_id": calendar_id},
            )

        except HttpError as e:
            if e.resp.status == 404:
                return SpokeResponse(
                    success=False,
                    error="Event not found",
                    metadata={"status_code": 404},
                )
            return SpokeResponse(
                success=False,
                error=f"Google Calendar API error: {e.reason}",
                metadata={"status_code": e.resp.status},
            )
        except ValueError as e:
            return SpokeResponse(success=False, error=f"Authentication error: {str(e)}")
        except Exception as e:
            return SpokeResponse(success=False, error=f"Unexpected error: {str(e)}")

    async def action_list_calendars(self, parameters: Dict[str, Any]) -> SpokeResponse:
        """カレンダーリスト取得アクション（新しいアクションの例）"""
        try:
            service = self._get_calendar_service(parameters["user_id"])

            # カレンダーリストを取得
            calendars_result = service.calendarList().list().execute()
            calendars = calendars_result.get("items", [])

            calendar_list = []
            for calendar in calendars:
                calendar_info = {
                    "id": calendar.get("id"),
                    "summary": calendar.get("summary"),
                    "description": calendar.get("description"),
                    "primary": calendar.get("primary", False),
                    "access_role": calendar.get("accessRole"),
                }
                calendar_list.append(calendar_info)

            return SpokeResponse(
                success=True,
                data=calendar_list,
                metadata={"total_calendars": len(calendar_list)},
            )

        except Exception as e:
            return SpokeResponse(
                success=False, error=f"Error listing calendars: {str(e)}"
            )
