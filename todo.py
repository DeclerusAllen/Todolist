import json
import typer
import getpass
from pathlib import Path
from rich.console import Console
from rich.table import Table
from datetime import datetime

console = Console()

# --- Fichiers JSON ---
USERS_FILE = Path("users.json")
TASKS_FILE = Path("tasks.json")
SESSION_FILE = Path("session.json")

current_user = {"username": None}

app = typer.Typer(help="📝 Gestion de tâches avec authentification")
auth_app = typer.Typer(help="Gestion de l'authentification (register/login/logout)")
tasks_app = typer.Typer(help="Gestion des tâches (après connexion)")

app.add_typer(auth_app, name="auth")
app.add_typer(tasks_app, name="tasks")

# ==========================
#       FONCTIONS UTILES
# ==========================

def load_json(file_path: Path, default_data):
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


def save_json(file_path: Path, data):
    try:
        file_path.write_text(json.dumps(data, indent=4))
    except Exception as e:
        console.print(f"[red]Erreur sauvegarde {file_path}: {e}[/red]")


def save_session(username: str):
    try:
        SESSION_FILE.write_text(json.dumps({"username": username}))
    except Exception as e:
        console.print(f"[red]Impossible de sauvegarder la session: {e}[/red]")


def clear_session():
    try:
        if SESSION_FILE.exists():
            SESSION_FILE.unlink()
    except Exception as e:
        console.print(f"[red]Impossible de supprimer la session: {e}[/red]")


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
    console.print("[yellow]Utilisez : python todo.py auth login[/yellow]")
    raise typer.Exit()


def get_user_tasks():
    tasks = load_json(TASKS_FILE, {})
    return tasks.get(current_user["username"], [])


def save_user_tasks(user_tasks):
    tasks = load_json(TASKS_FILE, {})
    tasks[current_user["username"]] = user_tasks
    save_json(TASKS_FILE, tasks)


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


def search_tasks_interactive(for_modify_delete=False):
    """
    Recherche flexible : ID, titre ou date.
    - for_modify_delete=True: après filtre par titre/date, demande ID pour confirmer
    - Retourne: résultats et indices
    """
    require_login()
    tasks = get_user_tasks()
    results = []
    indices = []

    # Choisir critère
    criteria = None
    while True:
        console.print("[blue]Recherche par :[/blue] (1) ID  (2) Titre  (3) Date  (Enter pour annuler)")
        choice = typer.prompt("Votre choix").strip()
        if choice == "":
            console.print("[yellow]Action annulée.[/yellow]")
            return [], []
        if choice not in ["1", "2", "3"]:
            console.print("[red]❌ Choix invalide, essayez encore.[/red]")
            continue
        criteria = choice
        break

    if criteria == "1":
        id_input = typer.prompt("Entrez l'ID de la tâche (1-based, Enter pour annuler)").strip()
        if id_input == "":
            console.print("[yellow]Action annulée.[/yellow]")
            return [], []
        try:
            id_num = int(id_input)
            if 1 <= id_num <= len(tasks):
                results = [tasks[id_num - 1]]
                indices = [id_num - 1]
            else:
                console.print("[red]❌ ID hors limites[/red]")
        except ValueError:
            console.print("[red]❌ ID doit être un nombre[/red]")
    elif criteria == "2":
        search_title = typer.prompt("Entrez le titre à rechercher (Enter pour annuler)").strip()
        if search_title == "":
            console.print("[yellow]Action annulée.[/yellow]")
            return [], []
        for idx, t in enumerate(tasks):
            if search_title.lower() in t["title"].lower():
                results.append(t)
                indices.append(idx)
    elif criteria == "3":
        search_date = typer.prompt("Entrez la date YYYY-MM-DD à rechercher (Enter pour annuler)").strip()
        if search_date == "":
            console.print("[yellow]Action annulée.[/yellow]")
            return [], []
        for idx, t in enumerate(tasks):
            if t["created_at"].startswith(search_date):
                results.append(t)
                indices.append(idx)

    if not results:
        console.print("[yellow]Aucune tâche trouvée.[/yellow]")
        return [], []

    table = Table(title="Résultats de recherche")
    table.add_column("ID", style="cyan")
    table.add_column("Titre", style="white")
    table.add_column("Description", style="white")
    table.add_column("Date", style="magenta")
    table.add_column("Statut", style="green")
    for i, t in enumerate(results):
        status = "✅ Fait" if t["done"] else "❌ En attente"
        table.add_row(str(i+1), t["title"], t["description"], t["created_at"], status)
    console.print(table)


    if for_modify_delete and criteria in ["2", "3"]:
        while True:
            id_choice = typer.prompt("Entrez l'ID pour confirmer la ligne (Enter pour annuler)").strip()
            if id_choice == "":
                console.print("[yellow]Action annulée.[/yellow]")
                return [], []
            try:
                id_choice = int(id_choice) - 1
                if 0 <= id_choice < len(results):
                    # Retourner seulement la tâche choisie
                    return [results[id_choice]], [indices[id_choice]]
                else:
                    console.print("[red]❌ ID invalide[/red]")
            except ValueError:
                console.print("[red]❌ ID doit être un nombre[/red]")

    return results, indices


# ==========================
#      AUTHENTIFICATION
# ==========================

@auth_app.command("register")
def register():
    users = load_json(USERS_FILE, {})
    username = ask_non_empty("Nom d'utilisateur")
    if username in users:
        console.print("[red]❌ Ce nom d'utilisateur existe déjà ![/red]")
        raise typer.Exit()
    password = getpass.getpass("Mot de passe: ").strip()
    if not password:
        console.print("[red]❌ Le mot de passe ne peut pas être vide ![/red]")
        raise typer.Exit()
    users[username] = {"password": password}
    save_json(USERS_FILE, users)
    console.print(f"[green]✅ Compte créé pour {username} ![/green]")
    console.print("Connectez-vous avec : python todo.py auth login")


@auth_app.command("login")
def login():
    global current_user
    users = load_json(USERS_FILE, {})
    username = ask_non_empty("Nom d'utilisateur")
    password = getpass.getpass("Mot de passe: ").strip()
    if username not in users or users[username]["password"] != password:
        console.print("[red]❌ Nom d'utilisateur ou mot de passe incorrect ![/red]")
        raise typer.Exit()
    current_user["username"] = username
    save_session(username)
    console.print(f"[green]🔓 Connecté en tant que {username}[/green]")


@auth_app.command("logout")
def logout():
    global current_user
    username = current_user["username"] or load_session()
    if username:
        clear_session()
        current_user["username"] = None
        console.print(f"[green]🔒 Déconnecté : {username}[/green]")
    else:
        console.print("[yellow]Vous n'étiez pas connecté.[/yellow]")


# ==========================
#          TÂCHES
# ==========================

@tasks_app.command("add")
def add():
    require_login()
    tasks = get_user_tasks()
    title = ask_non_empty("Titre de la tâche")
    description = ask_multiline("Description de la tâche")
    created_at = ask_date("Date et heure (YYYY-MM-DD HH:MM, vide = maintenant)")
    task = {"title": title, "description": description, "done": False, "created_at": created_at}
    tasks.append(task)
    save_user_tasks(tasks)
    console.print(f"[green]✅ Tâche '{title}' ajoutée ![/green]")


@tasks_app.command("list")
def list_tasks():
    require_login()
    tasks = get_user_tasks()
    if not tasks:
        console.print("[yellow]Aucune tâche.[/yellow]")
        return
    table = Table(title=f"Tâches de {current_user['username']}")
    table.add_column("ID", style="cyan")
    table.add_column("Titre", style="white")
    table.add_column("Description", style="white")
    table.add_column("Date", style="magenta")
    table.add_column("Statut", style="green")
    for i, t in enumerate(tasks):
        status = "✅ Fait" if t["done"] else "❌ En attente"
        table.add_row(str(i+1), t["title"], t["description"], t["created_at"], status)
    console.print(table)


@tasks_app.command("edit")
def edit():
    require_login()
    tasks = get_user_tasks()
    results, indices = search_tasks_interactive(for_modify_delete=True)
    if not results:
        return

    task_idx = indices[0]
    task = tasks[task_idx]

    console.print(f"Titre actuel : {task['title']}")
    new_title = typer.prompt("Nouveau titre (laisser vide pour garder)") or task['title']
    task["title"] = new_title

    console.print(f"Description actuelle :\n{task['description']}")
    new_desc = ask_multiline("Nouvelle description (laisser vide pour garder)") or task['description']
    task["description"] = new_desc

    console.print(f"Date actuelle : {task['created_at']}")
    new_date = typer.prompt("Nouvelle date YYYY-MM-DD HH:MM (laisser vide pour garder)") or task['created_at']
    try:
        dt = datetime.strptime(new_date, "%Y-%m-%d %H:%M")
        task["created_at"] = dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        if new_date != task['created_at']:
            console.print("[yellow]Format invalide, date inchangée[/yellow]")

    if confirm_action(f"Confirmer la modification de la tâche '{task['title']}' ?"):
        save_user_tasks(tasks)
        console.print("[green]✏️ Tâche modifiée ![/green]")
    else:
        console.print("[yellow]Modification annulée.[/yellow]")


@tasks_app.command("delete")
def delete():
    require_login()
    tasks = get_user_tasks()
    results, indices = search_tasks_interactive(for_modify_delete=True)
    if not results:
        return

    task_idx = indices[0]
    task = tasks[task_idx]

    if confirm_action(f"Confirmer la suppression de la tâche '{task['title']}' ?"):
        tasks.pop(task_idx)
        save_user_tasks(tasks)
        console.print(f"[green]🗑️ Tâche supprimée ![/green]")
    else:
        console.print("[yellow]Suppression annulée.[/yellow]")


@tasks_app.command("done")
def done():
    require_login()
    tasks = get_user_tasks()
    results, indices = search_tasks_interactive(for_modify_delete=True)
    if not results:
        return
    task_idx = indices[0]
    tasks[task_idx]["done"] = True
    save_user_tasks(tasks)
    console.print(f"[green]✅ Tâche '{tasks[task_idx]['title']}' complétée ![/green]")


@tasks_app.command("search")
def search():
    require_login()
    search_tasks_interactive()


if __name__ == "__main__":
    username = load_session()
    if username:
        users = load_json(USERS_FILE, {})
        if username in users:
            current_user["username"] = username
    app()
