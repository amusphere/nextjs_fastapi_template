from app.schema import TodoList
from sqlmodel import Session, select


def find_todo_list(
    session: Session,
    user_id: int,
    completed: bool = False,
    expires_at: float | None = None,
) -> list[TodoList]:
    """Find all ToDo lists for a specific user"""
    stmt = select(TodoList).where(
        TodoList.user_id == user_id,
        TodoList.completed == completed,
    )

    if expires_at is not None:
        stmt = stmt.where(TodoList.expires_at >= expires_at)

    return session.exec(stmt).all()


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
    expires_at: float | None = None,
) -> TodoList:
    """Create a new ToDo list"""
    todo_list = TodoList(
        user_id=user_id,
        title=title,
        description=description,
        expires_at=expires_at,
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
    expires_at: float | None = None,
    completed: bool | None = None,
) -> TodoList:
    """Update an existing ToDo list"""
    todo_list = get_todo_list(session, id)
    if not todo_list:
        raise ValueError("ToDo list not found")

    if title is not None:
        todo_list.title = title
    if description is not None:
        todo_list.description = description
    if expires_at is not None:
        todo_list.expires_at = expires_at
    if completed is not None:
        todo_list.completed = completed

    session.commit()
    session.refresh(todo_list)
    return todo_list


def complete_todo_list(
    session: Session,
    id: int,
) -> TodoList:
    """Mark a ToDo list as completed"""
    return update_todo_list(session, id, completed=True)


def incomplete_todo_list(
    session: Session,
    id: int,
) -> TodoList:
    """Mark a ToDo list as incomplete"""
    return update_todo_list(session, id, completed=False)


def delete_todo_list(
    session: Session,
    id: int,
) -> None:
    """Delete a ToDo list"""
    todo_list = get_todo_list(session, id)
    if not todo_list:
        raise ValueError("ToDo list not found")

    session.delete(todo_list)
    session.commit()
