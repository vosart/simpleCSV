from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.api.tasks import router as tasks_router
from app.infrastructure.scheduler import start_scheduler, stop_scheduler
from app.infrastructure.db import init_db
from contextlib import asynccontextmanager
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="Excel Processor API",
    description="API for processing CSV files and generating Excel reports",
    lifespan=lifespan
)

app.include_router(tasks_router)

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
    )


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/task", response_class=HTMLResponse)
async def task_page(request: Request):
    return templates.TemplateResponse(request, "task.html")