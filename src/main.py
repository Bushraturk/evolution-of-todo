"""Main entry point for Todo App CLI."""

import sys

from src.cli.commands import run_cli


def main() -> None:
    """Main entry point for the application."""
    exit_code = run_cli()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
