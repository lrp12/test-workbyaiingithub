# task-cli

A minimal Python command-line task manager using SQLite for storage.

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Add a task
task-cli add "Buy milk"

# List tasks
task-cli list

# Delete a task
task-cli delete 1
```

All tasks are stored in `~/.task_cli.db`.