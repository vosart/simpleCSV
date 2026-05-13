from dataclasses import dataclass
from app.models import TaskStatus

@dataclass
class Task:
  file_id: str
  status: TaskStatus
  input_path: str
  output_path: str | None
  error: str | None
  created_at: str
  attempts: int

  def can_retry(self) -> bool:
    pass

  def is_done(self) -> bool:
    pass
