from datetime import datetime
from typing import Any, Dict, Optional

from app.services.ai.models import (
    CalendarEvent,
    CalendarEventCreateRequest,
    CalendarEventDeleteRequest,
    CalendarEventsRequest,
    CalendarEventUpdateRequest,
    SpokeResponse,
)
from app.services.ai.spokes.spoke_interface import BaseSpoke
from app.utils.google_calendar import GoogleCalendarService
from googleapiclient.errors import HttpError
from sqlmodel import Session


class GoogleCalendarSpoke(BaseSpoke):
    """Google Calendar操作を提供するスポーク"""

    def __init__(self, encryption_key: str, session: Optional[Session] = None):
        super().__init__(encryption_key, session)
        self.calendar_service = GoogleCalendarService(encryption_key, session)

    async def execute_action(
        self, action_type: str, parameters: Dict[str, Any]
    ) -> SpokeResponse:
        """アクションを実行する"""
        try:
            if action_type == "get_calendar_events":
                # パラメータを検証してリクエストオブジェクトを作成
                request = CalendarEventsRequest(
                    user_id=parameters["user_id"],
                    start_date=datetime.fromisoformat(
                        parameters["start_date"].replace("Z", "+00:00")
                    ),
                    end_date=datetime.fromisoformat(
                        parameters["end_date"].replace("Z", "+00:00")
                    ),
                    calendar_id=parameters.get("calendar_id", "primary"),
                    max_results=parameters.get("max_results", 100),
                )
                return await self.get_events(request)

            elif action_type == "create_calendar_event":
                event = CalendarEvent(
                    summary=parameters["summary"],
                    start_time=datetime.fromisoformat(
                        parameters["start_time"].replace("Z", "+00:00")
                    ),
                    end_time=datetime.fromisoformat(
                        parameters["end_time"].replace("Z", "+00:00")
                    ),
                    description=parameters.get("description"),
                    location=parameters.get("location"),
                    attendees=parameters.get("attendees"),
                    recurrence=parameters.get("recurrence"),
                )
                request = CalendarEventCreateRequest(
                    user_id=parameters["user_id"],
                    event=event,
                    calendar_id=parameters.get("calendar_id", "primary"),
                )
                return await self.create_event(request)

            elif action_type == "update_calendar_event":
                event = CalendarEvent(
                    summary=parameters["summary"],
                    start_time=datetime.fromisoformat(
                        parameters["start_time"].replace("Z", "+00:00")
                    ),
                    end_time=datetime.fromisoformat(
                        parameters["end_time"].replace("Z", "+00:00")
                    ),
                    description=parameters.get("description"),
                    location=parameters.get("location"),
                    attendees=parameters.get("attendees"),
                    recurrence=parameters.get("recurrence"),
                )
                request = CalendarEventUpdateRequest(
                    user_id=parameters["user_id"],
                    event_id=parameters["event_id"],
                    event=event,
                    calendar_id=parameters.get("calendar_id", "primary"),
                )
                return await self.update_event(request)

            elif action_type == "delete_calendar_event":
                request = CalendarEventDeleteRequest(
                    user_id=parameters["user_id"],
                    event_id=parameters["event_id"],
                    calendar_id=parameters.get("calendar_id", "primary"),
                )
                return await self.delete_event(request)

            else:
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
        return [
            "get_calendar_events",
            "create_calendar_event",
            "update_calendar_event",
            "delete_calendar_event",
        ]

    async def get_events(self, request: CalendarEventsRequest) -> SpokeResponse:
        """指定期間のカレンダーイベントを取得"""
        try:
            # Google Calendar APIサービスを取得
            service = self.calendar_service.get_calendar_service(request.user_id)

            # イベントを取得
            events_result = (
                service.events()
                .list(
                    calendarId=request.calendar_id,
                    timeMin=request.start_date.isoformat(),
                    timeMax=request.end_date.isoformat(),
                    maxResults=request.max_results,
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

                calendar_event = CalendarEvent(
                    id=event.get("id"),
                    summary=event.get("summary", ""),
                    description=event.get("description"),
                    start_time=datetime.fromisoformat(start.replace("Z", "+00:00")),
                    end_time=datetime.fromisoformat(end.replace("Z", "+00:00")),
                    location=event.get("location"),
                    attendees=attendees if attendees else None,
                    recurrence=event.get("recurrence"),
                )
                calendar_events.append(calendar_event)

            return SpokeResponse(
                success=True,
                data=calendar_events,
                metadata={
                    "total_events": len(calendar_events),
                    "period": f"{request.start_date.date()} to {request.end_date.date()}",
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

    async def create_event(self, request: CalendarEventCreateRequest) -> SpokeResponse:
        """カレンダーイベントを作成"""
        try:
            service = self.calendar_service.get_calendar_service(request.user_id)

            # イベントデータを構築
            event_body = {
                "summary": request.event.summary,
                "start": {
                    "dateTime": request.event.start_time.isoformat(),
                    "timeZone": "Asia/Tokyo",
                },
                "end": {
                    "dateTime": request.event.end_time.isoformat(),
                    "timeZone": "Asia/Tokyo",
                },
            }

            if request.event.description:
                event_body["description"] = request.event.description

            if request.event.location:
                event_body["location"] = request.event.location

            if request.event.attendees:
                event_body["attendees"] = [
                    {"email": email} for email in request.event.attendees
                ]

            if request.event.recurrence:
                event_body["recurrence"] = request.event.recurrence

            # イベントを作成
            created_event = (
                service.events()
                .insert(calendarId=request.calendar_id, body=event_body)
                .execute()
            )

            return SpokeResponse(
                success=True,
                data={
                    "event_id": created_event.get("id"),
                    "html_link": created_event.get("htmlLink"),
                },
                metadata={"calendar_id": request.calendar_id},
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

    async def update_event(self, request: CalendarEventUpdateRequest) -> SpokeResponse:
        """カレンダーイベントを更新"""
        try:
            service = self.calendar_service.get_calendar_service(request.user_id)

            # 既存のイベントを取得
            existing_event = (
                service.events()
                .get(calendarId=request.calendar_id, eventId=request.event_id)
                .execute()
            )

            # イベントデータを更新
            existing_event["summary"] = request.event.summary
            existing_event["start"] = {
                "dateTime": request.event.start_time.isoformat(),
                "timeZone": "Asia/Tokyo",
            }
            existing_event["end"] = {
                "dateTime": request.event.end_time.isoformat(),
                "timeZone": "Asia/Tokyo",
            }

            if request.event.description is not None:
                existing_event["description"] = request.event.description

            if request.event.location is not None:
                existing_event["location"] = request.event.location

            if request.event.attendees is not None:
                existing_event["attendees"] = [
                    {"email": email} for email in request.event.attendees
                ]

            if request.event.recurrence is not None:
                existing_event["recurrence"] = request.event.recurrence

            # イベントを更新
            updated_event = (
                service.events()
                .update(
                    calendarId=request.calendar_id,
                    eventId=request.event_id,
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
                metadata={"calendar_id": request.calendar_id},
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

    async def delete_event(self, request: CalendarEventDeleteRequest) -> SpokeResponse:
        """カレンダーイベントを削除"""
        try:
            service = self.calendar_service.get_calendar_service(request.user_id)

            # イベントを削除
            service.events().delete(
                calendarId=request.calendar_id, eventId=request.event_id
            ).execute()

            return SpokeResponse(
                success=True,
                data={"deleted_event_id": request.event_id},
                metadata={"calendar_id": request.calendar_id},
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
