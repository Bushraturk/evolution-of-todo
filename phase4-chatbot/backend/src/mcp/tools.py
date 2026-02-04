"""MCP tool definitions for task operations."""
from typing import Any, Dict

# MCP Tool Schemas based on contracts/mcp-tools.json

ADD_TASK_SCHEMA = {
    "name": "add_task",
    "description": "Create a new task for the user. Use this when the user wants to add, create, or remember something.",
    "inputSchema": {
        "type": "object",
        "required": ["user_id", "title"],
        "properties": {
            "user_id": {
                "type": "string",
                "format": "uuid",
                "description": "ID of the user creating the task"
            },
            "title": {
                "type": "string",
                "minLength": 1,
                "maxLength": 200,
                "description": "Task title (what needs to be done)"
            },
            "description": {
                "type": "string",
                "maxLength": 1000,
                "description": "Optional detailed description of the task"
            }
        }
    }
}

LIST_TASKS_SCHEMA = {
    "name": "list_tasks",
    "description": "Retrieve tasks from the user's task list. Use this when the user wants to see, show, or list their tasks.",
    "inputSchema": {
        "type": "object",
        "required": ["user_id"],
        "properties": {
            "user_id": {
                "type": "string",
                "format": "uuid",
                "description": "ID of the user whose tasks to retrieve"
            },
            "status": {
                "type": "string",
                "enum": ["all", "pending", "completed"],
                "default": "all",
                "description": "Filter tasks by completion status"
            }
        }
    }
}

COMPLETE_TASK_SCHEMA = {
    "name": "complete_task",
    "description": "Mark a task as complete. Use this when the user says they finished, completed, or are done with a task.",
    "inputSchema": {
        "type": "object",
        "required": ["user_id", "task_id"],
        "properties": {
            "user_id": {
                "type": "string",
                "format": "uuid",
                "description": "ID of the user who owns the task"
            },
            "task_id": {
                "type": "string",
                "format": "uuid",
                "description": "ID of the task to mark as complete"
            }
        }
    }
}

UPDATE_TASK_SCHEMA = {
    "name": "update_task",
    "description": "Modify a task's title or description. Use this when the user wants to change, update, or rename a task.",
    "inputSchema": {
        "type": "object",
        "required": ["user_id", "task_id"],
        "properties": {
            "user_id": {
                "type": "string",
                "format": "uuid",
                "description": "ID of the user who owns the task"
            },
            "task_id": {
                "type": "string",
                "format": "uuid",
                "description": "ID of the task to update"
            },
            "title": {
                "type": "string",
                "minLength": 1,
                "maxLength": 200,
                "description": "New task title (optional)"
            },
            "description": {
                "type": "string",
                "maxLength": 1000,
                "description": "New task description (optional)"
            }
        }
    }
}

DELETE_TASK_SCHEMA = {
    "name": "delete_task",
    "description": "Remove a task from the user's list. Use this when the user wants to delete, remove, or cancel a task.",
    "inputSchema": {
        "type": "object",
        "required": ["user_id", "task_id"],
        "properties": {
            "user_id": {
                "type": "string",
                "format": "uuid",
                "description": "ID of the user who owns the task"
            },
            "task_id": {
                "type": "string",
                "format": "uuid",
                "description": "ID of the task to delete"
            }
        }
    }
}

# All tool schemas
ALL_TOOLS = [
    ADD_TASK_SCHEMA,
    LIST_TASKS_SCHEMA,
    COMPLETE_TASK_SCHEMA,
    UPDATE_TASK_SCHEMA,
    DELETE_TASK_SCHEMA
]
