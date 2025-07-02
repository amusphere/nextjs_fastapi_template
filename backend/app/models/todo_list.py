from pydantic import BaseModel


class TodoListModel(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False
