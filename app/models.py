from pydantic import BaseModel
from enum import Enum


class TaskStatus(str, Enum):
    processing = "processing"
    done = "done"
    failed = "failed"
    retry = "retry"


class TaskModel(BaseModel):
    file_id: str
    status: TaskStatus
    error: str | None = None
    input_path: str
    output_path: str | None = None
    created_at: str
    attempts: int = 0


class TaskListResponse(BaseModel):
    items: list[TaskModel]
    total: int

