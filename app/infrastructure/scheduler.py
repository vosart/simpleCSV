from apscheduler.schedulers.background import BackgroundScheduler
import logging

from app.infrastructure.db import cleanup_old_tasks



scheduler = BackgroundScheduler()

def cleanup_job():
    logging.info("[CLEANUP] triggered")
    cleanup_old_tasks(days=3)


def start_scheduler():
    scheduler.add_job(
        cleanup_job,
        "interval",
        minutes=10,
        max_instances=1,
        coalesce=True
    )
    scheduler.start()

def stop_scheduler():
    scheduler.shutdown()