from pathlib import Path
from rich.console import Console

USERS_FILE = Path("users.json")
TASKS_FILE = Path("tasks.json")
SESSION_FILE = Path("session.json")

current_user = {"username": None}

console = Console()
