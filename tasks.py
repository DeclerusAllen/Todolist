import typer
from rich.table import Table
from datetime import datetime
from getpass import getpass
from config import console, TASKS_FILE, current_user
from utils import load_json, save_json, require_login, ask_non_empty, ask_date, ask_multiline, confirm_action

tasks_app = typer.Typer(help="Gestion des tâches (après connexion)")

# ==========================
#  Fonctions pour les tâches
# ==========================
def get_user_tasks():
    tasks = load_json(TASKS_FILE, {})
    return tasks.get(current_user["username"], [])

def save_user_tasks(user_tasks):
    tasks = load_json(TASKS_FILE, {})
    tasks[current_user["username"]] = user_tasks
    save_json(TASKS_FILE, tasks)

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
                    return [results[id_choice]], [indices[id_choice]]
                else:
                    console.print("[red]❌ ID invalide[/red]")
            except ValueError:
                console.print("[red]❌ ID doit être un nombre[/red]")

    return results, indices

# ==========================
#  Commandes Typer
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
