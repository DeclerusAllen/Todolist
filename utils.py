import json
import bcrypt
import typer
from datetime import datetime
from config import console, USERS_FILE, TASKS_FILE, SESSION_FILE, current_user


# -------- JSON --------
def load_json(file_path, default_data):
    if not file_path.exists():
        file_path.write_text(json.dumps(default_data))
        return default_data
    try:
        content = file_path.read_text().strip()
        return json.loads(content) if content else default_data
    except json.JSONDecodeError:
        console.print(f"[yellow]⚠ Fichier {file_path} corrompu. Réinitialisation...[/yellow]")
        file_path.write_text(json.dumps(default_data))
        return default_data

def save_json(file_path, data):
    try:
        file_path.write_text(json.dumps(data, indent=4))
    except Exception as e:
        console.print(f"[red]Erreur sauvegarde {file_path}: {e}[/red]")

# -------- Session --------
def save_session(username: str):
    SESSION_FILE.write_text(json.dumps({"username": username}))

def clear_session():
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()

def load_session():
    if not SESSION_FILE.exists():
        return None
    try:
        data = json.loads(SESSION_FILE.read_text())
        return data.get("username")
    except Exception:
        return None

def require_login():
    if current_user["username"]:
        return
    username = load_session()
    if username:
        users = load_json(USERS_FILE, {})
        if username in users:
            current_user["username"] = username
            return
    console.print("[red]❌ Vous devez être connecté ![/red]")
    console.print("[yellow]Utilisez : python -m todolist.main auth login[/yellow]")
    raise typer.Exit()

# -------- Input utilisateur --------
def ask_non_empty(prompt_text):
    while True:
        value = typer.prompt(prompt_text).strip()
        if value:
            return value
        console.print("[red]❌ Cette valeur ne peut pas être vide.[/red]")

def ask_date(prompt_text):
    while True:
        date_input = typer.prompt(prompt_text).strip()
        if date_input == "":
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            dt = datetime.strptime(date_input, "%Y-%m-%d %H:%M")
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            console.print("[red]❌ Format invalide. Utilisez YYYY-MM-DD HH:MM[/red]")

def ask_multiline(prompt_text):
    console.print(f"{prompt_text} (Terminer avec une ligne vide)")
    lines = []
    while True:
        line = typer.prompt("").rstrip()
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines) if lines else "[Aucune description]"

def confirm_action(message):
    while True:
        choice = typer.prompt(f"{message} [Y/N]").strip().lower()
        if choice in ["y", "n"]:
            return choice == "y"
        console.print("[red]❌ Veuillez répondre par Y ou N[/red]")

# -------- Bcrypt --------
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
