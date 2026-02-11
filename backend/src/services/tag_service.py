"""Tag service for managing task tags."""

from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from models.tag import Tag


class TagService:
    """Service for managing tags."""

    def __init__(self, session: Session):
        """Initialize service.

        Args:
            session: Database session
        """
        self.session = session

    def get_all_tags(self, user_id: str) -> List[Tag]:
        """Get all tags for a user.

        Args:
            user_id: User ID

        Returns:
            List of tags
        """
        statement = select(Tag).where(Tag.user_id == user_id).order_by(Tag.name.asc())
        return list(self.session.exec(statement).all())

    def get_tag(self, tag_id: UUID, user_id: str) -> Optional[Tag]:
        """Get a tag by ID.

        Args:
            tag_id: Tag ID
            user_id: User ID

        Returns:
            Tag or None if not found
        """
        tag = self.session.get(Tag, tag_id)
        if tag and tag.user_id == user_id:
            return tag
        return None

    def create_tag(self, user_id: str, name: str, color: str = "#6366f1") -> Tag:
        """Create a new tag.

        Args:
            user_id: User ID
            name: Tag name
            color: Tag color (hex code)

        Returns:
            Created tag
        """
        # Check if tag with same name already exists
        existing = self.session.exec(
            select(Tag).where(Tag.user_id == user_id, Tag.name == name)
        ).first()

        if existing:
            raise ValueError(f"Tag with name '{name}' already exists")

        tag = Tag(
            user_id=user_id,
            name=name.strip(),
            color=color,
        )

        self.session.add(tag)
        self.session.commit()
        self.session.refresh(tag)

        return tag

    def update_tag(
        self,
        tag_id: UUID,
        user_id: str,
        name: Optional[str] = None,
        color: Optional[str] = None,
    ) -> Optional[Tag]:
        """Update a tag.

        Args:
            tag_id: Tag ID
            user_id: User ID
            name: New tag name
            color: New tag color

        Returns:
            Updated tag or None if not found
        """
        tag = self.get_tag(tag_id, user_id)
        if not tag:
            return None

        if name is not None:
            # Check if new name conflicts with existing tag
            existing = self.session.exec(
                select(Tag).where(
                    Tag.user_id == user_id,
                    Tag.name == name,
                    Tag.id != tag_id,
                )
            ).first()

            if existing:
                raise ValueError(f"Tag with name '{name}' already exists")

            tag.name = name.strip()

        if color is not None:
            tag.color = color

        self.session.add(tag)
        self.session.commit()
        self.session.refresh(tag)

        return tag

    def delete_tag(self, tag_id: UUID, user_id: str) -> bool:
        """Delete a tag.

        Args:
            tag_id: Tag ID
            user_id: User ID

        Returns:
            True if deleted, False if not found
        """
        tag = self.get_tag(tag_id, user_id)
        if not tag:
            return False

        # Delete tag (CASCADE will remove task_tags associations)
        self.session.delete(tag)
        self.session.commit()

        return True

    def get_tags_for_task(self, task_id: UUID, user_id: str) -> List[Tag]:
        """Get all tags for a task.

        Args:
            task_id: Task ID
            user_id: User ID

        Returns:
            List of tags
        """
        from models.task_tag import TaskTag

        statement = (
            select(Tag)
            .join(TaskTag, TaskTag.tag_id == Tag.id)
            .where(
                TaskTag.task_id == task_id,
                Tag.user_id == user_id,
            )
            .order_by(Tag.name.asc())
        )

        return list(self.session.exec(statement).all())

    def add_tag_to_task(self, task_id: UUID, tag_id: UUID, user_id: str) -> bool:
        """Add a tag to a task.

        Args:
            task_id: Task ID
            tag_id: Tag ID
            user_id: User ID

        Returns:
            True if added, False if already exists
        """
        from models.task_tag import TaskTag

        # Verify tag belongs to user
        tag = self.get_tag(tag_id, user_id)
        if not tag:
            raise ValueError("Tag not found")

        # Check if association already exists
        existing = self.session.exec(
            select(TaskTag).where(
                TaskTag.task_id == task_id,
                TaskTag.tag_id == tag_id,
            )
        ).first()

        if existing:
            return False

        # Create association
        task_tag = TaskTag(task_id=task_id, tag_id=tag_id)
        self.session.add(task_tag)
        self.session.commit()

        return True

    def remove_tag_from_task(self, task_id: UUID, tag_id: UUID, user_id: str) -> bool:
        """Remove a tag from a task.

        Args:
            task_id: Task ID
            tag_id: Tag ID
            user_id: User ID

        Returns:
            True if removed, False if not found
        """
        from models.task_tag import TaskTag

        # Verify tag belongs to user
        tag = self.get_tag(tag_id, user_id)
        if not tag:
            return False

        # Find and delete association
        task_tag = self.session.exec(
            select(TaskTag).where(
                TaskTag.task_id == task_id,
                TaskTag.tag_id == tag_id,
            )
        ).first()

        if not task_tag:
            return False

        self.session.delete(task_tag)
        self.session.commit()

        return True
