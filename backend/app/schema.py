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
    token_hash: str = Field(index=True)
    created_at: float = Field(default_factory=lambda: datetime.now().timestamp())
    expires_at: float

    user_id: int = Field(foreign_key="users.id")
    user: User = Relationship(back_populates="password_reset_tokens")


class ChatMessage(SQLModel, table=True):
    """チャット履歴の1メッセージ（ユーザ/アシスタント両方）。"""

    __tablename__ = "chat_messages"
    __table_args__ = {"extend_existing": True}

    id: int | None = Field(default=None, primary_key=True)
    created_at: float = Field(
        default_factory=lambda: datetime.now().timestamp(), index=True
    )

    role: str = Field(index=True)  # "user" | "assistant"
    content: str

    user_id: int = Field(foreign_key="users.id", index=True)
    user: User | None = Relationship()


metadata = SQLModel.metadata
