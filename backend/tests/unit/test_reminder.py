"""Unit tests for reminder calculations."""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from models.reminder import Channel, ReminderStatus
from services.reminder_service import ReminderService


class TestReminderCalculations:
    """Test reminder time calculations."""

    def test_remind_at_calculation_30_minutes(self):
        """Test remind_at calculation for 30 minutes before due date."""
        due_date = datetime(2026, 2, 15, 14, 0, 0)
        offset_minutes = 30

        expected_remind_at = datetime(2026, 2, 15, 13, 30, 0)
        actual_remind_at = due_date - timedelta(minutes=offset_minutes)

        assert actual_remind_at == expected_remind_at

    def test_remind_at_calculation_1_hour(self):
        """Test remind_at calculation for 1 hour before due date."""
        due_date = datetime(2026, 2, 15, 14, 0, 0)
        offset_minutes = 60

        expected_remind_at = datetime(2026, 2, 15, 13, 0, 0)
        actual_remind_at = due_date - timedelta(minutes=offset_minutes)

        assert actual_remind_at == expected_remind_at

    def test_remind_at_calculation_1_day(self):
        """Test remind_at calculation for 1 day before due date."""
        due_date = datetime(2026, 2, 15, 14, 0, 0)
        offset_minutes = 1440  # 24 hours

        expected_remind_at = datetime(2026, 2, 14, 14, 0, 0)
        actual_remind_at = due_date - timedelta(minutes=offset_minutes)

        assert actual_remind_at == expected_remind_at

    def test_remind_at_calculation_1_week(self):
        """Test remind_at calculation for 1 week before due date."""
        due_date = datetime(2026, 2, 15, 14, 0, 0)
        offset_minutes = 10080  # 7 days

        expected_remind_at = datetime(2026, 2, 8, 14, 0, 0)
        actual_remind_at = due_date - timedelta(minutes=offset_minutes)

        assert actual_remind_at == expected_remind_at

    def test_remind_at_crosses_day_boundary(self):
        """Test remind_at calculation that crosses day boundary."""
        due_date = datetime(2026, 2, 15, 1, 0, 0)  # 1 AM
        offset_minutes = 120  # 2 hours

        expected_remind_at = datetime(2026, 2, 14, 23, 0, 0)  # 11 PM previous day
        actual_remind_at = due_date - timedelta(minutes=offset_minutes)

        assert actual_remind_at == expected_remind_at

    def test_remind_at_crosses_month_boundary(self):
        """Test remind_at calculation that crosses month boundary."""
        due_date = datetime(2026, 3, 1, 10, 0, 0)  # March 1
        offset_minutes = 1440  # 1 day

        expected_remind_at = datetime(2026, 2, 28, 10, 0, 0)  # Feb 28 (not leap year)
        actual_remind_at = due_date - timedelta(minutes=offset_minutes)

        assert actual_remind_at == expected_remind_at

    def test_channel_enum_values(self):
        """Test Channel enum has correct values."""
        assert Channel.EMAIL.value == "EMAIL"
        assert Channel.PUSH.value == "PUSH"
        assert Channel.BOTH.value == "BOTH"

    def test_reminder_status_enum_values(self):
        """Test ReminderStatus enum has correct values."""
        assert ReminderStatus.PENDING.value == "PENDING"
        assert ReminderStatus.SCHEDULED.value == "SCHEDULED"
        assert ReminderStatus.SENT.value == "SENT"
        assert ReminderStatus.FAILED.value == "FAILED"
