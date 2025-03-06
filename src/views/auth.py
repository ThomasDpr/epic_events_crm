import re

import click

from core.auth import AuthManager
from core.security import hash_password, validate_password
from database.config import SessionLocal
from models.client import Client
from models.contract import Contract
from models.event import Event
from models.user import DepartmentType, User


@click.group()
def auth():
    """Commandes d'authentification"""
    pass

@auth.command()
@click.option('--email', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
def login(email: str, password: str):
    """Se connecter au système"""
    db = SessionLocal()
    auth_manager = AuthManager(db)
    
    user = auth_manager.authenticate(email, password)
    if user:
        click.echo(f"Connexion réussie! Bienvenue {user.name}")
    else:
        click.echo("Email ou mot de passe incorrect")


@auth.command()
def whoami():
    """Affiche l'utilisateur actuellement connecté"""
    db = SessionLocal()
    auth_manager = AuthManager(db)
    
    user = auth_manager.get_current_user()
    if user:
        click.echo(f"Utilisateur connecté: {user.name}")
        click.echo(f"Email: {user.email}")
        click.echo(f"Département: {user.department.value}")
        click.echo(f"Numéro d'employé: {user.employee_number}")
    else:
        click.echo("Aucun utilisateur connecté")
    
    db.close()


@auth.command()
def logout():
    """Se déconnecter du système"""
    db = SessionLocal()
    auth_manager = AuthManager(db)
    auth_manager.logout()
    click.echo("Déconnexion réussie")
    
    




def validate_email(ctx, param, value):
    """Valide le format de l'email et vérifie s'il existe déjà dans la base de données"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, value):
        raise click.BadParameter('Format d\'email invalide')
    
    # Vérification de l'existence de l'email dans la base de données
    db = SessionLocal()
    if db.query(User).filter(User.email == value).first():
        db.close()
        raise click.BadParameter('Cet email existe déjà')
    
    db.close()
    
        # with get_db() as db:
        # if db.query(User).filter(User.email == value).first():
        #     raise click.BadParameter('Cet email existe déjà')
    
    return value

def validate_employee_number(ctx, param, value):
    """Valide le numéro d'employé"""
    if len(value) < 3:
        raise click.BadParameter('Le numéro d\'employé doit contenir au moins 3 caractères')
    
    db = SessionLocal()
    if db.query(User).filter(User.employee_number == value).first():
        db.close()
        raise click.BadParameter('Ce numéro d\'employé existe déjà')
    
    db.close()
    return value

def prompt_for_password(ctx, param, value):
    """Gère la saisie et la validation du mot de passe"""
    click.echo("\nLe mot de passe doit contenir :")
    click.echo("- Au moins 8 caractères")
    click.echo("- Au moins une majuscule")
    click.echo("- Au moins une minuscule")
    click.echo("- Au moins un chiffre\n")
    
    while True:
        password = click.prompt('Password', hide_input=True)
        try:
            validate_password(None, None, password)
            confirm = click.prompt('Repeat password', hide_input=True)
            if password == confirm:
                return password
            click.echo('Les mots de passe ne correspondent pas')
        except click.BadParameter as e:
            click.echo(str(e))

@auth.command()
@click.option('--name', prompt=True, help='Nom complet')
@click.option('--email', prompt=True, callback=validate_email, help='Adresse email')
@click.option('--password', callback=prompt_for_password, help='Mot de passe')
@click.option('--employee-number', prompt=True, callback=validate_employee_number,
              help='Numéro d\'employé unique')
@click.option('--department', type=click.Choice(['commercial', 'support', 'gestion'], 
              case_sensitive=False), prompt=True)
def create_user(name: str, email: str, password: str, employee_number: str, department: str):
    """Créer un nouvel utilisateur"""
    db = SessionLocal()
    
    # Vérifier si l'email existe déjà
    if db.query(User).filter(User.email == email).first():
        db.close()
        raise click.BadParameter('Cet email existe déjà')
    
    # Vérifier si le numéro d'employé existe déjà
    if db.query(User).filter(User.employee_number == employee_number).first():
        db.close()
        raise click.BadParameter('Ce numéro d\'employé existe déjà')

    try:
        hashed_password = hash_password(password)
        user = User(
            name=name,
            email=email,
            password=hashed_password,
            employee_number=employee_number,
            department=DepartmentType(department)
        )
        db.add(user)
        db.commit()
        click.echo(f"Utilisateur {name} créé avec succès!")
    except Exception as e:
        db.rollback()
        click.echo(f"Erreur lors de la création de l'utilisateur: {str(e)}")
    finally:
        db.close()