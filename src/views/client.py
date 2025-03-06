import click
from sqlalchemy.orm import Session

from core.auth import AuthManager
from database.config import SessionLocal
from models.client import Client
from models.user import DepartmentType, User


@click.group()
def client():
    """Commandes de gestion des clients"""
    pass


def get_current_user():
    """Récupère l'utilisateur actuellement connecté"""
    db = SessionLocal()
    auth_manager = AuthManager(db)
    user = auth_manager.get_current_user()
    if not user:
        db.close()
        raise click.UsageError("Vous devez être connecté pour effectuer cette action")
    return user, db


def check_permission(user, department=None):
    """Vérifie si l'utilisateur a les permissions nécessaires"""
    if department and user.department != department:
        raise click.UsageError(f"Seuls les membres du département {department.value} peuvent effectuer cette action")
    return True


@client.command()
@click.option('--full-name', prompt=True, help='Nom complet du client')
@click.option('--email', prompt=True, help='Email du client')
@click.option('--phone', prompt=True, help='Numéro de téléphone du client')
@click.option('--company-name', prompt=True, help='Nom de l\'entreprise du client')
def create(full_name, email, phone, company_name):
    """Créer un nouveau client"""
    user, db = get_current_user()
    
    # Seuls les commerciaux peuvent créer des clients
    check_permission(user, DepartmentType.COMMERCIAL)
    
    try:
        # Vérifier si l'email existe déjà
        if db.query(Client).filter(Client.email == email).first():
            click.echo("Un client avec cet email existe déjà")
            db.close()
            return
        
        # Créer le client
        client = Client(
            full_name=full_name,
            email=email,
            phone=phone,
            company_name=company_name,
            sales_contact_id=user.id  # Le commercial qui crée le client en devient responsable
        )
        
        db.add(client)
        db.commit()
        click.echo(f"Client {full_name} créé avec succès!")
    except Exception as e:
        db.rollback()
        click.echo(f"Erreur lors de la création du client: {str(e)}")
    finally:
        db.close()


@client.command()
@click.option('--id', type=int, help='ID du client à afficher')
@click.option('--all', 'show_all', is_flag=True, help='Afficher tous les clients')
def list(id, show_all):
    """Lister les clients"""
    user, db = get_current_user()
    
    try:
        if id:
            # Afficher un client spécifique
            client = db.query(Client).get(id)
            if not client:
                click.echo(f"Aucun client trouvé avec l'ID {id}")
                return
            
            _display_client(client)
        elif show_all:
            # Afficher tous les clients
            clients = db.query(Client).all()
            if not clients:
                click.echo("Aucun client trouvé")
                return
            
            for client in clients:
                _display_client(client)
                click.echo("-" * 40)
        else:
            # Si l'utilisateur est un commercial, afficher ses clients
            if user.department == DepartmentType.COMMERCIAL:
                clients = db.query(Client).filter(Client.sales_contact_id == user.id).all()
                if not clients:
                    click.echo("Vous n'avez aucun client")
                    return
                
                for client in clients:
                    _display_client(client)
                    click.echo("-" * 40)
            else:
                # Pour les autres départements, afficher tous les clients
                clients = db.query(Client).all()
                if not clients:
                    click.echo("Aucun client trouvé")
                    return
                
                for client in clients:
                    _display_client(client)
                    click.echo("-" * 40)
    except Exception as e:
        click.echo(f"Erreur lors de la récupération des clients: {str(e)}")
    finally:
        db.close()


def _display_client(client):
    """Affiche les détails d'un client"""
    click.echo(f"ID: {client.id}")
    click.echo(f"Nom: {client.full_name}")
    click.echo(f"Email: {client.email}")
    click.echo(f"Téléphone: {client.phone}")
    click.echo(f"Entreprise: {client.company_name}")
    click.echo(f"Date de création: {client.created_date}")
    click.echo(f"Dernier contact: {client.last_contact_date}")
    click.echo(f"Commercial: {client.sales_contact.name if client.sales_contact else 'Non assigné'}")


@client.command()
@click.option('--id', type=int, prompt=True, help='ID du client à mettre à jour')
@click.option('--full-name', help='Nouveau nom complet')
@click.option('--email', help='Nouvel email')
@click.option('--phone', help='Nouveau numéro de téléphone')
@click.option('--company-name', help='Nouveau nom d\'entreprise')
def update(id, full_name, email, phone, company_name):
    """Mettre à jour un client existant"""
    user, db = get_current_user()
    
    try:
        # Récupérer le client
        client = db.query(Client).get(id)
        if not client:
            click.echo(f"Aucun client trouvé avec l'ID {id}")
            db.close()
            return
        
        # Vérifier les permissions
        if user.department == DepartmentType.COMMERCIAL and client.sales_contact_id != user.id:
            click.echo("Vous ne pouvez mettre à jour que les clients dont vous êtes responsable")
            db.close()
            return
        
        # Mettre à jour les champs si fournis
        if full_name:
            client.full_name = full_name
        if email:
            # Vérifier si l'email existe déjà pour un autre client
            existing = db.query(Client).filter(Client.email == email, Client.id != id).first()
            if existing:
                click.echo("Un autre client utilise déjà cet email")
                db.close()
                return
            client.email = email
        if phone:
            client.phone = phone
        if company_name:
            client.company_name = company_name
        
        db.commit()
        click.echo(f"Client {client.full_name} mis à jour avec succès!")
    except Exception as e:
        db.rollback()
        click.echo(f"Erreur lors de la mise à jour du client: {str(e)}")
    finally:
        db.close()


@client.command()
@click.option('--id', type=int, prompt=True, help='ID du client à supprimer')
@click.confirmation_option(prompt='Êtes-vous sûr de vouloir supprimer ce client?')
def delete(id):
    """Supprimer un client"""
    user, db = get_current_user()
    
    # Seuls les membres de l'équipe de gestion peuvent supprimer des clients
    check_permission(user, DepartmentType.GESTION)
    
    try:
        # Récupérer le client
        client = db.query(Client).get(id)
        if not client:
            click.echo(f"Aucun client trouvé avec l'ID {id}")
            db.close()
            return
        
        # Vérifier s'il a des contrats
        if client.contracts:
            click.echo("Ce client a des contrats associés. Supprimez d'abord les contrats.")
            db.close()
            return
        
        # Supprimer le client
        db.delete(client)
        db.commit()
        click.echo(f"Client {client.full_name} supprimé avec succès!")
    except Exception as e:
        db.rollback()
        click.echo(f"Erreur lors de la suppression du client: {str(e)}")
    finally:
        db.close() 