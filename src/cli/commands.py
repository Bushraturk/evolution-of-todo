"""CLI commands for Todo App using argparse."""

import argparse
import sys
from typing import NoReturn

from src import __version__
from src.services.task_service import TaskService
from src.services.exceptions import TaskNotFoundError, ValidationError


# Global task service instance (persists during runtime)
_task_service: TaskService | None = None


def get_task_service() -> TaskService:
    """Get or create the global TaskService instance."""
    global _task_service
    if _task_service is None:
        _task_service = TaskService()
    return _task_service


def reset_task_service() -> None:
    """Reset the task service (for testing purposes)."""
    global _task_service
    _task_service = None


def print_error(message: str) -> None:
    """Print error message to stderr."""
    print(f"Error: {message}", file=sys.stderr)


def print_success(message: str) -> None:
    """Print success message to stdout."""
    print(message)


# =============================================================================
# Command Handlers
# =============================================================================


def handle_add(args: argparse.Namespace) -> int:
    """Handle the 'add' command.

    Args:
        args: Parsed arguments containing title and optional description.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    service = get_task_service()

    try:
        description = args.description if args.description else ""
        task = service.add_task(args.title, description)

        print_success("Task created successfully!")
        print(f"  ID: {task.id}")
        print(f"  Title: {task.title}")
        if task.description:
            print(f"  Description: {task.description}")
        print(f"  Status: {'Complete' if task.completed else 'Incomplete'}")
        return 0

    except ValidationError as e:
        print_error(str(e))
        return 1


def handle_list(args: argparse.Namespace) -> int:
    """Handle the 'list' command.

    Args:
        args: Parsed arguments (none required).

    Returns:
        Exit code (0 for success).
    """
    service = get_task_service()
    tasks = service.get_all_tasks()

    if not tasks:
        print("No tasks found. Add a task to get started.")
        print()
        print("Usage: todo add <title> [--description <text>]")
        return 0

    # Print header
    print("Your Tasks:")
    print("=" * 70)
    print(f"{'ID':<5}{'Status':<10}{'Title':<25}{'Description':<30}")
    print("=" * 70)

    # Print tasks
    for task in tasks:
        title_display = task.title[:22] + "..." if len(task.title) > 25 else task.title
        desc_display = task.description[:27] + "..." if len(task.description) > 30 else task.description
        print(f"{task.id:<5}{task.status_indicator:<10}{title_display:<25}{desc_display:<30}")

    # Print summary
    print("=" * 70)
    total = service.task_count
    completed = service.completed_count
    pending = service.pending_count
    print(f"Total: {total} task{'s' if total != 1 else ''} ({completed} completed, {pending} pending)")

    return 0


def handle_complete(args: argparse.Namespace) -> int:
    """Handle the 'complete' command.

    Args:
        args: Parsed arguments containing task ID.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    service = get_task_service()

    try:
        task_id = int(args.id)
    except ValueError:
        print_error("Invalid task ID. Please provide a numeric ID.")
        return 1

    try:
        task = service.toggle_complete(task_id)

        if task.completed:
            print_success(f"Task {task_id} marked as complete!")
        else:
            print_success(f"Task {task_id} marked as incomplete.")
        print(f"  Title: {task.title}")
        return 0

    except TaskNotFoundError as e:
        print_error(str(e))
        return 1


def handle_update(args: argparse.Namespace) -> int:
    """Handle the 'update' command.

    Args:
        args: Parsed arguments containing task ID and optional title/description.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    service = get_task_service()

    try:
        task_id = int(args.id)
    except ValueError:
        print_error("Invalid task ID. Please provide a numeric ID.")
        return 1

    try:
        task = service.update_task(
            task_id,
            title=args.title,
            description=args.description,
        )

        print_success(f"Task {task_id} updated successfully!")
        print(f"  Title: {task.title}")
        if task.description:
            print(f"  Description: {task.description}")
        return 0

    except TaskNotFoundError as e:
        print_error(str(e))
        return 1
    except ValidationError as e:
        print_error(str(e))
        return 1


def handle_delete(args: argparse.Namespace) -> int:
    """Handle the 'delete' command.

    Args:
        args: Parsed arguments containing task ID.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    service = get_task_service()

    try:
        task_id = int(args.id)
    except ValueError:
        print_error("Invalid task ID. Please provide a numeric ID.")
        return 1

    try:
        task = service.delete_task(task_id)

        print_success(f"Task {task_id} deleted successfully.")
        print(f"  Title: {task.title}")
        return 0

    except TaskNotFoundError as e:
        print_error(str(e))
        return 1


# =============================================================================
# Parser Creation
# =============================================================================


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    # Main parser
    parser = argparse.ArgumentParser(
        prog="todo",
        description="Todo App - A simple task management CLI",
        epilog="For more information, visit: https://github.com/user/todo-app",
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"Todo App v{__version__} (Phase I)",
    )

    # Subparsers for commands
    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        description="Available commands",
    )

    # 'add' command
    add_parser = subparsers.add_parser(
        "add",
        help="Add a new task",
        description="Add a new task to your todo list.",
    )
    add_parser.add_argument(
        "title",
        type=str,
        help="Task title (required, max 200 characters)",
    )
    add_parser.add_argument(
        "--description", "-d",
        type=str,
        default="",
        help="Task description (optional)",
    )
    add_parser.set_defaults(func=handle_add)

    # 'list' command
    list_parser = subparsers.add_parser(
        "list",
        help="View all tasks",
        description="Display all tasks with their status.",
    )
    list_parser.set_defaults(func=handle_list)

    # 'complete' command
    complete_parser = subparsers.add_parser(
        "complete",
        help="Toggle task completion",
        description="Mark a task as complete or incomplete.",
    )
    complete_parser.add_argument(
        "id",
        type=str,
        help="Task ID to toggle",
    )
    complete_parser.set_defaults(func=handle_complete)

    # 'update' command
    update_parser = subparsers.add_parser(
        "update",
        help="Update task details",
        description="Update a task's title and/or description.",
    )
    update_parser.add_argument(
        "id",
        type=str,
        help="Task ID to update",
    )
    update_parser.add_argument(
        "--title", "-t",
        type=str,
        default=None,
        help="New title for the task",
    )
    update_parser.add_argument(
        "--description", "-d",
        type=str,
        default=None,
        help="New description for the task",
    )
    update_parser.set_defaults(func=handle_update)

    # 'delete' command
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete a task",
        description="Remove a task from your todo list.",
    )
    delete_parser.add_argument(
        "id",
        type=str,
        help="Task ID to delete",
    )
    delete_parser.set_defaults(func=handle_delete)

    return parser


# =============================================================================
# Main Entry Point
# =============================================================================


def run_cli(args: list[str] | None = None) -> int:
    """Run the CLI application.

    Args:
        args: Command line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # If no command provided, show help
    if parsed_args.command is None:
        parser.print_help()
        return 0

    # Execute the command handler
    return parsed_args.func(parsed_args)
