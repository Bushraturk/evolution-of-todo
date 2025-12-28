"""Integration tests for Todo App CLI."""

import pytest

from src.cli.commands import run_cli, reset_task_service


@pytest.fixture(autouse=True)
def reset_service():
    """Reset the task service before each test."""
    reset_task_service()
    yield
    reset_task_service()


class TestCLIAdd:
    """Integration tests for the 'add' command."""

    def test_add_task_with_description(self, capsys) -> None:
        """Test adding a task with title and description."""
        exit_code = run_cli(["add", "Buy groceries", "-d", "Milk, eggs, bread"])

        assert exit_code == 0
        output = capsys.readouterr().out
        assert "Task created successfully!" in output
        assert "ID: 1" in output
        assert "Buy groceries" in output
        assert "Milk, eggs, bread" in output

    def test_add_task_without_description(self, capsys) -> None:
        """Test adding a task with only title."""
        exit_code = run_cli(["add", "Call mom"])

        assert exit_code == 0
        output = capsys.readouterr().out
        assert "Task created successfully!" in output
        assert "Call mom" in output

    def test_add_task_empty_title_fails(self, capsys) -> None:
        """Test that adding task with empty title fails."""
        exit_code = run_cli(["add", ""])

        assert exit_code == 1
        output = capsys.readouterr().err
        assert "Error:" in output


class TestCLIList:
    """Integration tests for the 'list' command."""

    def test_list_empty(self, capsys) -> None:
        """Test listing when no tasks exist."""
        exit_code = run_cli(["list"])

        assert exit_code == 0
        output = capsys.readouterr().out
        assert "No tasks found" in output

    def test_list_with_tasks(self, capsys) -> None:
        """Test listing tasks."""
        run_cli(["add", "Task 1"])
        run_cli(["add", "Task 2"])

        exit_code = run_cli(["list"])

        assert exit_code == 0
        output = capsys.readouterr().out
        assert "Task 1" in output
        assert "Task 2" in output
        assert "Total: 2 tasks" in output


class TestCLIComplete:
    """Integration tests for the 'complete' command."""

    def test_complete_task(self, capsys) -> None:
        """Test marking a task as complete."""
        run_cli(["add", "Test task"])

        exit_code = run_cli(["complete", "1"])

        assert exit_code == 0
        output = capsys.readouterr().out
        assert "marked as complete" in output

    def test_complete_toggle_back(self, capsys) -> None:
        """Test toggling task back to incomplete."""
        run_cli(["add", "Test task"])
        run_cli(["complete", "1"])

        exit_code = run_cli(["complete", "1"])

        assert exit_code == 0
        output = capsys.readouterr().out
        assert "marked as incomplete" in output

    def test_complete_not_found(self, capsys) -> None:
        """Test completing non-existent task."""
        exit_code = run_cli(["complete", "99"])

        assert exit_code == 1
        output = capsys.readouterr().err
        assert "Task with ID 99 not found" in output

    def test_complete_invalid_id(self, capsys) -> None:
        """Test completing with invalid ID."""
        exit_code = run_cli(["complete", "abc"])

        assert exit_code == 1
        output = capsys.readouterr().err
        assert "Invalid task ID" in output


class TestCLIUpdate:
    """Integration tests for the 'update' command."""

    def test_update_title(self, capsys) -> None:
        """Test updating task title."""
        run_cli(["add", "Original title"])

        exit_code = run_cli(["update", "1", "-t", "New title"])

        assert exit_code == 0
        output = capsys.readouterr().out
        assert "updated successfully" in output
        assert "New title" in output

    def test_update_description(self, capsys) -> None:
        """Test updating task description."""
        run_cli(["add", "Task"])

        exit_code = run_cli(["update", "1", "-d", "New description"])

        assert exit_code == 0
        output = capsys.readouterr().out
        assert "updated successfully" in output
        assert "New description" in output

    def test_update_not_found(self, capsys) -> None:
        """Test updating non-existent task."""
        exit_code = run_cli(["update", "99", "-t", "New title"])

        assert exit_code == 1
        output = capsys.readouterr().err
        assert "Task with ID 99 not found" in output

    def test_update_no_changes(self, capsys) -> None:
        """Test updating with no changes provided."""
        run_cli(["add", "Task"])

        exit_code = run_cli(["update", "1"])

        assert exit_code == 1
        output = capsys.readouterr().err
        assert "No updates provided" in output


class TestCLIDelete:
    """Integration tests for the 'delete' command."""

    def test_delete_task(self, capsys) -> None:
        """Test deleting a task."""
        run_cli(["add", "Task to delete"])

        exit_code = run_cli(["delete", "1"])

        assert exit_code == 0
        output = capsys.readouterr().out
        assert "deleted successfully" in output
        assert "Task to delete" in output

    def test_delete_not_found(self, capsys) -> None:
        """Test deleting non-existent task."""
        exit_code = run_cli(["delete", "99"])

        assert exit_code == 1
        output = capsys.readouterr().err
        assert "Task with ID 99 not found" in output


class TestCLIHelp:
    """Integration tests for help and version."""

    def test_help_no_command(self, capsys) -> None:
        """Test showing help when no command provided."""
        exit_code = run_cli([])

        assert exit_code == 0
        output = capsys.readouterr().out
        assert "Todo App" in output

    def test_version(self, capsys) -> None:
        """Test version flag."""
        with pytest.raises(SystemExit) as exc_info:
            run_cli(["--version"])

        assert exc_info.value.code == 0
        output = capsys.readouterr().out
        assert "Todo App v1.0.0" in output


class TestCLIWorkflow:
    """Integration tests for complete workflows."""

    def test_full_workflow(self, capsys) -> None:
        """Test complete workflow: add -> view -> complete -> view."""
        # Add tasks
        run_cli(["add", "Task 1", "-d", "Description 1"])
        run_cli(["add", "Task 2"])

        # View tasks
        run_cli(["list"])
        output = capsys.readouterr().out
        assert "Task 1" in output
        assert "Task 2" in output
        assert "[ ]" in output  # Both incomplete

        # Complete first task
        run_cli(["complete", "1"])

        # View again to verify
        run_cli(["list"])
        output = capsys.readouterr().out
        assert "[x]" in output  # First task complete
        assert "1 completed" in output

    def test_crud_workflow(self, capsys) -> None:
        """Test Create, Read, Update, Delete workflow."""
        # Create
        run_cli(["add", "Original Task"])

        # Read
        run_cli(["list"])
        output = capsys.readouterr().out
        assert "Original Task" in output

        # Update
        run_cli(["update", "1", "-t", "Updated Task"])

        # Read again
        run_cli(["list"])
        output = capsys.readouterr().out
        assert "Updated Task" in output
        assert "Original Task" not in output

        # Delete
        run_cli(["delete", "1"])

        # Read final
        run_cli(["list"])
        output = capsys.readouterr().out
        assert "No tasks found" in output
