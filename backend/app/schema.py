from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id: int | None = Field(default=None, primary_key=True)
    uuid: UUID = Field(default_factory=uuid4, index=True)
    created_at: float = Field(default_factory=lambda: datetime.now().timestamp())
    email: str | None = Field(nullable=True, index=True)
    password: str | None = Field(nullable=True)
    name: str | None = Field(nullable=True)
    clerk_sub: str = Field(nullable=True, unique=True, index=True)


metadata = SQLModel.metadata  # SQLModel metadata
