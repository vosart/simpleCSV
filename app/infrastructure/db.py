import logging
from contextlib import contextmanager
from collections.abc import Generator
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.infrastructure.orm import Base, TaskORM
from app.models import TaskModel, TaskStatus

BASE_DIR = Path(__file__).resolve().parent.parent
DB_NAME = BASE_DIR / "simpleCSV.db"
DATABASE_URL = f"sqlite:///{DB_NAME}"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
SessionLocal = sessionmaker(bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    Base.metadata.create_all(engine)
    logging.info(f"[DB] initialized at {DB_NAME}")


def create_task(
    file_id: str,
    input_path: str,
    output_path: str,
    status: str = "processing",
    error: str | None = None,
) -> TaskModel:
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_db() as session:
        task = TaskORM(
            file_id=file_id,
            status=status,
            error=error,
            input_path=input_path,
            output_path=output_path,
            created_at=created_at,
            attempts=0,
        )
        session.add(task)
    result = get_task(file_id)
    if result is None:
        raise RuntimeError(f"Task was not found after creation: {file_id}")
    return result


def update_task(
    file_id: str,
    status: str,
    error: str | None = None,
    output_path: str | None = None,
):
    with get_db() as session:
        row = session.get(TaskORM, file_id)
        if row:
            row.status = status
            row.error = error
            if output_path is not None:
                row.output_path = output_path


def increment_attempts(file_id: str) -> int:
    with get_db() as session:
        row = session.get(TaskORM, file_id)
        if not row:
            raise ValueError(f"Task not found: {file_id}")
        row.attempts = (row.attempts or 0) + 1
        session.flush()
        return int(row.attempts)


def get_task(file_id: str) -> TaskModel | None:
    with get_db() as session:
        row = session.get(TaskORM, file_id)
        if not row:
            return None
        return TaskModel.model_validate(row)


def get_tasks(status: str | None = None, limit: int = 50, offset: int = 0) -> list[TaskModel]:
    limit = min(limit, 100)
    offset = min(offset, 10000)
    with get_db() as session:
        query = session.query(TaskORM)
        if status is not None:
            query = query.filter(TaskORM.status == status)
        rows = (
            query.order_by(TaskORM.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return [TaskModel.model_validate(row) for row in rows]


def delete_task(file_id: str) -> bool:
    with get_db() as session:
        row = session.get(TaskORM, file_id)
        if row:
            session.delete(row)
            return True
    return False


def get_old_tasks(days: int) -> list[dict]:
    cleanup_statuses = [TaskStatus.done.value, TaskStatus.failed.value]
    old_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    with get_db() as session:
        rows = (
            session.query(TaskORM)
            .filter(
                TaskORM.created_at < old_date,
                TaskORM.status.in_(cleanup_statuses),
            )
            .order_by(TaskORM.created_at)
            .limit(100)
            .all()
        )
        return [
            {
                "file_id": r.file_id,
                "input_path": r.input_path,
                "output_path": r.output_path,
            }
            for r in rows
        ]


def cleanup_old_tasks(days: int):
    rows = get_old_tasks(days)

    for task in rows:
        file_id = task["file_id"]
        input_ok = False
        output_ok = False
        db_ok = False

        input_path = Path(task["input_path"])
        output_path = Path(task["output_path"])

        try:
            if input_path.exists():
                input_path.unlink()
            input_ok = True
        except Exception:
            logging.exception(f"[CLEANUP][INPUT] file_id={file_id}")

        try:
            if output_path.exists():
                output_path.unlink()
            output_ok = True
        except Exception:
            logging.exception(f"[CLEANUP][OUTPUT] file_id={file_id}")

        try:
            with get_db() as session:
                row = session.get(TaskORM, file_id)
                if row:
                    session.delete(row)
                    db_ok = True
                else:
                    logging.warning(f"[CLEANUP][DB] nothing deleted file_id={file_id}")
        except Exception:
            logging.exception(f"[CLEANUP][DB] file_id={file_id}")

        logging.info(
            f"[CLEANUP] file_id={file_id} "
            f"input={input_ok} output={output_ok} db={db_ok}"
        )
