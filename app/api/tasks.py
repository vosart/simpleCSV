from itertools import count

from fastapi import (
    APIRouter,
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    BackgroundTasks,
    Depends,
)
from fastapi.responses import FileResponse
from pathlib import Path
from app.infrastructure.db import (
    create_task,
    delete_task,
    init_db,
    get_tasks,
)
from app.services.processor import process_in_background
from app.api_logic import validate_file_extension, save_uploaded_file, lifespan
from app.models import (
    TaskModel,
    TaskListResponse,
    ProcessResponse,
    StatsResponse,
    TaskQueryParams,
    TaskStatus,
    TaskCreateDTO,
    TaskResponseDTO,
)
from app.services.task_service import TaskService
import os
import uuid


BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "files"))
UPLOAD_DIR.mkdir(exist_ok=True)


router = APIRouter()


@router.post("/process_csv", response_model=ProcessResponse)
async def process_csv(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename or validate_file_extension(file.filename):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    if background_tasks is None:
        raise HTTPException(status_code=500, detail="BackgroundTasks not provided")

    # Генерация уникального ID для задачи
    file_id = str(uuid.uuid4())
    input_path = UPLOAD_DIR / f"{file_id}.csv"
    output_path = UPLOAD_DIR / f"{file_id}.xlsx"

    await save_uploaded_file(file, input_path)
    create_task(file_id, str(input_path), str(output_path))

    # Добавляем задачу в background
    background_tasks.add_task(process_in_background, input_path, output_path, file_id)

    return {
        "status": "processing",
        "file_id": file_id,
        "download_url": f"/download/{file_id}",
    }


@router.get("/download/{file_id}")
def download_file(file_id: str):
    """Скачивание готового Excel файла"""
    file_path = UPLOAD_DIR / f"{file_id}.xlsx"
    task = get_task(file_id)
    if not task:
        raise HTTPException(404, "Task not found")
    if task.status != TaskStatus.done:
        raise HTTPException(400, "File yet not ready")

    return FileResponse(
        file_path,
        filename=f"{file_id}.xlsx",
        media_type="routerlication/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.get("/status/{file_id}", response_model=TaskResponseDTO)
def check_status(file_id: str):
    """Проверка статуса задачи"""
    task = get_task(file_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task


@router.get("/tasks", response_model=TaskListResponse)
def list_tasks(params: TaskQueryParams = Depends()):
    tasks = get_tasks(params.status, params.limit, params.offset)
    total = len(get_tasks(params.status))
    return TaskListResponse(
        items=[TaskResponseDTO.model_validate(t) for t in tasks], total=total
    )


@router.get("/tasks/all")
def list_all_tasks():
    tasks = get_tasks(limit=1000, offset=0)

    return {"tasks": tasks, "total": len(tasks)}


@router.post("/tasks/{file_id}/retry")
def retry_task(file_id: str, background_tasks: BackgroundTasks):
    service = TaskService()
    try:
        task = service.retry(file_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
    if not task.output_path:
        raise HTTPException(status_code=400, detail="Task has no output path")

    background_tasks.add_task(
        process_in_background,
        Path(task.input_path),
        Path(task.output_path),
        file_id,
    )
    return {"status": "restarted", "file_id": file_id}


@router.get("/tasks/stats", response_model=StatsResponse)
def tasks_stats():
    tasks = get_tasks()
    return StatsResponse(
        total=len(tasks),
        done=sum(t.status == TaskStatus.done for t in tasks),
        failed=sum(t.status == TaskStatus.failed for t in tasks),
        processing=sum(t.status == TaskStatus.processing for t in tasks),
    )


@router.get("/tasks/{file_id}", response_model=TaskResponseDTO)
def get_task_detail(file_id: str):
    task = get_task(file_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/tasks/{file_id}")
def delete_task_api(file_id: str):
    delete_task(file_id)
    return {"status": "deleted"}
