from genericpath import exists
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from app.core.constants import CLEANUP_STATUSES
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_NAME = BASE_DIR / "simpleCSV.db"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

@contextmanager
def get_db():
    logging.info(f"[DB] using db path = {Path(DB_NAME).resolve()}")
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.execute("""
                       CREATE TABLE IF NOT EXISTS tasks (
                           file_id          TEXT PRIMARY KEY,
                           status           TEXT,
                           error            TEXT,
                           input_path       TEXT,
                           output_path      TEXT,
                           created_at       TEXT    DEFAULT CURRENT_TIMESTAMP
                       )

                       """)
        try:
            conn.execute("ALTER TABLE tasks ADD COLUMN attempts INTEGER DEFAULT 0")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                logging.info("[DB] attempts column already exists")
                pass
            else:
                raise



def create_task(
    file_id: str,
    input_path: str,
    output_path: str,
    status="processing",
    error: str = None
    ):

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_db() as conn:
        conn.execute("""
                       INSERT INTO tasks (
                           file_id,
                           status,
                           error,
                           input_path,
                           output_path,
                           created_at)
                       VALUES (?, ?, ?, ?, ?, ?)

                       """, (
                           file_id,
                           status,
                           error,
                           input_path,
                           output_path,
                           created_at
                           )
                       )

    return get_task(file_id)

def update_task(
    file_id: str,
    status: str,
    error: str = None,
    output_path: str = None,
    ):

    with get_db() as conn:
        conn.execute("""
                    UPDATE tasks
                    SET status = ?, error = ?, output_path = ?
                    WHERE file_id = ?
                    """, (status, error, output_path, file_id))


def increment_attempts(file_id: str):
    with get_db() as conn:
        cursor = conn.execute(
            "UPDATE tasks SET attempts = attempts + 1 WHERE file_id = ?",
            (file_id,)
        )

        if cursor.rowcount == 0:
            raise ValueError(f"Task not found {file_id}")

        cursor = conn.execute("SELECT attempts FROM tasks WHERE file_id = ?",
                              (file_id,)
        )
        return cursor.fetchone()[0]

def get_task(file_id: str):
    with get_db() as conn:
        cursor = conn.execute("""
                       SELECT * FROM tasks WHERE file_id = ?
                       """, (file_id, ))

        row = cursor.fetchone()

    if not row:
        return {}

    return dict(row)

def get_tasks(status: str = None, limit: int = 50, offset: int = 0):
    limit = min(limit, 100)
    offset = min(offset, 10000)
    with get_db() as conn:
        if status is not None:
            cursor = conn.execute("""
                                SELECT COUNT(*)
                                FROM tasks
                                WHERE status = ?
                                """, (status,))
            total = cursor.fetchone()[0]
            cursor = conn.execute("""
                                  SELECT * FROM tasks
                                  WHERE status = ?
                                  ORDER BY CREATED_AT
                                  DESC LIMIT ? OFFSET ?""", (status, limit, offset))
            rows = cursor.fetchall()

        else:
            cursor = conn.execute("SELECT COUNT(*) FROM tasks")
            total = cursor.fetchone()[0]
            cursor = conn.execute("""
                                  SELECT * FROM tasks
                                  ORDER BY CREATED_AT
                                  DESC LIMIT ? OFFSET ?""", (limit, offset))
            rows = cursor.fetchall()

    return [dict(row) for row in rows]

def delete_task(file_id: str):
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM tasks WHERE file_id = ?", (file_id,))

    return cursor.rowcount > 0

def get_old_tasks(days: int) -> list:
    if not CLEANUP_STATUSES:
        return []
    old_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    placeholders = ", ".join(["?"] * len(CLEANUP_STATUSES))
    with get_db() as conn:
        cursor = conn.execute(f"""
                              SELECT file_id, input_path, output_path FROM tasks
                              WHERE created_at < ?
                              AND status IN ({placeholders})
                              ORDER BY created_at ASC
                              LIMIT 100
                              """, (old_date, *CLEANUP_STATUSES))
        rows = cursor.fetchall()
    return [dict(row) for row in rows]

def cleanup_old_tasks(days: int):
    rows = get_old_tasks(days)

    for task in rows:
        file_id = task["file_id"]

        input_ok = False
        output_ok = False
        db_ok = False

        input_path = Path(task["input_path"])
        output_path = Path(task["output_path"])

        # --- FILES ---
        try:
            if input_path.exists():
                input_path.unlink()
                input_ok = True
            else:
                input_ok = True  # уже удалён = тоже OK

        except Exception:
            logging.exception(f"[CLEANUP][INPUT] file_id={file_id}")

        try:
            if output_path.exists():
                output_path.unlink()
                output_ok = True
            else:
                output_ok = True

        except Exception:
            logging.exception(f"[CLEANUP][OUTPUT] file_id={file_id}")

        # --- DB ---
        try:
            with get_db() as conn:
                cursor = conn.execute(
                    "DELETE FROM tasks WHERE file_id = ?",
                    (file_id,)
                )

                if cursor.rowcount > 0:
                    db_ok = True
                else:
                    logging.warning(f"[CLEANUP][DB] nothing deleted file_id={file_id}")

        except Exception:
            logging.exception(f"[CLEANUP][DB] file_id={file_id}")

        # --- FINAL LOG ---
        logging.info(
            f"[CLEANUP] file_id={file_id} "
            f"input={input_ok} output={output_ok} db={db_ok}"
        )




