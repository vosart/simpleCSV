from app.infrastructure.scheduler import scheduler
from app.core.backoff import get_backoff

from datetime import datetime, timedelta
import logging

def schedule_retry(task):
    delay = get_backoff(task["attempts"])
    run_at = datetime.now() + timedelta(seconds=delay)

    scheduler.add_job(
        "app.services.processor:process_in_background",
        trigger="date",
        run_date=run_at,
        args=[
            task["input_path"],
            task["output_path"],
            task["file_id"]
        ],
        id=f"retry_{task['file_id']}",
        replace_existing=True
    )
    logging.info(
        f"[RETRY] scheduled file_id={task['file_id']} in {delay}s"
    )

