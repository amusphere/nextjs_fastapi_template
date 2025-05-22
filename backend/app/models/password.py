from pydantic import BaseModel


class PasswordResetRequestModel(BaseModel):
    email: str


class PasswordResetModel(BaseModel):
    token: str
    new_password: str
