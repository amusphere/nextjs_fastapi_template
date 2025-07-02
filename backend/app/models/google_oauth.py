from pydantic import BaseModel


class GoogleAuthUrlResponse(BaseModel):
    auth_url: str


class GoogleCallbackRequest(BaseModel):
    code: str
    state: str


class GoogleAuthResponse(BaseModel):
    success: bool
    message: str
