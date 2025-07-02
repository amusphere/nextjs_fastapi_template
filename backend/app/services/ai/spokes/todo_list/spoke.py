from app.services.ai.spokes.spoke_interface import BaseSpoke


class TodoListSpoke(BaseSpoke):
    """Manage ToDo List Spoke"""

    def __init__(self, session):
        super().__init__(session)

    def search_todo_lists(self, user_id: int):
        """Search ToDo lists for a specific user"""
        from app.repositories.todo_list import find_todo_list_by_user_id

        return find_todo_list_by_user_id(self.session, user_id)
