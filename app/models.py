from pydantic import BaseModel, Field
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

class ProcessResponse(BaseModel):
  status: TaskStatus
  file_id: str
  download_url: str

class StatsResponse(BaseModel):
  total: int
  done: int
  failed: int
  processing: int

class TaskQueryParams(BaseModel):
  status: TaskStatus | None = None
  limit: int = Field(default=50, ge=1, le=100)
  offset: int = Field(default=0, ge=0, le=10000)

