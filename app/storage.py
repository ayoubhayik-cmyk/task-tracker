"""
In-memory storage layer for the Task Tracker API.

_tasks holds TaskResponse objects keyed by id. id, created_at, and
updated_at are generated here -- never accepted from client input.
"""

import uuid
from datetime import date, datetime, timezone
from typing import Optional

from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

_tasks: dict[str, TaskResponse] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _compute_overdue(due_date: Optional[date], status: TaskStatus) -> bool:
    """A task is overdue if it has a due date in the past AND is not Done.
    A completed task is never considered overdue, even if it was finished late."""
    if due_date is None or status == TaskStatus.DONE:
        return False
    return due_date < datetime.now(timezone.utc).date()


def add_task(payload: TaskCreate) -> TaskResponse:
    task_id = str(uuid.uuid4())
    timestamp = _now()
    task = TaskResponse(
        id=task_id,
        title=payload.title,
        description=payload.description or "",
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        due_date=payload.due_date,
        tags=payload.tags,
        is_overdue=_compute_overdue(payload.due_date, payload.status),
        created_at=timestamp,
        updated_at=timestamp,
    )
    _tasks[task_id] = task
    return task


def get_all_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    overdue: Optional[bool] = None,
    tag: Optional[str] = None,
) -> list[TaskResponse]:
    results = list(_tasks.values())
    if status is not None:
        results = [t for t in results if t.status == status]
    if priority is not None:
        results = [t for t in results if t.priority == priority]
    if overdue is not None:
        results = [t for t in results if t.is_overdue == overdue]
    if tag is not None:
        results = [t for t in results if tag in t.tags]
    return results


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    existing = _tasks.get(task_id)
    if existing is None:
        return None

    updates = payload.model_dump(exclude_unset=True)
    updated = existing.model_copy(update=updates)
    updated.is_overdue = _compute_overdue(updated.due_date, updated.status)
    updated.updated_at = _now()
    _tasks[task_id] = updated
    return updated


def delete_task(task_id: str) -> bool:
    if task_id in _tasks:
        del _tasks[task_id]
        return True
    return False


def _reset() -> None:
    _tasks.clear()
