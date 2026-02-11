"""Notification Service - Handles reminder delivery via email and push notifications."""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID

from sqlmodel import Session, select

from models.reminder import Reminder, ReminderStatus
from models.scheduled_notification import ScheduledNotification, NotificationStatus
from models.task import Task
from services.reminder_service import ReminderService
from database import get_session

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for delivering notifications."""

    def __init__(self, session: Session):
        """Initialize service.

        Args:
            session: Database session
        """
        self.session = session
        self.reminder_service = ReminderService(session)
        self.resend_api_key = os.getenv("RESEND_API_KEY")
        self.resend_from_email = os.getenv("RESEND_FROM_EMAIL", "noreply@todoapp.com")

    async def process_pending_notifications(self) -> int:
        """Process all pending notifications that are due.

        Returns:
            Number of notifications processed
        """
        try:
            notifications = self.reminder_service.get_pending_notifications(limit=100)
            processed_count = 0

            for notification in notifications:
                try:
                    # Check if task is still incomplete
                    task = self.session.get(Task, notification.task_id)
                    if not task or task.completed:
                        logger.info(f"Skipping notification {notification.id} - task completed or not found")
                        self.reminder_service.update_notification_status(
                            notification.id,
                            NotificationStatus.SENT,
                        )
                        continue

                    # Update status to QUEUED
                    self.reminder_service.update_notification_status(
                        notification.id,
                        NotificationStatus.QUEUED,
                    )

                    # Deliver notification
                    success = await self._deliver_notification(notification, task)

                    if success:
                        # Mark as SENT
                        self.reminder_service.update_notification_status(
                            notification.id,
                            NotificationStatus.SENT,
                        )

                        # Update reminder status
                        self.reminder_service.update_reminder_status(
                            notification.reminder_id,
                            ReminderStatus.SENT,
                        )

                        processed_count += 1
                        logger.info(f"Successfully delivered notification {notification.id}")
                    else:
                        # Mark as FAILED
                        self.reminder_service.update_notification_status(
                            notification.id,
                            NotificationStatus.FAILED,
                            error_message="Delivery failed",
                        )

                        # Retry logic
                        if notification.retry_count < 3:
                            logger.warning(f"Notification {notification.id} failed, will retry")
                        else:
                            logger.error(f"Notification {notification.id} failed after 3 retries")
                            self.reminder_service.update_reminder_status(
                                notification.reminder_id,
                                ReminderStatus.FAILED,
                            )

                except Exception as e:
                    logger.error(f"Error processing notification {notification.id}: {e}", exc_info=True)
                    self.reminder_service.update_notification_status(
                        notification.id,
                        NotificationStatus.FAILED,
                        error_message=str(e),
                    )

            logger.info(f"Processed {processed_count} notifications")
            return processed_count

        except Exception as e:
            logger.error(f"Error in process_pending_notifications: {e}", exc_info=True)
            return 0

    async def _deliver_notification(
        self,
        notification: ScheduledNotification,
        task: Task,
    ) -> bool:
        """Deliver a notification via the specified channel.

        Args:
            notification: Notification to deliver
            task: Task associated with the notification

        Returns:
            True if delivery succeeded, False otherwise
        """
        try:
            if notification.delivery_channel == "EMAIL":
                return await self._send_email_notification(notification, task)
            elif notification.delivery_channel == "PUSH":
                return await self._send_push_notification(notification, task)
            else:
                logger.error(f"Unknown delivery channel: {notification.delivery_channel}")
                return False
        except Exception as e:
            logger.error(f"Error delivering notification: {e}", exc_info=True)
            return False

    async def _send_email_notification(
        self,
        notification: ScheduledNotification,
        task: Task,
    ) -> bool:
        """Send email notification via Resend.

        Args:
            notification: Notification to send
            task: Task associated with the notification

        Returns:
            True if email sent successfully
        """
        try:
            if not self.resend_api_key:
                logger.warning("RESEND_API_KEY not configured, skipping email")
                return False

            # Import resend library
            try:
                import resend
            except ImportError:
                logger.error("resend library not installed")
                return False

            resend.api_key = self.resend_api_key

            # Get user email (would need to fetch from user table)
            # For now, using a placeholder
            user_email = f"user_{notification.user_id}@example.com"

            # Format due date
            due_date_str = task.due_date.strftime("%B %d, %Y at %I:%M %p") if task.due_date else "soon"

            # Send email
            params = {
                "from": self.resend_from_email,
                "to": [user_email],
                "subject": f"Reminder: {task.title}",
                "html": f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #7c3aed;">📅 Task Reminder</h2>
                        <p>This is a reminder about your upcoming task:</p>

                        <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <h3 style="margin-top: 0; color: #7c3aed;">{task.title}</h3>
                            {f'<p style="color: #666;">{task.description}</p>' if task.description else ''}
                            <p><strong>Due:</strong> {due_date_str}</p>
                            <p><strong>Priority:</strong> {task.priority.value.upper()}</p>
                        </div>

                        <p>Don't forget to complete this task on time!</p>

                        <p style="color: #999; font-size: 12px; margin-top: 30px;">
                            This is an automated reminder from your Todo App.
                        </p>
                    </div>
                </body>
                </html>
                """,
            }

            response = resend.Emails.send(params)
            logger.info(f"Email sent successfully: {response}")
            return True

        except Exception as e:
            logger.error(f"Error sending email: {e}", exc_info=True)
            return False

    async def _send_push_notification(
        self,
        notification: ScheduledNotification,
        task: Task,
    ) -> bool:
        """Send push notification via Web Push API.

        Args:
            notification: Notification to send
            task: Task associated with the notification

        Returns:
            True if push notification sent successfully
        """
        try:
            # Web Push implementation would go here
            # For now, just log
            logger.info(f"Push notification for task {task.title} (not implemented yet)")

            # TODO: Implement Web Push API
            # Would need:
            # 1. User's push subscription (endpoint, keys)
            # 2. VAPID keys for authentication
            # 3. pywebpush library

            return True

        except Exception as e:
            logger.error(f"Error sending push notification: {e}", exc_info=True)
            return False

    async def run_notification_scheduler(self) -> None:
        """Run notification scheduler (cron job).

        This should be called every minute to check for pending notifications.
        """
        try:
            logger.info("Running notification scheduler")
            processed = await self.process_pending_notifications()
            logger.info(f"Notification scheduler completed: {processed} notifications processed")
        except Exception as e:
            logger.error(f"Error in notification scheduler: {e}", exc_info=True)


async def main():
    """Main entry point for notification service."""
    logger.info("Starting Notification Service")

    # Get database session
    session = next(get_session())

    # Initialize service
    service = NotificationService(session)

    # Run scheduler in a loop
    try:
        while True:
            await service.run_notification_scheduler()
            # Wait 1 minute before next check
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        logger.info("Shutting down Notification Service")


if __name__ == "__main__":
    asyncio.run(main())
