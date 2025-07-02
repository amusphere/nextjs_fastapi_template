from app.schema import TodoList
from sqlmodel import Session


def find_todo_list_by_user_id(
    session: Session,
    user_id: int,
) -> list[TodoList]:
    """Find all ToDo lists for a specific user"""
    todo_lists = session.query(TodoList).filter(TodoList.user_id == user_id).all()
    return todo_lists


def get_todo_list(
    session: Session,
    id: int,
) -> TodoList | None:
    """Get a ToDo list by ID"""
    todo_list = session.get(TodoList, id)
    if not todo_list:
        return None
    return todo_list


def create_todo_list(
    session: Session,
    user_id: int,
    title: str,
    description: str | None = None,
) -> TodoList:
    """Create a new ToDo list"""
    todo_list = TodoList(
        user_id=user_id,
        title=title,
        description=description,
    )
    session.add(todo_list)
    session.commit()
    session.refresh(todo_list)
    return todo_list


def update_todo_list(
    session: Session,
    id: int,
    title: str | None = None,
    description: str | None = None,
) -> TodoList:
    """Update an existing ToDo list"""
    todo_list = get_todo_list(session, id)
    if not todo_list:
        raise ValueError("ToDo list not found")

    if title is not None:
        todo_list.title = title
    if description is not None:
        todo_list.description = description

    session.commit()
    session.refresh(todo_list)
    return todo_list


def complete_todo_list(
    session: Session,
    id: int,
) -> TodoList:
    """Mark a ToDo list as completed"""
    todo_list = get_todo_list(session, id)
    if not todo_list:
        raise ValueError("ToDo list not found")

    todo_list.completed = True
    session.commit()
    session.refresh(todo_list)
    return todo_list


def incomplete_todo_list(
    session: Session,
    id: int,
) -> TodoList:
    """Mark a ToDo list as incomplete"""
    todo_list = get_todo_list(session, id)
    if not todo_list:
        raise ValueError("ToDo list not found")

    todo_list.completed = False
    session.commit()
    session.refresh(todo_list)
    return todo_list
