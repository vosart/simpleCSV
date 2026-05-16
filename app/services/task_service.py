from app.domain.task import Task
from app.models import TaskCreateDTO

class TaskService:
  
  def get(self, file_id: str) -> Task | None:
    