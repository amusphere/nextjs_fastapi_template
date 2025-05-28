from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel


class NextAction(BaseModel):
    """次に実行すべきアクション"""
    action_type: str  # 動的にスポークから読み込まれるアクションタイプ
    parameters: Dict[str, Any]
    priority: int = 1  # 1が最高優先度
    description: str  # アクションの説明


class OperatorResponse(BaseModel):
    """オペレーターからの応答"""
    actions: List[NextAction]
    analysis: str  # プロンプト解析結果の説明
    confidence: float  # 判断の信頼度 (0.0-1.0)


class CalendarEvent(BaseModel):
    """カレンダーイベント"""
    id: Optional[str] = None
    summary: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    attendees: Optional[List[str]] = None
    recurrence: Optional[List[str]] = None


class CalendarEventsRequest(BaseModel):
    """カレンダーイベント取得リクエスト"""
    user_id: int
    start_date: datetime
    end_date: datetime
    calendar_id: str = "primary"
    max_results: int = 100


class CalendarEventCreateRequest(BaseModel):
    """カレンダーイベント作成リクエスト"""
    user_id: int
    event: CalendarEvent
    calendar_id: str = "primary"


class CalendarEventUpdateRequest(BaseModel):
    """カレンダーイベント更新リクエスト"""
    user_id: int
    event_id: str
    event: CalendarEvent
    calendar_id: str = "primary"


class CalendarEventDeleteRequest(BaseModel):
    """カレンダーイベント削除リクエスト"""
    user_id: int
    event_id: str
    calendar_id: str = "primary"


class SpokeResponse(BaseModel):
    """スポークからの応答"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
