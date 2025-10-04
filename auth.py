import typer, getpass
from config import console, USERS_FILE, current_user
from utils import clear_session, hash_password, verify_password,save_json, load_json, save_session, load_session, require_login


auth_app = typer.Typer(help="Gestion de l'authentification")

@auth_app.command("register")
def register():
    users = load_json(USERS_FILE, {})
    username = typer.prompt("Nom d'utilisateur").strip()
    if username in users:
        console.print("[red]❌ Ce nom existe déjà ![/red]")
        raise typer.Exit()
    password = getpass.getpass("Mot de passe: ").strip()
    if not password:
        console.print("[red]❌ Le mot de passe ne peut pas être vide ![/red]")
        raise typer.Exit()
    users[username] = {"password": hash_password(password)}
    save_json(USERS_FILE, users)
    console.print(f"[green]✅ Compte créé pour {username} ![/green]")

@auth_app.command("login")
def login():
    users = load_json(USERS_FILE, {})
    username = typer.prompt("Nom d'utilisateur").strip()
    password = getpass.getpass("Mot de passe: ").strip()
    if username not in users or not verify_password(password, users[username]["password"]):
        console.print("[red]❌ Nom d'utilisateur ou mot de passe incorrect ![/red]")
        raise typer.Exit()
    current_user["username"] = username
    save_session(username)
    console.print(f"[green]🔓 Connecté en tant que {username}[/green]")

@auth_app.command("logout")
def logout():
    username = current_user["username"]
    if username:
        clear_session()
        current_user["username"] = None
        console.print(f"[green]🔒 Déconnecté : {username}[/green]")
    else:
        console.print("[yellow]Pas de session active.[/yellow]")
