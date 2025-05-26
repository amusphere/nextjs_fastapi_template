from typing import Optional

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str


class ChatPromptRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7


class ChatPromptResponse(BaseModel):
    response: str
    model: str
    tokens_used: Optional[int] = None
