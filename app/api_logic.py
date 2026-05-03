from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.infrastructure.scheduler import start_scheduler, stop_scheduler

import logging
import os



logging.basicConfig(level=logging.INFO)

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "files"))
UPLOAD_DIR.mkdir(exist_ok=True)

scheduler_started = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler_started
    if not scheduler_started:
        start_scheduler()
        scheduler_started = True
    yield

    if scheduler_started:
        stop_scheduler()
        scheduler_started = False

app = FastAPI(
    title="Excel Processor API",
    description="API for processing CSV files and generating Excel reports",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="static"), name="static")


def validate_file_extension(filename: str) -> bool:
    """Проверяет, что файл имеет допустимое расширение (.csv)"""
    return filename.lower().endswith('.csv')


async def save_uploaded_file(file: UploadFile, file_path: Path) -> Path:
    """Сохраняет загруженный файл и возвращает путь к нему"""
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

            logging.info(f"[UPLOAD] saved file = {file_path.resolve()}")
            logging.info(f"[UPLOAD] exists? {file_path.exists()}")

            logging.info(f"[UPLOAD] saving to {file_path.resolve()}")
        return file_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")


@app.get("/example.csv")
def example_csv():
    """Возвращает пример CSV файла для тестирования"""
    example_path = UPLOAD_DIR / "example.csv"
    if not example_path.exists():
        raise HTTPException(status_code=404, detail="Example CSV not found")
    return FileResponse(
        example_path,
        filename="example.csv",
        media_type="text/csv"
    )






