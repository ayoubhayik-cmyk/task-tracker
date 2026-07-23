"""
Pydantic v2 data model layer for the Task Tracker API.

Client input models (TaskCreate, TaskUpdate) forbid extra fields and never
accept server-managed fields (id, created_at, updated_at). Those fields are
generated exclusively by the storage layer.
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

MAX_TAGS = 10
MAX_TAG_LENGTH = 30


def _normalize_tags(tags: Optional[list[str]]) -> list[str]:
    if tags is None:
        return []
    normalized: list[str] = []
    for tag in tags:
        cleaned = tag.strip()
        if not cleaned:
            raise ValueError("tags must not be blank or whitespace-only")
        if len(cleaned) > MAX_TAG_LENGTH:
            raise ValueError(f"each tag must be {MAX_TAG_LENGTH} characters or fewer")
        normalized.append(cleaned)
    if len(normalized) > MAX_TAGS:
        raise ValueError(f"a task may have at most {MAX_TAGS} tags")
    return normalized


class TaskStatus(str, Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


def _validate_title(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("title must not be blank or whitespace-only")
    if len(stripped) > 200:
        raise ValueError("title must be 200 characters or fewer")
    return stripped


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    due_date: Optional[date] = None
    tags: list[str] = []

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return _validate_title(value)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str]) -> list[str]:
        return _normalize_tags(value)


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = None
    due_date: Optional[date] = None
    tags: Optional[list[str]] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return _validate_title(value)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: Optional[list[str]]) -> Optional[list[str]]:
        if value is None:
            return value
        return _normalize_tags(value)


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str]
    due_date: Optional[date] = None
    tags: list[str] = []
    is_overdue: bool = False
    created_at: datetime
    updated_at: datetime
