# 📝 Todolist CLI

Une application en ligne de commande (CLI) pour gérer vos tâches avec **authentification utilisateur**.  
Développée en **Python** avec [Typer](https://typer.tiangolo.com/) et [Rich](https://rich.readthedocs.io/) pour une expérience simple et agréable.  

---

## ✨ Fonctionnalités

### 🔐 Gestion des utilisateurs
- Créer un compte (**register**)  
- Se connecter (**login**)  
- Se déconnecter (**logout**)  
- Vérification stricte des entrées  

### ✅ Gestion des tâches
- Ajouter une tâche (titre, description multi-lignes, date/heure)  
- Lister toutes les tâches de l’utilisateur connecté  
- Modifier une tâche existante  
- Supprimer une tâche (avec confirmation)  
- Marquer une tâche comme terminée  
- Rechercher des tâches par **ID, titre ou date**  
- Contrôle strict des entrées et confirmation avant modification/suppression  

### 🎨 Interface CLI conviviale
- Commandes gérées avec **Typer**  
- Affichage clair et coloré avec **Rich.Table**  
- IDs affichés à partir de `1` pour plus de lisibilité  

---

## ⚙️ Installation

Cloner le repository :  
```bash
git clone https://github.com/votre-utilisateur/todolist-cli.git
cd todolist-cli
```

Créer un environnement virtuel :  
```bash
python -m venv venv
```

Activer l’environnement :  

**Windows** :  
```bash
venv\Scripts\activate
```

**macOS / Linux** :  
```bash
source venv/bin/activate
```

Installer les dépendances :  
```bash
pip install typer rich
```

---

## 🚀 Commandes principales

### 🔐 Authentification
Créer un compte :  
```bash
python todo.py auth register
```

Se connecter :  
```bash
python todo.py auth login
```

Se déconnecter :  
```bash
python todo.py auth logout
```

### ✅ Gestion des tâches (après connexion)
Ajouter une tâche :  
```bash
python todo.py tasks add
```

Lister toutes les tâches :  
```bash
python todo.py tasks list
```

Modifier une tâche :  
```bash
python todo.py tasks edit
```

Supprimer une tâche :  
```bash
python todo.py tasks delete
```

Marquer une tâche comme terminée :  
```bash
python todo.py tasks done
```

Rechercher une tâche :  
```bash
python todo.py tasks search
```

---

## 🖥️ Exemple d’utilisation

```bash
# Créer un compte
python todo.py auth register

# Connexion
python todo.py auth login

# Ajouter une tâche
python todo.py tasks add

# Lister les tâches
python todo.py tasks list

# Modifier une tâche
python todo.py tasks edit

# Supprimer une tâche
python todo.py tasks delete

# Marquer comme faite
python todo.py tasks done

# Rechercher une tâche
python todo.py tasks search
```

---

## 📂 Structure du projet

```
Todolist/
│
├─ todo.py        # Fichier principal avec toutes les commandes
├─ users.json     # Stockage des utilisateurs
├─ tasks.json     # Stockage des tâches par utilisateur
├─ session.json   # Session pour maintenir la connexion
└─ README.md      # Documentation du projet
```

---

## 🛠️ Technologies utilisées
- **Python 3.x**  
- [Typer](https://typer.tiangolo.com/) → CLI moderne et simple  
- [Rich](https://rich.readthedocs.io/) → Affichage coloré et tableaux  

---

📌 **Remarques**  
- Les IDs affichés commencent à `1` pour plus de lisibilité.  
- Toutes les actions critiques (**modification, suppression**) nécessitent une confirmation.  
- Les champs obligatoires sont strictement contrôlés pour éviter les erreurs.  
