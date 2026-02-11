"""Unit tests for tag creation and management."""

import pytest
from uuid import uuid4

from sqlmodel import Session

from models.tag import Tag
from services.tag_service import TagService


@pytest.fixture
def tag_service(session: Session) -> TagService:
    """Create TagService instance."""
    return TagService(session)


class TestTagCreation:
    """Test tag creation and management."""

    def test_create_tag(self, session: Session, tag_service: TagService):
        """Test creating a tag."""
        tag = tag_service.create_tag(
            user_id="test_user_123",
            name="Urgent",
            color="#ef4444",
        )

        assert tag.id is not None
        assert tag.name == "Urgent"
        assert tag.color == "#ef4444"
        assert tag.user_id == "test_user_123"

    def test_create_tag_with_default_color(
        self, session: Session, tag_service: TagService
    ):
        """Test creating a tag with default color."""
        tag = tag_service.create_tag(
            user_id="test_user_123",
            name="Work",
        )

        assert tag.color == "#6366f1"

    def test_create_duplicate_tag_fails(
        self, session: Session, tag_service: TagService
    ):
        """Test that creating duplicate tag fails."""
        tag_service.create_tag(
            user_id="test_user_123",
            name="Important",
        )

        with pytest.raises(ValueError, match="already exists"):
            tag_service.create_tag(
                user_id="test_user_123",
                name="Important",
            )

    def test_create_tag_strips_whitespace(
        self, session: Session, tag_service: TagService
    ):
        """Test that tag name is stripped of whitespace."""
        tag = tag_service.create_tag(
            user_id="test_user_123",
            name="  Personal  ",
        )

        assert tag.name == "Personal"

    def test_get_all_tags(self, session: Session, tag_service: TagService):
        """Test getting all tags for a user."""
        tag_service.create_tag(user_id="test_user_123", name="Work")
        tag_service.create_tag(user_id="test_user_123", name="Personal")
        tag_service.create_tag(user_id="test_user_123", name="Urgent")

        tags = tag_service.get_all_tags("test_user_123")

        assert len(tags) == 3
        # Should be sorted by name
        assert tags[0].name == "Personal"
        assert tags[1].name == "Urgent"
        assert tags[2].name == "Work"

    def test_get_tag_by_id(self, session: Session, tag_service: TagService):
        """Test getting a tag by ID."""
        created_tag = tag_service.create_tag(
            user_id="test_user_123",
            name="Important",
        )

        tag = tag_service.get_tag(created_tag.id, "test_user_123")

        assert tag is not None
        assert tag.id == created_tag.id
        assert tag.name == "Important"

    def test_get_tag_wrong_user_returns_none(
        self, session: Session, tag_service: TagService
    ):
        """Test that getting tag with wrong user returns None."""
        created_tag = tag_service.create_tag(
            user_id="test_user_123",
            name="Private",
        )

        tag = tag_service.get_tag(created_tag.id, "different_user")

        assert tag is None

    def test_update_tag_name(self, session: Session, tag_service: TagService):
        """Test updating tag name."""
        created_tag = tag_service.create_tag(
            user_id="test_user_123",
            name="Old Name",
        )

        updated_tag = tag_service.update_tag(
            tag_id=created_tag.id,
            user_id="test_user_123",
            name="New Name",
        )

        assert updated_tag is not None
        assert updated_tag.name == "New Name"

    def test_update_tag_color(self, session: Session, tag_service: TagService):
        """Test updating tag color."""
        created_tag = tag_service.create_tag(
            user_id="test_user_123",
            name="Colorful",
            color="#000000",
        )

        updated_tag = tag_service.update_tag(
            tag_id=created_tag.id,
            user_id="test_user_123",
            color="#ffffff",
        )

        assert updated_tag is not None
        assert updated_tag.color == "#ffffff"

    def test_update_tag_duplicate_name_fails(
        self, session: Session, tag_service: TagService
    ):
        """Test that updating to duplicate name fails."""
        tag_service.create_tag(user_id="test_user_123", name="Existing")
        tag2 = tag_service.create_tag(user_id="test_user_123", name="ToUpdate")

        with pytest.raises(ValueError, match="already exists"):
            tag_service.update_tag(
                tag_id=tag2.id,
                user_id="test_user_123",
                name="Existing",
            )

    def test_delete_tag(self, session: Session, tag_service: TagService):
        """Test deleting a tag."""
        created_tag = tag_service.create_tag(
            user_id="test_user_123",
            name="To Delete",
        )

        success = tag_service.delete_tag(created_tag.id, "test_user_123")

        assert success is True

        # Verify tag is deleted
        tag = tag_service.get_tag(created_tag.id, "test_user_123")
        assert tag is None

    def test_delete_nonexistent_tag(self, session: Session, tag_service: TagService):
        """Test deleting a tag that doesn't exist."""
        success = tag_service.delete_tag(uuid4(), "test_user_123")

        assert success is False

    def test_add_tag_to_task(self, session: Session, tag_service: TagService):
        """Test adding a tag to a task."""
        from models.task import Task

        # Create task
        task = Task(
            id=uuid4(),
            user_id="test_user_123",
            title="Test task",
            priority="medium",
            completed=False,
        )
        session.add(task)
        session.commit()

        # Create tag
        tag = tag_service.create_tag(user_id="test_user_123", name="Important")

        # Add tag to task
        added = tag_service.add_tag_to_task(
            task_id=task.id,
            tag_id=tag.id,
            user_id="test_user_123",
        )

        assert added is True

    def test_add_duplicate_tag_to_task_returns_false(
        self, session: Session, tag_service: TagService
    ):
        """Test that adding duplicate tag to task returns False."""
        from models.task import Task

        task = Task(
            id=uuid4(),
            user_id="test_user_123",
            title="Test task",
            priority="medium",
            completed=False,
        )
        session.add(task)
        session.commit()

        tag = tag_service.create_tag(user_id="test_user_123", name="Important")

        # Add tag first time
        tag_service.add_tag_to_task(task.id, tag.id, "test_user_123")

        # Try to add again
        added = tag_service.add_tag_to_task(task.id, tag.id, "test_user_123")

        assert added is False

    def test_get_tags_for_task(self, session: Session, tag_service: TagService):
        """Test getting all tags for a task."""
        from models.task import Task

        task = Task(
            id=uuid4(),
            user_id="test_user_123",
            title="Test task",
            priority="medium",
            completed=False,
        )
        session.add(task)
        session.commit()

        # Create and add multiple tags
        tag1 = tag_service.create_tag(user_id="test_user_123", name="Work")
        tag2 = tag_service.create_tag(user_id="test_user_123", name="Urgent")

        tag_service.add_tag_to_task(task.id, tag1.id, "test_user_123")
        tag_service.add_tag_to_task(task.id, tag2.id, "test_user_123")

        # Get tags
        tags = tag_service.get_tags_for_task(task.id, "test_user_123")

        assert len(tags) == 2
        tag_names = {tag.name for tag in tags}
        assert tag_names == {"Work", "Urgent"}

    def test_remove_tag_from_task(self, session: Session, tag_service: TagService):
        """Test removing a tag from a task."""
        from models.task import Task

        task = Task(
            id=uuid4(),
            user_id="test_user_123",
            title="Test task",
            priority="medium",
            completed=False,
        )
        session.add(task)
        session.commit()

        tag = tag_service.create_tag(user_id="test_user_123", name="Important")
        tag_service.add_tag_to_task(task.id, tag.id, "test_user_123")

        # Remove tag
        removed = tag_service.remove_tag_from_task(task.id, tag.id, "test_user_123")

        assert removed is True

        # Verify tag removed
        tags = tag_service.get_tags_for_task(task.id, "test_user_123")
        assert len(tags) == 0
