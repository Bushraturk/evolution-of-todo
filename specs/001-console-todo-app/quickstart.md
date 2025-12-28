# Quickstart: Console Todo App

**Feature**: 001-console-todo-app
**Date**: 2025-12-28

## Prerequisites

- Python 3.13 or higher
- UV package manager

### Verify Python Installation

```bash
python --version
# Expected: Python 3.13.x
```

### Install UV (if not installed)

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/user/todo-app.git
cd todo-app
```

### 2. Create Virtual Environment

```bash
uv venv
```

### 3. Activate Virtual Environment

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (CMD)
.venv\Scripts\activate.bat

# macOS/Linux
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
uv pip install -e .
```

## Usage

### Running the Application

```bash
# Using Python module
python -m src.main <command>

# Or if installed as package
todo <command>
```

### Quick Examples

```bash
# Add your first task
todo add "Buy groceries" -d "Milk, eggs, bread"

# View all tasks
todo list

# Mark task as complete
todo complete 1

# Update a task
todo update 1 -t "Buy organic groceries"

# Delete a task
todo delete 1

# Get help
todo help
```

## Example Session

```bash
$ todo add "Learn Python" -d "Complete the tutorial"
Task created successfully!
  ID: 1
  Title: Learn Python
  Description: Complete the tutorial
  Status: Incomplete

$ todo add "Exercise"
Task created successfully!
  ID: 2
  Title: Exercise
  Status: Incomplete

$ todo list
Your Tasks:
─────────────────────────────────────────────────────────────
ID   Status   Title                    Description
─────────────────────────────────────────────────────────────
1    [ ]      Learn Python             Complete the tutorial
2    [ ]      Exercise
─────────────────────────────────────────────────────────────
Total: 2 tasks (0 completed, 2 pending)

$ todo complete 1
Task 1 marked as complete!
  Title: Learn Python

$ todo list
Your Tasks:
─────────────────────────────────────────────────────────────
ID   Status   Title                    Description
─────────────────────────────────────────────────────────────
1    [x]      Learn Python             Complete the tutorial
2    [ ]      Exercise
─────────────────────────────────────────────────────────────
Total: 2 tasks (1 completed, 1 pending)
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/unit/test_task.py

# Run with verbose output
pytest -v
```

## Project Structure

```
todo-app/
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py          # Task dataclass
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py  # Business logic
│   └── cli/
│       ├── __init__.py
│       └── main.py          # CLI commands
├── tests/
│   ├── unit/
│   │   ├── test_task.py
│   │   └── test_task_service.py
│   └── integration/
│       └── test_cli.py
├── pyproject.toml
└── README.md
```

## Troubleshooting

### "Command not found: todo"

Make sure you've activated the virtual environment and installed the package:

```bash
source .venv/bin/activate  # or Windows equivalent
uv pip install -e .
```

### "Python version not supported"

Ensure you have Python 3.13+:

```bash
python --version
```

If needed, install Python 3.13 from [python.org](https://www.python.org/downloads/).

### "Module not found: src"

Run from the project root directory:

```bash
cd /path/to/todo-app
python -m src.main list
```

## Next Steps

After completing Phase I, the application will evolve in subsequent phases:

- **Phase II**: Full-stack web application with database persistence
- **Phase III**: AI-powered chatbot interface
- **Phase IV**: Kubernetes deployment
- **Phase V**: Cloud-native distributed system

## Support

For issues and feature requests, please open an issue on GitHub.
