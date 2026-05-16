from app.domain.task import Task
from app.infrastructure.db import get_task, update_task


class TaskService:
    def get(self, file_id: str) -> Task | None:
        model = get_task(file_id)
        if model is None:
            return None
        return Task(**model.model_dump())

    def retry(self, file_id: str) -> Task:
        task = self.get(file_id)

        if task is None:
            raise ValueError(f"Task is not found: {file_id}")

        if not task.can_retry():
            raise ValueError("Only failed tasks can be retried")

        update_task(file_id, status="processing", error=None)
        updated = self.get(file_id)
        if updated is None:
            raise RuntimeError(f"Task disappeared after update: {file_id}")
        return updated

    def get_for_download(self, file_id: str) -> Task:
          task = self.get(file_id)
          if task is None:
            raise LookupError(f"Task not found: {file_id}")
          if not task.is_done():
            raise ValueError("File is not ready yet")
          return task