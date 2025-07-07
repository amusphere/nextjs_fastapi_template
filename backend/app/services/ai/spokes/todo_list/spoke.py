from app.repositories.todo_list import (
    complete_todo_list,
    create_todo_list,
    delete_todo_list,
    find_todo_list,
    incomplete_todo_list,
    update_todo_list,
)
from app.services.ai.models import SpokeResponse
from app.services.ai.spokes.spoke_interface import BaseSpoke


class TodoListSpoke(BaseSpoke):
    """Manage ToDo List Spoke"""

    def _todo_to_dict(self, todo) -> dict:
        """Convert ToDo object to dictionary for JSON serialization"""
        return {
            "uuid": str(todo.uuid),
            "title": todo.title,
            "description": todo.description,
            "completed": todo.completed,
            "expires_at": todo.expires_at,
            "created_at": todo.created_at,
            "updated_at": todo.updated_at,
        }

    async def action_get_incomplete_todo_list(self, _: dict) -> SpokeResponse:
        """Get all incomplete ToDo lists for a user."""
        try:
            todo_lists = find_todo_list(
                session=self.session,
                user_id=self.current_user.id,
                completed=False,
            )
            # Convert to dict for JSON serialization
            todo_data = [self._todo_to_dict(todo) for todo in todo_lists]
            return SpokeResponse(success=True, data=todo_data)
        except Exception as e:
            return SpokeResponse(
                success=False, error=f"Error getting incomplete todos: {str(e)}"
            )

    async def action_get_completed_todo_list(self, _: dict) -> SpokeResponse:
        """Get all completed ToDo lists for a user."""
        try:
            todo_lists = find_todo_list(
                session=self.session,
                user_id=self.current_user.id,
                completed=True,
            )
            # Convert to dict for JSON serialization
            todo_data = [self._todo_to_dict(todo) for todo in todo_lists]
            return SpokeResponse(success=True, data=todo_data)
        except Exception as e:
            return SpokeResponse(
                success=False, error=f"Error getting completed todos: {str(e)}"
            )

    async def action_search_todo_list_more_than_expires_at(
        self, parameters: dict
    ) -> SpokeResponse:
        """Search ToDo lists that expire after a certain timestamp."""
        try:
            expires_at = parameters["expires_at"]
            todo_lists = find_todo_list(
                session=self.session,
                user_id=self.current_user.id,
                completed=False,
                expires_at=expires_at,
            )
            # Convert to dict for JSON serialization
            todo_data = [self._todo_to_dict(todo) for todo in todo_lists]
            return SpokeResponse(success=True, data=todo_data)
        except Exception as e:
            return SpokeResponse(
                success=False, error=f"Error searching todos: {str(e)}"
            )

    async def action_add_todo_list(self, parameters: dict) -> SpokeResponse:
        """Add a new ToDo list."""
        try:
            title = parameters["title"]
            description = parameters.get("description")
            expires_at = parameters.get("expires_at")

            todo = create_todo_list(
                session=self.session,
                user_id=self.current_user.id,
                title=title,
                description=description,
                expires_at=expires_at,
            )

            # Convert to dict for JSON serialization
            todo_data = self._todo_to_dict(todo)
            return SpokeResponse(success=True, data=todo_data)
        except Exception as e:
            return SpokeResponse(success=False, error=f"Error adding todo: {str(e)}")

    async def action_to_complete_todo_list(self, parameters: dict) -> SpokeResponse:
        """Mark a ToDo list as completed."""
        try:
            todo_list_id = parameters["todo_list_id"]
            todo = complete_todo_list(
                session=self.session,
                id=todo_list_id,
            )

            # Convert to dict for JSON serialization
            todo_data = self._todo_to_dict(todo)
            return SpokeResponse(success=True, data=todo_data)
        except Exception as e:
            return SpokeResponse(
                success=False, error=f"Error completing todo: {str(e)}"
            )

    async def action_to_incomplete_todo_list(self, parameters: dict) -> SpokeResponse:
        """Mark a ToDo list as incomplete."""
        try:
            todo_list_id = parameters["todo_list_id"]
            todo = incomplete_todo_list(
                session=self.session,
                id=todo_list_id,
            )

            # Convert to dict for JSON serialization
            todo_data = self._todo_to_dict(todo)
            return SpokeResponse(success=True, data=todo_data)
        except Exception as e:
            return SpokeResponse(
                success=False, error=f"Error marking todo as incomplete: {str(e)}"
            )

    async def action_update_user_todo_list(self, parameters: dict) -> SpokeResponse:
        """Update a ToDo list."""
        try:
            todo_list_id = parameters["todo_list_id"]
            title = parameters.get("title")
            description = parameters.get("description")
            expires_at = parameters.get("expires_at")

            todo = update_todo_list(
                session=self.session,
                id=todo_list_id,
                title=title,
                description=description,
                expires_at=expires_at,
            )

            # Convert to dict for JSON serialization
            todo_data = self._todo_to_dict(todo)
            return SpokeResponse(success=True, data=todo_data)
        except Exception as e:
            return SpokeResponse(success=False, error=f"Error updating todo: {str(e)}")

    async def action_delete_user_todo_list(self, parameters: dict) -> SpokeResponse:
        """Delete a ToDo list."""
        try:
            todo_list_id = parameters["todo_list_id"]
            delete_todo_list(session=self.session, id=todo_list_id)
            return SpokeResponse(success=True, data={"deleted_todo_id": todo_list_id})
        except ValueError as e:
            return SpokeResponse(success=False, error=f"Todo not found: {str(e)}")
        except Exception as e:
            return SpokeResponse(success=False, error=f"Error deleting todo: {str(e)}")
