from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


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

    password_reset_tokens: list["PasswordResetToken"] = Relationship(
        back_populates="user"
    )


class PasswordResetToken(SQLModel, table=True):
    __tablename__ = "password_reset_tokens"
    __table_args__ = {"extend_existing": True}

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    token: str = Field(index=True)
    created_at: float = Field(default_factory=lambda: datetime.now().timestamp())
    expires_at: float

    user: User = Relationship(back_populates="password_reset_tokens")


class PasswordResetToken(SQLModel, table=True):
    __tablename__ = "password_reset_tokens"
    __table_args__ = {"extend_existing": True}

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    token_hash: str = Field(index=True, unique=True)
    expires_at: float
    used: bool = Field(default=False)


metadata = SQLModel.metadata
