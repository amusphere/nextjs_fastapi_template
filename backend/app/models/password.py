from pydantic import BaseModel


class PasswordResetRequestModel(BaseModel):
    email: str


class PasswordResetModel(BaseModel):
    token: str
    new_password: str


class PasswordChangeModel(BaseModel):
    current_password: str
    new_password: str
