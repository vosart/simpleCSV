from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.tasks import router as tasks_router
from app.infrastructure.scheduler import start_scheduler, stop_scheduler
from app.infrastructure.db import init_db
from contextlib import asynccontextmanager




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
app.mount("/static", StaticFiles(directory="app/static"), name="static")
