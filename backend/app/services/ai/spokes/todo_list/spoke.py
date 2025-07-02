from app.repositories.todo_list import (
    complete_todo_list,
    create_todo_list,
    delete_todo_list,
    find_todo_list,
    incomplete_todo_list,
    update_todo_list,
)
from app.schema import TodoList
from app.services.ai.spokes.spoke_interface import BaseSpoke


class TodoListSpoke(BaseSpoke):
    """Manage ToDo List Spoke"""

    def __init__(self, session):
        super().__init__(session)

    def get_incomplete_todo_list(self, user_id: int) -> list[TodoList]:
        """Get all incomplete ToDo lists for a user."""
        return find_todo_list(
            session=self.session,
            user_id=user_id,
            completed=False,
        )

    def get_completed_todo_list(self, user_id: int) -> list[TodoList]:
        """Get all completed ToDo lists for a user."""
        return find_todo_list(
            session=self.session,
            user_id=user_id,
            completed=True,
        )

    def search_todo_list_more_than_expires_at(
        self,
        user_id: int,
        expires_at: float,
    ) -> list[TodoList]:
        """Search ToDo lists that expire after a certain timestamp."""
        return find_todo_list(
            session=self.session,
            user_id=user_id,
            completed=False,
            expires_at=expires_at,
        )

    def add_todo_list(
        self,
        user_id: int,
        title: str,
        description: str | None = None,
        expires_at: float | None = None,
    ) -> TodoList:
        """Add a new ToDo list."""
        return create_todo_list(
            session=self.session,
            user_id=user_id,
            title=title,
            description=description,
            expires_at=expires_at,
        )

    def to_complete_todo_list(self, todo_list_id: int):
        """Mark a ToDo list as completed."""
        return complete_todo_list(
            session=self.session,
            id=todo_list_id,
        )

    def to_incomplete_todo_list(self, todo_list_id: int):
        """Mark a ToDo list as incomplete."""
        return incomplete_todo_list(
            session=self.session,
            id=todo_list_id,
        )

    def update_user_todo_list(
        self,
        todo_list_id: int,
        title: str | None = None,
        description: str | None = None,
        expires_at: float | None = None,
    ) -> TodoList:
        """Update a ToDo list."""
        return update_todo_list(
            session=self.session,
            id=todo_list_id,
            title=title,
            description=description,
            expires_at=expires_at,
        )

    def delete_user_todo_list(self, todo_list_id: int) -> bool:
        """Delete a ToDo list."""
        try:
            delete_todo_list(session=self.session, id=todo_list_id)
            return True
        except ValueError:
            return False
