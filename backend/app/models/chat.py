from pydantic import BaseModel


class ChatRequestModel(BaseModel):
    prompt: str


class ChatResponseModel(BaseModel):
    response: str
