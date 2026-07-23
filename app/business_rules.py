"""
Backend-enforced business rules for task status transitions.

The frontend can hide invalid buttons, but a client calling the API
directly (curl, Postman, etc.) must still be blocked by the backend.
This is the single source of truth for which status transitions are legal.
"""

from fastapi import HTTPException, status

from app.models import TaskStatus

# Same -> same is intentionally excluded: no-op transitions are invalid.
VALID_TRANSITIONS: frozenset[tuple[TaskStatus, TaskStatus]] = frozenset(
    {
        (TaskStatus.TODO, TaskStatus.IN_PROGRESS),
        (TaskStatus.IN_PROGRESS, TaskStatus.DONE),
        (TaskStatus.DONE, TaskStatus.IN_PROGRESS),
    }
)


def validate_status_transition(current: TaskStatus, new: TaskStatus) -> None:
    if (current, new) not in VALID_TRANSITIONS:
        allowed = sorted({f"{f.value}->{t.value}" for f, t in VALID_TRANSITIONS})
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Invalid status transition from {current.value} to {new.value}. "
                f"Allowed transitions: {allowed}"
            ),
        )
