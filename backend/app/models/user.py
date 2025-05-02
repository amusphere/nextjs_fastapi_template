from uuid import UUID
from pydantic import BaseModel


class UserModel(BaseModel):
    uuid: UUID
    clerk_sub: str
