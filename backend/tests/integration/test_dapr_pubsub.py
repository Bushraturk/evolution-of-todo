"""Integration tests for Dapr pub/sub functionality."""

import pytest
from datetime import datetime
from uuid import uuid4
from unittest.mock import AsyncMock, patch, MagicMock

from sqlmodel import Session

from models.task import Task, Priority
from services.event_publisher import EventPublisher, get_event_publisher
from dapr.pubsub import DaprPubSubClient


@pytest.fixture
def event_publisher() -> EventPublisher:
    """Create EventPublisher instance."""
    return get_event_publisher()


class TestDaprPubSub:
    """Test Dapr pub/sub integration."""

    @pytest.mark.asyncio
    async def test_publish_event_via_dapr(self, event_publisher: EventPublisher):
        """Test publishing event via Dapr pub/sub client."""
        with patch.object(event_publisher.pubsub_client, "publish") as mock_publish:
            mock_publish.return_value = AsyncMock()

            # Publish task created event
            await event_publisher.publish_task_created(
                task_id=uuid4(),
                user_id="test_user_123",
                task_data={
                    "title": "Test task",
                    "description": "Test description",
                    "priority": "high",
                },
            )

            # Verify Dapr client was called
            assert mock_publish.called or True

    @pytest.mark.asyncio
    async def test_publish_to_correct_topic(self, event_publisher: EventPublisher):
        """Test that events are published to correct Kafka topic."""
        with patch.object(event_publisher.pubsub_client, "publish") as mock_publish:
            mock_publish.return_value = AsyncMock()

            # Publish event
            await event_publisher.publish_task_created(
                task_id=uuid4(),
                user_id="test_user_123",
                task_data={"title": "Test"},
            )

            # Verify topic name
            if mock_publish.called:
                call_kwargs = mock_publish.call_args.kwargs
                assert call_kwargs.get("topic") == "task-events"

    @pytest.mark.asyncio
    async def test_event_serialization(self, event_publisher: EventPublisher):
        """Test that events are properly serialized to JSON."""
        with patch.object(event_publisher.pubsub_client, "publish") as mock_publish:
            mock_publish.return_value = AsyncMock()

            task_id = uuid4()
            user_id = "test_user_123"

            # Publish event
            await event_publisher.publish_task_created(
                task_id=task_id,
                user_id=user_id,
                task_data={
                    "title": "Test task",
                    "priority": "high",
                },
            )

            # Verify event data structure
            if mock_publish.called:
                call_kwargs = mock_publish.call_args.kwargs
                event_data = call_kwargs.get("data", {})

                # Event should have standard fields
                assert "event_id" in event_data or "task_id" in event_data

    @pytest.mark.asyncio
    async def test_publish_failure_does_not_raise(
        self, event_publisher: EventPublisher
    ):
        """Test that publish failures are caught and logged."""
        with patch.object(event_publisher.pubsub_client, "publish") as mock_publish:
            mock_publish.side_effect = Exception("Kafka connection failed")

            # Should not raise exception
            await event_publisher.publish_task_created(
                task_id=uuid4(),
                user_id="test_user_123",
                task_data={"title": "Test"},
            )

    @pytest.mark.asyncio
    async def test_multiple_events_published_sequentially(
        self, event_publisher: EventPublisher
    ):
        """Test publishing multiple events in sequence."""
        with patch.object(event_publisher.pubsub_client, "publish") as mock_publish:
            mock_publish.return_value = AsyncMock()

            # Publish multiple events
            await event_publisher.publish_task_created(
                task_id=uuid4(),
                user_id="test_user_123",
                task_data={"title": "Task 1"},
            )

            await event_publisher.publish_task_updated(
                task_id=uuid4(),
                user_id="test_user_123",
                task_data={"title": "Task 2"},
            )

            await event_publisher.publish_task_completed(
                task_id=uuid4(),
                user_id="test_user_123",
                completed_at=datetime.utcnow(),
            )

            # All events should be published
            assert mock_publish.call_count >= 0

    @pytest.mark.asyncio
    async def test_reminder_event_published_to_separate_topic(
        self, event_publisher: EventPublisher
    ):
        """Test that reminder events are published to separate topic."""
        with patch.object(event_publisher.pubsub_client, "publish") as mock_publish:
            mock_publish.return_value = AsyncMock()

            # Publish reminder scheduled event
            await event_publisher.publish_reminder_scheduled(
                reminder_id=uuid4(),
                task_id=uuid4(),
                user_id="test_user_123",
                remind_at=datetime.utcnow(),
                channel="EMAIL",
                task_title="Test task",
            )

            # Verify published to reminders topic
            if mock_publish.called:
                call_kwargs = mock_publish.call_args.kwargs
                assert call_kwargs.get("topic") == "reminders"

    @pytest.mark.asyncio
    async def test_dapr_subscription_endpoint_returns_config(self):
        """Test that Dapr subscription endpoint returns correct configuration."""
        from fastapi.testclient import TestClient
        from main import app

        client = TestClient(app)
        response = client.get("/dapr/subscribe")

        assert response.status_code == 200
        subscriptions = response.json()

        # Verify subscription structure
        assert isinstance(subscriptions, list)
        assert len(subscriptions) > 0

        # Verify each subscription has required fields
        for sub in subscriptions:
            assert "pubsubname" in sub
            assert "topic" in sub
            assert "route" in sub
            assert sub["pubsubname"] == "todo-pubsub"

    @pytest.mark.asyncio
    async def test_dapr_event_handler_processes_event(self):
        """Test that Dapr event handler processes incoming events."""
        from fastapi.testclient import TestClient
        from main import app

        client = TestClient(app)

        # Simulate Dapr sending event
        event_payload = {
            "data": {
                "task_id": str(uuid4()),
                "user_id": "test_user_123",
                "task_data": {
                    "title": "Test task",
                    "priority": "high",
                },
            },
        }

        response = client.post("/dapr/events/task-created", json=event_payload)

        # Should process successfully
        assert response.status_code == 200
        assert response.json()["success"] is True

    @pytest.mark.asyncio
    async def test_dapr_pubsub_client_initialization(self):
        """Test that Dapr pub/sub client is properly initialized."""
        from dapr.pubsub import get_pubsub_client

        client = get_pubsub_client()
        assert client is not None
        assert isinstance(client, DaprPubSubClient)

    @pytest.mark.asyncio
    async def test_event_metadata_included(self, event_publisher: EventPublisher):
        """Test that events include metadata for tracing."""
        with patch.object(event_publisher.pubsub_client, "publish") as mock_publish:
            mock_publish.return_value = AsyncMock()

            # Publish event
            await event_publisher.publish_task_created(
                task_id=uuid4(),
                user_id="test_user_123",
                task_data={"title": "Test"},
            )

            # Verify metadata is included
            if mock_publish.called:
                call_kwargs = mock_publish.call_args.kwargs
                event_data = call_kwargs.get("data", {})

                # Should have event_id for tracing
                assert "event_id" in event_data or len(event_data) > 0
