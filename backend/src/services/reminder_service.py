"""ReminderService for managing task reminders and notifications."""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from models.reminder import Channel, Reminder, ReminderStatus
from models.scheduled_notification import ScheduledNotification, NotificationStatus
from models.task import Task
from services.event_publisher import get_event_publisher


class ReminderService:
    """Service for managing task reminders."""

    def __init__(self, session: Session):
        """Initialize service with database session.

        Args:
            session: SQLModel database session
        """
        self.session = session
        self.event_publisher = get_event_publisher()

    def schedule_reminder(
        self,
        task_id: UUID,
        user_id: str,
        offset_minutes: int,
        channel: Channel,
        due_date: datetime,
    ) -> Reminder:
        """Schedule a reminder for a task.

        Args:
            task_id: Task ID
            user_id: User ID
            offset_minutes: Minutes before due date to send reminder
            channel: Notification channel (EMAIL, PUSH, BOTH)
            due_date: Task due date

        Returns:
            Created Reminder
        """
        # Calculate remind_at timestamp
        remind_at = due_date - timedelta(minutes=offset_minutes)

        # Create reminder
        reminder = Reminder(
            task_id=task_id,
            user_id=user_id,
            remind_at=remind_at,
            offset_minutes=offset_minutes,
            channel=channel,
            status=ReminderStatus.PENDING,
        )

        self.session.add(reminder)
        self.session.commit()
        self.session.refresh(reminder)

        # Create scheduled notification(s)
        self._create_scheduled_notifications(reminder)

        # Publish reminder.scheduled event
        task = self.session.get(Task, task_id)
        if task:
            import asyncio
            try:
                asyncio.create_task(
                    self.event_publisher.publish_reminder_scheduled(
                        reminder_id=reminder.id,
                        task_id=task_id,
                        user_id=user_id,
                        remind_at=remind_at,
                        channel=channel.value,
                        task_title=task.title,
                    )
                )
            except RuntimeError:
                # No event loop running, skip event publishing
                pass

        return reminder

    def _create_scheduled_notifications(self, reminder: Reminder) -> None:
        """Create scheduled notification records for a reminder.

        Args:
            reminder: Reminder to create notifications for
        """
        channels = []
        if reminder.channel == Channel.EMAIL:
            channels = ["EMAIL"]
        elif reminder.channel == Channel.PUSH:
            channels = ["PUSH"]
        elif reminder.channel == Channel.BOTH:
            channels = ["EMAIL", "PUSH"]

        for channel in channels:
            notification = ScheduledNotification(
                reminder_id=reminder.id,
                task_id=reminder.task_id,
                user_id=reminder.user_id,
                scheduled_for=reminder.remind_at,
                delivery_channel=channel,
                status=NotificationStatus.PENDING,
            )
            self.session.add(notification)

        self.session.commit()

    def get_reminders_for_task(self, task_id: UUID, user_id: str) -> List[Reminder]:
        """Get all reminders for a task.

        Args:
            task_id: Task ID
            user_id: User ID

        Returns:
            List of reminders
        """
        statement = select(Reminder).where(
            Reminder.task_id == task_id,
            Reminder.user_id == user_id,
        ).order_by(Reminder.remind_at.asc())

        return list(self.session.exec(statement).all())

    def get_reminder(self, reminder_id: UUID, user_id: str) -> Optional[Reminder]:
        """Get a reminder by ID.

        Args:
            reminder_id: Reminder ID
            user_id: User ID

        Returns:
            Reminder or None if not found
        """
        reminder = self.session.get(Reminder, reminder_id)
        if reminder and reminder.user_id == user_id:
            return reminder
        return None

    def delete_reminder(self, reminder_id: UUID, user_id: str) -> bool:
        """Delete a reminder.

        Args:
            reminder_id: Reminder ID
            user_id: User ID

        Returns:
            True if deleted, False if not found
        """
        reminder = self.get_reminder(reminder_id, user_id)
        if not reminder:
            return False

        # Delete associated scheduled notifications (CASCADE)
        self.session.delete(reminder)
        self.session.commit()
        return True

    def update_reminder_status(
        self,
        reminder_id: UUID,
        status: ReminderStatus,
    ) -> Optional[Reminder]:
        """Update reminder status.

        Args:
            reminder_id: Reminder ID
            status: New status

        Returns:
            Updated Reminder or None if not found
        """
        reminder = self.session.get(Reminder, reminder_id)
        if not reminder:
            return None

        reminder.status = status
        reminder.updated_at = datetime.utcnow()

        self.session.add(reminder)
        self.session.commit()
        self.session.refresh(reminder)

        return reminder

    def get_pending_notifications(self, limit: int = 100) -> List[ScheduledNotification]:
        """Get pending notifications that are due to be sent.

        Args:
            limit: Maximum number of notifications to retrieve

        Returns:
            List of pending notifications
        """
        statement = (
            select(ScheduledNotification)
            .where(
                ScheduledNotification.status == NotificationStatus.PENDING,
                ScheduledNotification.scheduled_for <= datetime.utcnow(),
            )
            .order_by(ScheduledNotification.scheduled_for.asc())
            .limit(limit)
        )

        return list(self.session.exec(statement).all())

    def update_notification_status(
        self,
        notification_id: UUID,
        status: NotificationStatus,
        error_message: Optional[str] = None,
    ) -> Optional[ScheduledNotification]:
        """Update notification status.

        Args:
            notification_id: Notification ID
            status: New status
            error_message: Error message if failed

        Returns:
            Updated ScheduledNotification or None if not found
        """
        notification = self.session.get(ScheduledNotification, notification_id)
        if not notification:
            return None

        notification.status = status
        notification.last_attempt_at = datetime.utcnow()
        notification.updated_at = datetime.utcnow()

        if error_message:
            notification.error_message = error_message

        if status == NotificationStatus.FAILED:
            notification.retry_count += 1

        self.session.add(notification)
        self.session.commit()
        self.session.refresh(notification)

        return notification
