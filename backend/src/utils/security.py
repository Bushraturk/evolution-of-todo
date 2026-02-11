"""Security utilities for input validation and sanitization."""

import re
from typing import Any, Dict
from uuid import UUID


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """Sanitize string input by removing potentially dangerous characters.

    Args:
        value: Input string
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if not value:
        return ""

    # Remove null bytes
    sanitized = value.replace("\x00", "")

    # Trim to max length
    sanitized = sanitized[:max_length]

    # Strip leading/trailing whitespace
    sanitized = sanitized.strip()

    return sanitized


def validate_uuid(value: str) -> bool:
    """Validate UUID format.

    Args:
        value: UUID string

    Returns:
        True if valid UUID, False otherwise
    """
    try:
        UUID(value)
        return True
    except (ValueError, AttributeError):
        return False


def validate_email(email: str) -> bool:
    """Validate email format.

    Args:
        email: Email address

    Returns:
        True if valid email, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_color_hex(color: str) -> bool:
    """Validate hex color code format.

    Args:
        color: Hex color code

    Returns:
        True if valid hex color, False otherwise
    """
    pattern = r'^#[0-9A-Fa-f]{6}$'
    return bool(re.match(pattern, color))


def sanitize_event_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize event data before publishing.

    Args:
        data: Event data dictionary

    Returns:
        Sanitized event data
    """
    sanitized = {}

    for key, value in data.items():
        # Sanitize string values
        if isinstance(value, str):
            sanitized[key] = sanitize_string(value)
        # Recursively sanitize nested dicts
        elif isinstance(value, dict):
            sanitized[key] = sanitize_event_data(value)
        # Keep other types as-is (numbers, booleans, None)
        else:
            sanitized[key] = value

    return sanitized


def validate_task_title(title: str) -> tuple[bool, str]:
    """Validate task title.

    Args:
        title: Task title

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not title or not title.strip():
        return False, "Title cannot be empty"

    if len(title) > 200:
        return False, "Title must be 200 characters or less"

    # Check for suspicious patterns (potential XSS)
    suspicious_patterns = [
        r'<script',
        r'javascript:',
        r'onerror=',
        r'onclick=',
    ]

    for pattern in suspicious_patterns:
        if re.search(pattern, title, re.IGNORECASE):
            return False, "Title contains potentially unsafe content"

    return True, ""


def validate_task_description(description: str) -> tuple[bool, str]:
    """Validate task description.

    Args:
        description: Task description

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not description:
        return True, ""  # Description is optional

    if len(description) > 1000:
        return False, "Description must be 1000 characters or less"

    # Check for suspicious patterns
    suspicious_patterns = [
        r'<script',
        r'javascript:',
        r'onerror=',
        r'onclick=',
    ]

    for pattern in suspicious_patterns:
        if re.search(pattern, description, re.IGNORECASE):
            return False, "Description contains potentially unsafe content"

    return True, ""


def validate_tag_name(name: str) -> tuple[bool, str]:
    """Validate tag name.

    Args:
        name: Tag name

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Tag name cannot be empty"

    if len(name) > 50:
        return False, "Tag name must be 50 characters or less"

    # Only allow alphanumeric, spaces, hyphens, underscores
    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
        return False, "Tag name can only contain letters, numbers, spaces, hyphens, and underscores"

    return True, ""


def sanitize_search_query(query: str) -> str:
    """Sanitize search query to prevent SQL injection.

    Args:
        query: Search query

    Returns:
        Sanitized query
    """
    if not query:
        return ""

    # Remove SQL special characters
    sanitized = query.replace("'", "").replace('"', "").replace(";", "")

    # Remove SQL keywords (case-insensitive)
    sql_keywords = [
        "DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE",
        "EXEC", "EXECUTE", "UNION", "SELECT", "--", "/*", "*/"
    ]

    for keyword in sql_keywords:
        sanitized = re.sub(
            rf'\b{keyword}\b',
            '',
            sanitized,
            flags=re.IGNORECASE
        )

    # Trim and limit length
    sanitized = sanitized.strip()[:200]

    return sanitized


def validate_offset_minutes(offset: int) -> tuple[bool, str]:
    """Validate reminder offset minutes.

    Args:
        offset: Offset in minutes

    Returns:
        Tuple of (is_valid, error_message)
    """
    if offset < 1:
        return False, "Offset must be at least 1 minute"

    if offset > 43200:  # 30 days
        return False, "Offset cannot exceed 30 days (43200 minutes)"

    return True, ""


def validate_recurrence_interval(interval: int) -> tuple[bool, str]:
    """Validate recurrence interval.

    Args:
        interval: Recurrence interval

    Returns:
        Tuple of (is_valid, error_message)
    """
    if interval < 1:
        return False, "Interval must be at least 1"

    if interval > 365:
        return False, "Interval cannot exceed 365"

    return True, ""
