from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.tasks.reminder_task import check_due_reminders

scheduler = AsyncIOScheduler()


def start_scheduler():
    scheduler.add_job(
        check_due_reminders,
        "interval",
        minutes=settings.reminder_check_interval_minutes,
        id="check_reminders",
        replace_existing=True,
    )
    scheduler.start()


def stop_scheduler():
    scheduler.shutdown(wait=False)
