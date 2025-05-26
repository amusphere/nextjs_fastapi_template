from typing import List, Optional

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str


class ChatPromptRequest(BaseModel):
    prompt: str
    messages: Optional[List[ChatMessage]] = []
    model: Optional[str] = "gpt-4.1"
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7


class ChatPromptResponse(BaseModel):
    response: str
    model: str
    tokens_used: Optional[int] = None
