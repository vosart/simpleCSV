from pydantic import BaseModel
from enum import Enum

class TaskStatus(Enum):
  "processing"
  "done"
  "failed"
  "retry"

class TaskModel(BaseModel):
  file_id: str
  status: str
  error: str | None = None
  input_path: str
  output_path: str | None = None
  created_at: str
  attempts: int

class TaskListResponse(BaseModel):
  items: list[TaskModel]
  total: int

  