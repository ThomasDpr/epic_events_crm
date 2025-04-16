

"""
Service de gestion des utilisateurs.

Ce module encapsule toute la logique métier liée aux utilisateurs et sert d'interface 
entre les contrôleurs et le modèle de données User.
"""

from core.security import hash_password
from models.user import DepartmentType, User
from utils.logging_utils import log_error, log_success


class UserService:
    """
    Service responsable de toutes les opérations CRUD sur les utilisateurs.
    
    Cette classe implémente le pattern "Service" pour isoler la logique métier
    des contrôleurs et des modèles. Elle gère les transactions avec la base de 
    données, les validations métier et le logging des actions que j'utilise avec sentry.
    """
    def __init__(self, db_session):
        """
        Initialise le service avec une session de base de données SQLAlchemy.
                
        Args:
            db_session: Une instance de session SQLAlchemy active
        """
        self.db = db_session
    
    def get_all_users(self):
        """
        Récupère tous les utilisateurs enregistrés dans le système.
        
        Cette méthode exécute une requête SELECT sans filtre pour obtenir
        la liste complète des utilisateurs.
        
        Returns:
            list: Liste d'objets User contenant tous les utilisateurs
        """
        return self.db.query(User).all()
    
    def get_user_by_id(self, user_id):
        """
        Récupère un utilisateur spécifique par son identifiant unique.
        
        Utilise la méthode db.get() qui est optimisée pour les recherches par clé primaire.
        En cas d'erreur, la transaction est annulée avec rollback.
        
        Args:
            user_id (int): L'identifiant unique de l'utilisateur
            
        Returns:
            User: L'instance de l'utilisateur trouvé ou None si non trouvé
            
        Raises:
            Exception: Si une erreur de base de données se produit
        """
        try:
            return self.db.get(User, user_id)
        except Exception as e:
            self.db.rollback()
            raise e
    
    def create_user(self, name, email, employee_number, department, password):
        """
        Crée un nouvel utilisateur avec les informations fournies.
        
        Cette méthode:
        1. Hache le mot de passe pour le stockage sécurisé
        2. Crée une nouvelle instance User avec les données fournies
        3. Persiste l'utilisateur dans la base de données
        4. Journalise l'action pour audit
        
        Args:
            name (str): Nom complet de l'utilisateur
            email (str): Adresse email professionnelle
            employee_number (str): Numéro d'employé unique (format 6 chiffres)
            department (str): Département ('commercial', 'support', 'gestion')
            password (str): Mot de passe en clair (sera haché avant stockage)
        
        Returns:
            User: L'instance de l'utilisateur créé avec son ID généré
            
        Raises:
            Exception: En cas d'erreur de validation ou d'accès à la base de données
        """
        try:
            # Sécurisation: Le mot de passe est haché avant d'être stocké
            # pour ne jamais conserver de mot de passe en clair dans la BDD
            hashed_password = hash_password(password)
            
            # Création d'une nouvelle instance du modèle User
            # L'enum DepartmentType garantit que seules les valeurs valides sont acceptées
            user = User(
                name=name,
                email=email,
                password=hashed_password,
                employee_number=employee_number,
                department=DepartmentType(department)
            )
            
            # Persister l'utilisateur dans la base de données
            # add() prépare l'objet pour insertion
            self.db.add(user)
            # commit() confirme la transaction et enregistre définitivement l'utilisateur en BDD
            self.db.commit()
            
            # Journalisation de la création réussie pour audit et monitoring            
            log_success(
                action="create_user",
                extra_data={
                    "user_name": name,
                    "user_email": email,
                    "user_department": department,
                    # On vérifie si c'est le premier admin créé pour l'informer via sentry                
                    "is_first_admin": (department == "gestion" and self.db.query(User).count() == 1)
                },
                message=f"Utilisateur créé avec succès: {user.name} ({user.email})"
            )
            
            return user
            
        except Exception as e:
            # En cas d'erreur, on annule toutes les modifications en cours
            # pour maintenir la cohérence de la base de données
            self.db.rollback()
            
            # Journalisation de l'erreur pour diagnostic et suivi            
            log_error(
                action="create_user",
                exception=e,
                extra_data={
                    "user_name": name,
                    "user_email": email,
                    "user_department": department
                }
            )
            # On propage l'erreur au contrôleur qui pourra la gérer
            raise e 

    def get_users_by_department(self, department):
        """
        Filtre les utilisateurs par département.
        
        Cette méthode est utilisée pour obtenir tous les membres d'un département
        spécifique, par exemple pour l'assignation de tâches ou la gestion d'équipe.
        
        Args:
            department (DepartmentType): Le département à filtrer (enum DepartmentType)
            
        Returns:
            list: Liste des utilisateurs appartenant au département spécifié
            
        Raises:
            Exception: Si l'accès à la base de données échoue
        """
        try:
            # Requête avec filtre sur le département
            # filter() est utilisé pour ajouter une clause WHERE dans la requête SQL
            return self.db.query(User).filter(User.department == department).all()
        except Exception as e:
            # Annulation des modifications en cas d'erreur            
            self.db.rollback()
            raise e 

    def update_user(self, user_id, **user_data):
        """
        Met à jour les informations d'un utilisateur existant.
        
        Cette méthode utilise les arguments nommés (**kwargs) pour permettre
        la mise à jour partielle - seuls les champs fournis sont modifiés.
        
        Points importants:
        - Une vérification spéciale est faite lors de l'attribution du rôle "gestion"
        - Le mot de passe, s'il est fourni, est haché avant stockage
        - Les modifications sont journalisées pour audit
        
        Args:
            user_id (int): ID de l'utilisateur à mettre à jour
            **user_data: Dictionnaire des champs à mettre à jour
                Clés possibles: name, email, employee_number, department, password
            
        Returns:
            User: L'utilisateur après mise à jour
            
        Raises:
            ValueError: Si l'utilisateur n'existe pas
            Exception: Si la mise à jour échoue pour d'autres raisons
        """
        try:
            # Récupération de l'utilisateur par son ID
            # Si l'utilisateur n'existe pas, user sera None
            user = self.db.get(User, user_id)
            if not user:
                raise ValueError(f"Utilisateur avec ID {user_id} non trouvé.")
            
            # Détection si + de privilèges
            # On note spécifiquement quand un utilisateur obtient des droits supplémentaires            
            was_gestion_department_granted = False
            if 'department' in user_data and user_data['department'] == 'gestion' and user.department.value != 'gestion':
                was_gestion_department_granted = True
            
            # Mise à jour conditionnelle des attributs fournis
            # Seuls les champs présents dans user_data seront modifiés
            if 'name' in user_data:
                user.name = user_data['name']
            
            if 'email' in user_data:
                user.email = user_data['email']
            
            if 'employee_number' in user_data:
                user.employee_number = user_data['employee_number']
            
            if 'department' in user_data:
                user.department = DepartmentType(user_data['department'])

            # Cas spécial: le mot de passe doit être haché avant stockage
            if 'password' in user_data and user_data['password']:
                user.password = hash_password(user_data['password'])
            
            # Persistance des modifications
            self.db.add(user)
            self.db.commit()
            
            # Préparation des données pour la journalisation
            log_data = {
                "user_id": user_id,
                "user_name": user.name,
                "user_email": user.email,
                "user_department": user.department.value,
                "updated_fields": list(user_data.keys())
            }
            
            # Message différent si des privilèges + ont été accordés            
            if was_gestion_department_granted:
                log_data["was_gestion_department_granted"] = True
                message = f"ATTENTION: Privilèges admin accordés à l'utilisateur {user.name} ({user_id})"
            else:
                message = f"Utilisateur mis à jour avec succès: {user.name} ({user_id})"
            
            # Journalisation de la mise à jour            
            log_success(
                action="update_user",
                extra_data=log_data,
                message=message
            )
            
            return user
            
        except Exception as e:
            # Annulation des modifications en cas d'erreur            
            self.db.rollback()
            
            # Journalisation de l'erreur pour diagnostic et suivi            
            log_error(
                action="update_user",
                exception=e,
                extra_data={
                    "user_id": user_id,
                    # On utilise locals() pour vérifier si user_data est défini
                    # (en cas d'erreur très tôt dans la fonction)                    
                    "updated_fields": list(user_data.keys()) if 'user_data' in locals() else None
                }
            )
            raise e 

    def delete_user(self, user_id):
        """
        Supprime un utilisateur du système après vérification des dépendances.
        
        Cette méthode effectue plusieurs contrôles avant la suppression:
        1. Vérifie que l'utilisateur existe
        2. Vérifie qu'il ne s'agit pas du dernier administrateur
        3. Vérifie que l'utilisateur n'est pas associé à des clients ou événements
        
        Ces contrôles garantissent l'intégrité référentielle et le bon fonctionnement
        du système après la suppression.
        
        Args:
            user_id (int): ID de l'utilisateur à supprimer
            
        Returns:
            bool: True si la suppression a réussi
            
        Raises:
            ValueError: Si l'utilisateur ne peut pas être supprimé pour une raison métier
            Exception: Pour les autres erreurs techniques
        """
        try:
            # Vérification de l'existence de l'utilisateur
            user = self.db.get(User, user_id)
            if not user:
                raise ValueError(f"Utilisateur avec ID {user_id} non trouvé.")
            
            # Règle métier pensée: on doit toujours garder au moins un gars dans le dep gestion
            
            if user.department == DepartmentType.GESTION:
                # Compte le nombre d'utilisateurs du département Gestion
                gestion_users_count = self.db.query(User).filter(User.department == DepartmentType.GESTION).count()
                if gestion_users_count <= 1:
                    raise ValueError("Impossible de supprimer le dernier utilisateur de gestion.")
            
            # Import des modèles ici pour éviter les références circulaires
            from models.client import Client
            from models.event import Event

            # Vérification des dépendances: clients associés
            # Cette vérification empêche de supprimer un utilisateur qui gère des clients
            clients = self.db.query(Client).filter(Client.sales_contact_id == user_id).first()
            if clients:
                raise ValueError("Impossible de supprimer cet utilisateur car il est associé à un ou plusieurs clients.")
            
            
            # Vérification des dépendances: événements associés
            # Cette vérification empêche de supprimer un utilisateur assigné à des événements
            events = self.db.query(Event).filter(Event.support_contact_id == user_id).first()
            if events:
                raise ValueError("Impossible de supprimer cet utilisateur car il est associé à un ou plusieurs événements.")
            
            # Suppression effective de l'utilisateur après toutes les vérifications
            self.db.delete(user)
            self.db.commit()
            
            # Journalisation de la suppression pour audit
            log_success(
                action="delete_user",
                extra_data={
                    "user_id": user_id,
                    "user_name": user.name,
                    "user_email": user.email,
                    "user_department": user.department.value
                },
                message=f"Utilisateur supprimé avec succès: {user.name} ({user_id})"
            )
            
            return True
            
        except Exception as e:
            # Annulation des modifications en cas d'erreur            
            self.db.rollback()
            
            # Journalisation de l'erreur pour diagnostic et suivi            
            log_error(
                action="delete_user",
                exception=e,
                extra_data={
                    "user_id": user_id
                }
            )
            raise e 