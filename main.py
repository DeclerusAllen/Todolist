import typer
from auth import auth_app
from tasks import tasks_app
from utils import load_session, load_json
from config import USERS_FILE, current_user

app = typer.Typer(help="📝 Gestion de tâches avec authentification")
app.add_typer(auth_app, name="auth")
app.add_typer(tasks_app, name="tasks")

if __name__ == "__main__":
    username = load_session()
    if username:
        users = load_json(USERS_FILE, {})
        if username in users:
            current_user["username"] = username
    app()
