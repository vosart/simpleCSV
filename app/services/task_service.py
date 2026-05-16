from app.domain.task import Task
from app.models import TaskCreateDTO
from app.infrastructure.db import get_task, update_task

class TaskService:
  
  def get(self, file_id: str) -> Task | None:
    model = get_task(file_id)  
    if model is None:
      return None
    return Task(
      
    )