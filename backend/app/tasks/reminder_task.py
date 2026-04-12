import logging

from app.database import async_session
from app.services.email_service import send_reminder_email
from app.services.notification_service import create as create_notification
from app.services.reminder_service import get_due_reminders

logger = logging.getLogger(__name__)


async def check_due_reminders():
    async with async_session() as db:
        reminders = await get_due_reminders(db)

        for reminder in reminders:
            if reminder.notify_in_app:
                await create_notification(
                    db,
                    reminder_id=reminder.id,
                    title=f"Reminder: {reminder.title}",
                    message=reminder.description or reminder.title,
                )

            if reminder.notify_email and not reminder.email_sent:
                success = await send_reminder_email(
                    to_email="",
                    subject=f"Reminder: {reminder.title}",
                    body=reminder.description or reminder.title,
                )
                if success:
                    reminder.email_sent = True

        await db.commit()
        if reminders:
            logger.info(f"Processed {len(reminders)} due reminders")
