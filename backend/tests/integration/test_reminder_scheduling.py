"""Integration tests for reminder scheduling."""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from sqlmodel import Session, select

from models.reminder import Channel, Reminder, ReminderStatus
from models.scheduled_notification import ScheduledNotification, NotificationStatus
from models.task import Task
from services.reminder_service import ReminderService


@pytest.fixture
def reminder_service(session: Session) -> ReminderService:
    """Create ReminderService instance."""
    return ReminderService(session)


@pytest.fixture
def sample_task(session: Session) -> Task:
    """Create a sample task with due date."""
    task = Task(
        id=uuid4(),
        title="Test task with due date",
        description="Test description",
        user_id="test_user_123",
        completed=False,
        priority="medium",
        due_date=datetime.utcnow() + timedelta(hours=2),
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


class TestReminderScheduling:
    """Test reminder scheduling functionality."""

    def test_schedule_reminder_email(
        self, session: Session, reminder_service: ReminderService, sample_task: Task
    ):
        """Test scheduling an email reminder."""
        offset_minutes = 30
        due_date = sample_task.due_date

        reminder = reminder_service.schedule_reminder(
            task_id=sample_task.id,
            user_id=sample_task.user_id,
            offset_minutes=offset_minutes,
            channel=Channel.EMAIL,
            due_date=due_date,
        )

        # Verify reminder created
        assert reminder.id is not None
        assert reminder.task_id == sample_task.id
        assert reminder.user_id == sample_task.user_id
        assert reminder.offset_minutes == offset_minutes
        assert reminder.channel == Channel.EMAIL
        assert reminder.status == ReminderStatus.PENDING

        # Verify remind_at calculation
        expected_remind_at = due_date - timedelta(minutes=offset_minutes)
        assert reminder.remind_at == expected_remind_at

        # Verify scheduled notification created
        notifications = session.exec(
            select(ScheduledNotification).where(
                ScheduledNotification.reminder_id == reminder.id
            )
        ).all()

        assert len(notifications) == 1
        assert notifications[0].delivery_channel == "EMAIL"
        assert notifications[0].status == NotificationStatus.PENDING

    def test_schedule_reminder_push(
        self, session: Session, reminder_service: ReminderService, sample_task: Task
    ):
        """Test scheduling a push notification reminder."""
        offset_minutes = 60
        due_date = sample_task.due_date

        reminder = reminder_service.schedule_reminder(
            task_id=sample_task.id,
            user_id=sample_task.user_id,
            offset_minutes=offset_minutes,
            channel=Channel.PUSH,
            due_date=due_date,
        )

        # Verify reminder created
        assert reminder.channel == Channel.PUSH

        # Verify scheduled notification created
        notifications = session.exec(
            select(ScheduledNotification).where(
                ScheduledNotification.reminder_id == reminder.id
            )
        ).all()

        assert len(notifications) == 1
        assert notifications[0].delivery_channel == "PUSH"

    def test_schedule_reminder_both_channels(
        self, session: Session, reminder_service: ReminderService, sample_task: Task
    ):
        """Test scheduling reminder with both email and push."""
        offset_minutes = 120
        due_date = sample_task.due_date

        reminder = reminder_service.schedule_reminder(
            task_id=sample_task.id,
            user_id=sample_task.user_id,
            offset_minutes=offset_minutes,
            channel=Channel.BOTH,
            due_date=due_date,
        )

        # Verify reminder created
        assert reminder.channel == Channel.BOTH

        # Verify two scheduled notifications created
        notifications = session.exec(
            select(ScheduledNotification).where(
                ScheduledNotification.reminder_id == reminder.id
            )
        ).all()

        assert len(notifications) == 2
        channels = {n.delivery_channel for n in notifications}
        assert channels == {"EMAIL", "PUSH"}

    def test_get_reminders_for_task(
        self, session: Session, reminder_service: ReminderService, sample_task: Task
    ):
        """Test retrieving all reminders for a task."""
        # Create multiple reminders
        reminder1 = reminder_service.schedule_reminder(
            task_id=sample_task.id,
            user_id=sample_task.user_id,
            offset_minutes=30,
            channel=Channel.EMAIL,
            due_date=sample_task.due_date,
        )

        reminder2 = reminder_service.schedule_reminder(
            task_id=sample_task.id,
            user_id=sample_task.user_id,
            offset_minutes=60,
            channel=Channel.PUSH,
            due_date=sample_task.due_date,
        )

        # Get reminders
        reminders = reminder_service.get_reminders_for_task(
            sample_task.id, sample_task.user_id
        )

        assert len(reminders) == 2
        assert reminders[0].id in [reminder1.id, reminder2.id]
        assert reminders[1].id in [reminder1.id, reminder2.id]

    def test_delete_reminder(
        self, session: Session, reminder_service: ReminderService, sample_task: Task
    ):
        """Test deleting a reminder."""
        reminder = reminder_service.schedule_reminder(
            task_id=sample_task.id,
            user_id=sample_task.user_id,
            offset_minutes=30,
            channel=Channel.EMAIL,
            due_date=sample_task.due_date,
        )

        # Delete reminder
        success = reminder_service.delete_reminder(reminder.id, sample_task.user_id)
        assert success is True

        # Verify reminder deleted
        deleted_reminder = session.get(Reminder, reminder.id)
        assert deleted_reminder is None

        # Verify scheduled notifications also deleted (CASCADE)
        notifications = session.exec(
            select(ScheduledNotification).where(
                ScheduledNotification.reminder_id == reminder.id
            )
        ).all()
        assert len(notifications) == 0

    def test_delete_nonexistent_reminder(
        self, session: Session, reminder_service: ReminderService
    ):
        """Test deleting a reminder that doesn't exist."""
        success = reminder_service.delete_reminder(uuid4(), "test_user_123")
        assert success is False

    def test_update_reminder_status(
        self, session: Session, reminder_service: ReminderService, sample_task: Task
    ):
        """Test updating reminder status."""
        reminder = reminder_service.schedule_reminder(
            task_id=sample_task.id,
            user_id=sample_task.user_id,
            offset_minutes=30,
            channel=Channel.EMAIL,
            due_date=sample_task.due_date,
        )

        # Update status to SENT
        updated = reminder_service.update_reminder_status(
            reminder.id, ReminderStatus.SENT
        )

        assert updated is not None
        assert updated.status == ReminderStatus.SENT
        assert updated.updated_at > reminder.created_at

    def test_get_pending_notifications(
        self, session: Session, reminder_service: ReminderService, sample_task: Task
    ):
        """Test retrieving pending notifications that are due."""
        # Create reminder with past due time
        past_due_date = datetime.utcnow() + timedelta(minutes=10)
        reminder = reminder_service.schedule_reminder(
            task_id=sample_task.id,
            user_id=sample_task.user_id,
            offset_minutes=15,  # Will be 5 minutes in the past
            channel=Channel.EMAIL,
            due_date=past_due_date,
        )

        # Get pending notifications
        pending = reminder_service.get_pending_notifications(limit=10)

        # Should include our notification
        notification_ids = [n.id for n in pending]
        reminder_notifications = session.exec(
            select(ScheduledNotification).where(
                ScheduledNotification.reminder_id == reminder.id
            )
        ).all()

        assert len(reminder_notifications) > 0

    def test_update_notification_status(
        self, session: Session, reminder_service: ReminderService, sample_task: Task
    ):
        """Test updating notification status."""
        reminder = reminder_service.schedule_reminder(
            task_id=sample_task.id,
            user_id=sample_task.user_id,
            offset_minutes=30,
            channel=Channel.EMAIL,
            due_date=sample_task.due_date,
        )

        # Get notification
        notification = session.exec(
            select(ScheduledNotification).where(
                ScheduledNotification.reminder_id == reminder.id
            )
        ).first()

        # Update status to SENT
        updated = reminder_service.update_notification_status(
            notification.id, NotificationStatus.SENT
        )

        assert updated is not None
        assert updated.status == NotificationStatus.SENT
        assert updated.last_attempt_at is not None

    def test_update_notification_status_with_error(
        self, session: Session, reminder_service: ReminderService, sample_task: Task
    ):
        """Test updating notification status with error message."""
        reminder = reminder_service.schedule_reminder(
            task_id=sample_task.id,
            user_id=sample_task.user_id,
            offset_minutes=30,
            channel=Channel.EMAIL,
            due_date=sample_task.due_date,
        )

        # Get notification
        notification = session.exec(
            select(ScheduledNotification).where(
                ScheduledNotification.reminder_id == reminder.id
            )
        ).first()

        # Update status to FAILED with error
        error_msg = "SMTP connection failed"
        updated = reminder_service.update_notification_status(
            notification.id, NotificationStatus.FAILED, error_message=error_msg
        )

        assert updated is not None
        assert updated.status == NotificationStatus.FAILED
        assert updated.error_message == error_msg
        assert updated.retry_count == 1
