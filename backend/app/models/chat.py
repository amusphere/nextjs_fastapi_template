from datetime import datetime

from pydantic import BaseModel


class ChatRequestModel(BaseModel):
    prompt: str


class ChatResponseModel(BaseModel):
    response: str


class ChatMessageModel(BaseModel):
    id: int
    role: str
    content: str
    created_at: float

    @property
    def created_at_dt(self) -> datetime:
        return datetime.fromtimestamp(self.created_at)


class ChatHistoryResponseModel(BaseModel):
    total: int
    messages: list[ChatMessageModel]
