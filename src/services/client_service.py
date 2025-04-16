from models.client import Client
from models.user import DepartmentType, User
from utils.logging_utils import log_error, log_success


class ClientService:
    """
    Service responsable de toutes les opérations CRUD sur les clients.
    
    Cette classe implémente le pattern "Service" qui sépare la logique métier
    de l'accès aux données et des interfaces utilisateur. Elle gère:
    - La création et modification des clients
    - L'assignation des commerciaux responsables
    - La validation des règles métier liées aux clients
    """
    def __init__(self, db_session):
        """
        Initialise le service avec une session de base de données SQLAlchemy.
        
        L'injection de la session permet de maintenir la cohérence transactionnelle
        et facilite les tests unitaires en permettant l'utilisation de mocks.
        
        Args:
            db_session: Session SQLAlchemy active pour les opérations de BD
        """
        self.db = db_session
    
    def get_all_clients(self):
        """
        Récupère la liste complète des clients enregistrés dans le système.
        
        Cette méthode exécute une requête SELECT simple pour obtenir
        tous les enregistrements de la table clients sans filtrage.
        
        Returns:
            list: Liste d'objets Client avec tous leurs attributs et relations
        """
        return self.db.query(Client).all()
    
    def get_client_by_id(self, client_id):
        """
        Récupère un client spécifique par son identifiant unique.
        
        Utilise la méthode db.get() qui est optimisée pour les recherches
        par clé primaire et charge également les relations associées.
        
        Args:
            client_id (int): L'identifiant unique du client recherché
            
        Returns:
            Client: L'objet client trouvé ou None si aucun client ne correspond
        """
        return self.db.get(Client, client_id)
    
    def get_commercial_clients(self, commercial_id):
        """
        Récupère tous les clients dont un commercial spécifique est responsable.
        
        Cette méthode est utilisée pour afficher le portefeuille clients d'un 
        commercial, notamment dans le tableau de bord du département commercial.
        
        Args:
            commercial_id (int): ID du commercial dont on veut les clients
            
        Returns:
            list: Liste des clients associés au commercial spécifié
        """
        # Filtre les clients où le sales_contact_id correspond au commercial demandé
        return self.db.query(Client).filter(Client.sales_contact_id == commercial_id).all()
    
    def create_client(self, full_name, email, phone, company_name, sales_contact_id):
        """
        Crée un nouveau client et l'associe à un commercial responsable.
        
        Cette méthode:
        1. Crée une nouvelle instance de Client avec les informations fournies
        2. Associe le client au commercial spécifié par son ID
        3. Persiste le nouveau client dans la base de données
        
        Args:
            full_name (str): Nom complet du client (prénom et nom)
            email (str): Adresse email professionnelle du client
            phone (str): Numéro de téléphone au format international
            company_name (str): Nom de l'entreprise du client
            sales_contact_id (int): ID du commercial qui sera responsable du client
            
        Returns:
            Client: L'objet client créé avec son ID généré
            
        Raises:
            Exception: Si la création échoue (contrainte d'unicité, erreur de BD, etc.)
        """
        try:
            # Création d'une nouvelle instance de Client            
            client = Client(
                full_name=full_name,
                email=email,
                phone=phone,
                company_name=company_name,
                sales_contact_id=sales_contact_id # On associe le client au commercial spécifié par son ID
            )
            # On ajoute le client à la session de la base de données
            # pour préparer l'insertion
            self.db.add(client)
            # On confirme l'insertion en base de données
            self.db.commit()
            
                        # Journalisation du succès
            log_success(
                action="create_client",
                extra_data={
                    "client_name": full_name,
                    "client_email": email,
                    "company_name": company_name,
                    "commercial_id": sales_contact_id
                },
                message=f"Client créé avec succès: {full_name} ({company_name})"
            )

            return client
            
        except Exception as e:
            # Annulation des modifications en cas d'erreur
            self.db.rollback()
            
            # Journalisation de l'erreur
            log_error(
                action="create_client",
                exception=e,
                extra_data={
                    "client_name": full_name,
                    "client_email": email,
                    "company_name": company_name,
                    "commercial_id": sales_contact_id
                }
            )
            
            # Propagation de l'erreur au contrôleur
            raise e
        
    def update_client(self, client_id, **kwargs):
        """
        Met à jour les informations d'un client existant.
        
        Cette méthode utilise les arguments nommés variables (**kwargs) pour
        permettre la mise à jour partielle - seuls les champs fournis sont modifiés.
        Les attributs non mentionnés conservent leur valeur actuelle.
        
        Args:
            client_id (int): ID du client à mettre à jour
            **kwargs: Attributs à modifier avec leurs nouvelles valeurs
                        Clés possibles: full_name, email, phone, company_name
            
        Returns:
            Client: L'objet client après mise à jour
            
        Raises:
            ValueError: Si le client n'existe pas
            Exception: Pour les autres erreurs (contraintes, BD, etc.)
        """
        try:
            # Récupération du client par son ID            
            client = self.get_client_by_id(client_id)
            if not client:
                raise ValueError(f"Client avec ID {client_id} non trouvé")
            
            # Mise à jour dynamique des attributs fournis uniquement
            # Cette boucle permet d'éviter d'écrire une condition pour chaque attribut
            for attr, value in kwargs.items():
                # Vérification que l'attribut existe et que la valeur n'est pas None                
                if hasattr(client, attr) and value is not None:
                    setattr(client, attr, value)
            
            # On confirme la mise à jour en base de données
            self.db.commit()
            
            # Journalisation de la mise à jour
            log_success(
                action="update_client",
                extra_data={
                    "client_id": client_id,
                    "client_name": client.full_name,
                    "updated_fields": list(kwargs.keys())
                },
                message=f"Client mis à jour: {client.full_name} ({client_id})"
            )
            
            return client
            
        except Exception as e:
            # Annulation des modifications en cas d'erreur
            self.db.rollback()
            
            # Journalisation de l'erreur
            log_error(
                action="update_client",
                exception=e,
                extra_data={
                    "client_id": client_id,
                    "updated_fields": list(kwargs.keys()) if 'kwargs' in locals() else None
                }
            )
            
            # Propagation de l'erreur
            raise e
    
    def reassign_client(self, client_id, new_commercial_id):
        """
        Change le commercial responsable d'un client.
        
        Cette opération est importante pour la gestion du portefeuille clients
        et intervient généralement lors d'un changement d'organisation ou du départ
        d'un commercial. La méthode vérifie que:
        1. Le client existe
        2. Le nouveau commercial existe
        3. L'utilisateur est bien du département commercial
        
        Args:
            client_id (int): ID du client à réassigner
            new_commercial_id (int): ID du nouveau commercial responsable
            
        Returns:
            Client: Le client mis à jour avec son nouveau commercial
            
        Raises:
            ValueError: Si le client ou le commercial n'existe pas,
                        ou si l'utilisateur n'est pas un commercial
            Exception: Pour les autres erreurs de base de données
        """
        try:
            # Vérification de l'existence du client            
            client = self.get_client_by_id(client_id)
            if not client:
                raise ValueError(f"Client avec ID {client_id} non trouvé")
            
            # Vérification de l'existence du commercial
            commercial = self.db.get(User, new_commercial_id)
            if not commercial:
                raise ValueError(f"Commercial avec ID {new_commercial_id} non trouvé")
            
            # Validation du département (règle métier: seul un commercial peut être responsable)
            if commercial.department != DepartmentType.COMMERCIAL:
                raise ValueError(f"L'utilisateur {commercial.name} n'est pas un commercial")
            
            # Sauvegarde de l'ancien commercial pour la journalisation
            old_commercial_id = client.sales_contact_id
            
            # Mise à jour de l'association
            client.sales_contact_id = new_commercial_id
            
            # Confirmation de la modification            
            self.db.commit()
            # Journalisation du changement
            log_success(
                action="reassign_client",
                extra_data={
                    "client_id": client_id,
                    "client_name": client.full_name,
                    "old_commercial_id": old_commercial_id,
                    "new_commercial_id": new_commercial_id,
                    "new_commercial_name": commercial.name
                },
                message=f"Client {client.full_name} réassigné au commercial {commercial.name}"
            )
            
            return client
            
        except Exception as e:
            # Annulation des modifications en cas d'erreur
            self.db.rollback()
            
            # Journalisation de l'erreur
            log_error(
                action="reassign_client",
                exception=e,
                extra_data={
                    "client_id": client_id,
                    "new_commercial_id": new_commercial_id
                }
            )
            
            # Propagation de l'erreur
            raise e
    
    def get_available_commercials(self):
        """
        Retourne la liste de tous les utilisateurs du département commercial.
        
        Cette méthode est utilisée notamment dans les interfaces pour:
        - Assigner un commercial à un nouveau client
        - Réassigner un client à un autre commercial
        - Afficher la liste des commerciaux disponibles
        
        Returns:
            list: Liste des utilisateurs du département commercial
        """
        # Filtre sur l'enum DepartmentType.COMMERCIAL pour ne récupérer que les commerciaux
        return self.db.query(User).filter(User.department == DepartmentType.COMMERCIAL).all()