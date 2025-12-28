# CLI Command Contracts: Console Todo App

**Feature**: 001-console-todo-app
**Date**: 2025-12-28
**Status**: Complete

## Overview

This document defines the command-line interface contracts for the Phase I Console Todo App.

**Application Entry Point**: `python -m src.main` or `todo` (after installation)

## Commands

### 1. Add Task

**Command**: `todo add`

**Synopsis**:
```bash
todo add <title> [--description <text>]
todo add <title> [-d <text>]
```

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `title` | string | Yes | Task title (1-200 chars) |
| `--description`, `-d` | string | No | Task description |

**Output (Success)**:
```
Task created successfully!
  ID: 1
  Title: Buy groceries
  Description: Milk, eggs, bread
  Status: Incomplete
```

**Output (Error - Empty Title)**:
```
Error: Task title is required.
```

**Output (Error - Title Too Long)**:
```
Error: Task title must be 200 characters or less.
```

**Exit Codes**:
- `0`: Success
- `1`: Validation error

---

### 2. List Tasks

**Command**: `todo list`

**Synopsis**:
```bash
todo list
```

**Arguments**: None

**Output (Tasks Exist)**:
```
Your Tasks:
─────────────────────────────────────────────────────────────
ID   Status   Title                    Description
─────────────────────────────────────────────────────────────
1    [ ]      Buy groceries            Milk, eggs, bread
2    [x]      Call mom
3    [ ]      Write report             Q4 sales analysis
─────────────────────────────────────────────────────────────
Total: 3 tasks (1 completed, 2 pending)
```

**Output (No Tasks)**:
```
No tasks found. Add a task to get started.

Usage: todo add <title> [--description <text>]
```

**Exit Codes**:
- `0`: Success (regardless of task count)

---

### 3. Mark Complete/Incomplete

**Command**: `todo complete`

**Synopsis**:
```bash
todo complete <id>
```

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | integer | Yes | Task ID to toggle |

**Output (Mark Complete)**:
```
Task 1 marked as complete!
  Title: Buy groceries
```

**Output (Mark Incomplete)**:
```
Task 1 marked as incomplete.
  Title: Buy groceries
```

**Output (Error - Not Found)**:
```
Error: Task with ID 99 not found.
```

**Output (Error - Invalid ID)**:
```
Error: Invalid task ID. Please provide a numeric ID.
```

**Exit Codes**:
- `0`: Success
- `1`: Task not found or invalid ID

---

### 4. Update Task

**Command**: `todo update`

**Synopsis**:
```bash
todo update <id> [--title <text>] [--description <text>]
todo update <id> [-t <text>] [-d <text>]
```

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | integer | Yes | Task ID to update |
| `--title`, `-t` | string | No | New title |
| `--description`, `-d` | string | No | New description |

**Output (Success)**:
```
Task 1 updated successfully!
  Title: Buy organic groceries
  Description: Include vegetables
```

**Output (Error - Not Found)**:
```
Error: Task with ID 99 not found.
```

**Output (Error - Empty Title)**:
```
Error: Task title cannot be empty.
```

**Output (Error - No Changes)**:
```
Error: No updates provided. Use --title or --description.
```

**Exit Codes**:
- `0`: Success
- `1`: Validation error or task not found

---

### 5. Delete Task

**Command**: `todo delete`

**Synopsis**:
```bash
todo delete <id>
```

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | integer | Yes | Task ID to delete |

**Output (Success)**:
```
Task 1 deleted successfully.
  Title: Buy groceries
```

**Output (Error - Not Found)**:
```
Error: Task with ID 99 not found.
```

**Exit Codes**:
- `0`: Success
- `1`: Task not found

---

### 6. Help

**Command**: `todo help` or `todo --help` or `todo -h`

**Synopsis**:
```bash
todo help
todo --help
todo -h
```

**Output**:
```
Todo App - A simple task management CLI

Usage: todo <command> [options]

Commands:
  add <title> [-d <desc>]     Add a new task
  list                        View all tasks
  complete <id>               Toggle task completion
  update <id> [-t] [-d]       Update task details
  delete <id>                 Delete a task
  help                        Show this help message

Examples:
  todo add "Buy groceries" -d "Milk, eggs, bread"
  todo list
  todo complete 1
  todo update 1 -t "Buy organic groceries"
  todo delete 1

For more information, visit: https://github.com/user/todo-app
```

**Exit Codes**:
- `0`: Always

---

## Global Options

| Option | Description |
|--------|-------------|
| `--help`, `-h` | Show help for any command |
| `--version`, `-v` | Show application version |

## Error Handling

All errors follow this format:
```
Error: <message>
```

Error messages are:
- Human-readable
- Actionable (suggest fix when possible)
- Printed to stderr
- Return non-zero exit code

## Version Output

**Command**: `todo --version`

**Output**:
```
Todo App v1.0.0 (Phase I)
```
