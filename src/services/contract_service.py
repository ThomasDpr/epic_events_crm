from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models.client import Client
from models.contract import Contract
from models.event import Event
from models.user import DepartmentType, User
from utils.logging_utils import log_error, log_success


class ContractService:
    """
    Service responsable de la gestion des contrats dans le CRM Epic Events.
    
    Cette classe implémente le pattern "Service" pour isoler la logique métier
    des contrats. Elle gère:
    - La création et modification des contrats
    - Le suivi du statut des contrats (signé, payé)
    - Les relations entre contrats, clients et commerciaux
    - Les règles métier liées aux contrats (montants, validité)
    """
    
    def __init__(self, db_session):
        """
        Initialise le service avec une session de base de données SQLAlchemy.
        
        La session est injectée pour permettre la gestion cohérente des transactions
        et faciliter les tests unitaires via l'injection de dépendances.
        
        Args:
            db_session: Session SQLAlchemy active pour interagir avec la BD
        """
        self.db = db_session
    
    def get_all_contracts(self):
        """
        Récupère l'ensemble des contrats enregistrés dans le système.
        
        Cette méthode est utilisée principalement par le département Gestion
        pour obtenir une vue globale de tous les contrats de l'entreprise.
        
        Returns:
            list: Liste de tous les objets Contract avec leurs relations chargées
            
        Raises:
            SQLAlchemyError: En cas d'erreur d'accès à la base de données
        """
        try:
            # Requête simple pour récupérer tous les contrats
            return self.db.query(Contract).all()
        except SQLAlchemyError as e:
            # Annulation de la transaction en cas d'erreur
            self.db.rollback()
            
            # Journalisation de l'erreur
            log_error(
                action="get_all_contracts",
                exception=e
            )
            
            # Propagation de l'erreur
            raise e
    
    def get_commercial_contracts(self, commercial_id):
        """
        Récupère tous les contrats dont un commercial est responsable.
        
        Cette méthode est utilisée pour afficher le portefeuille des contrats
        d'un commercial, notamment pour le suivi de performance ou l'attribution
        de commissions.
        
        Args:
            commercial_id (int): ID du commercial dont on veut les contrats
            
        Returns:
            list: Liste des contrats associés au commercial spécifié
            
        Raises:
            SQLAlchemyError: En cas d'erreur d'accès à la base de données
        """
        try:
            # Filtrage des contrats par ID du commercial
            return self.db.query(Contract).filter(Contract.sales_contact_id == commercial_id).all()
        except SQLAlchemyError as e:
            self.db.rollback()
            
            log_error(
                action="get_commercial_contracts",
                exception=e,
                extra_data={"commercial_id": commercial_id}
            )
            
            raise e
    
    def get_client_contracts(self, client_id):
        """
        Récupère tous les contrats associés à un client spécifique.
        
        Cette méthode permet de visualiser l'historique contractuel d'un client
        et est utilisée pour le suivi client et la génération de rapports commerciaux.
        
        Args:
            client_id (int): ID du client dont on veut consulter les contrats
            
        Returns:
            list: Liste des contrats associés au client
            
        Raises:
            SQLAlchemyError: En cas d'erreur d'accès à la base de données
        """
        try:
            # Filtrage des contrats par ID du client
            return self.db.query(Contract).filter(Contract.client_id == client_id).all()
        except SQLAlchemyError as e:
            self.db.rollback()
            
            log_error(
                action="get_client_contracts",
                exception=e,
                extra_data={"client_id": client_id}
            )
            
            raise e
    
    def get_contract_by_id(self, contract_id):
        """
        Récupère un contrat spécifique par son identifiant unique.
        
        Cette méthode est utilisée pour consulter les détails d'un contrat
        ou pour effectuer des opérations sur un contrat particulier (mise à jour, suppression).
        
        Args:
            contract_id (int): ID du contrat à récupérer
            
        Returns:
            Contract: L'objet contrat correspondant à l'ID ou None s'il n'existe pas
            
        Raises:
            SQLAlchemyError: En cas d'erreur d'accès à la base de données
        """
        try:
            # Utilisation de la méthode get() optimisée pour la recherche par clé primaire
            return self.db.get(Contract, contract_id)
        except SQLAlchemyError as e:
            self.db.rollback()
            
            log_error(
                action="get_contract_by_id",
                exception=e,
                extra_data={"contract_id": contract_id}
            )
            
            raise e
    
    def create_contract(self, client_id, total_amount, remaining_amount, is_signed=False):
        """
        Crée un nouveau contrat associé à un client existant.
        
        Cette méthode:
        1. Vérifie l'existence du client
        2. Récupère le commercial associé au client
        3. Crée le contrat avec les montants spécifiés
        4. Enregistre le contrat dans la base de données
        
        Args:
            client_id (int): ID du client signataire du contrat
            total_amount (float): Montant total du contrat en euros
            remaining_amount (float): Montant restant à payer (initialement égal au total)
            is_signed (bool, optional): Indique si le contrat est déjà signé. Par défaut False.
            
        Returns:
            Contract: L'objet contrat créé avec son ID généré
            
        Raises:
            ValueError: Si le client n'existe pas ou si les montants sont invalides
            SQLAlchemyError: En cas d'erreur d'accès à la base de données
        """
        try:
            # Vérification de l'existence du client
            client = self.db.get(Client, client_id)
            if not client:
                raise ValueError(f"Client avec ID {client_id} non trouvé")
            
            # Création du contrat
            # Note: On utilise automatiquement le commercial associé au client
            contract = Contract(
                client_id=client_id,
                sales_contact_id=client.sales_contact_id,
                total_amount=total_amount,
                remaining_amount=remaining_amount,
                is_signed=is_signed
            )
            
            # Persistance en base de données
            self.db.add(contract)
            self.db.commit()
            # Rafraîchissement pour obtenir l'ID généré et d'autres champs calculés
            self.db.refresh(contract)

            # Journalisation du succès
            log_success(
                action="create_contract",
                extra_data={
                    "contract_id": contract.id,
                    "client_id": client_id,
                    "commercial_id": client.sales_contact_id,
                    "total_amount": total_amount,
                    "is_signed": is_signed
                },
                message=f"Contrat #{contract.id} créé pour le client {client.full_name} ({total_amount}€)"
            )
            
            return contract
            
        except SQLAlchemyError as e:
            self.db.rollback()
            
            log_error(
                action="create_contract",
                exception=e,
                extra_data={
                    "client_id": client_id,
                    "total_amount": total_amount,
                    "remaining_amount": remaining_amount
                }
            )
            
            raise e
    
    def update_contract(self, contract_id, **kwargs):
        """
        Met à jour les informations d'un contrat existant.
        
        Cette méthode utilise les arguments nommés variables pour permettre
        la mise à jour sélective des champs. Elle est particulièrement utile pour:
        - Marquer un contrat comme signé
        - Mettre à jour le montant restant après un paiement
        - Modifier le montant total suite à un avenant
        
        Args:
            contract_id (int): ID du contrat à mettre à jour
            **kwargs: Attributs à modifier avec leurs nouvelles valeurs
                        Clés possibles: total_amount, remaining_amount, is_signed
            
        Returns:
            Contract: L'objet contrat après mise à jour
            
        Raises:
            ValueError: Si le contrat n'existe pas
            SQLAlchemyError: En cas d'erreur d'accès à la base de données
        """
        try:
            # Récupération du contrat à mettre à jour            
            contract = self.get_contract_by_id(contract_id)
            if not contract:
                raise ValueError(f"Contrat avec ID {contract_id} non trouvé")
            
            # Sauvegarde des valeurs initiales pour la journalisation
            initial_state = {
                "total_amount": contract.total_amount,
                "remaining_amount": contract.remaining_amount,
                "is_signed": contract.is_signed
            }            
            # Mettre à jour les attributs
            for key, value in kwargs.items():
                if hasattr(contract, key):
                    setattr(contract, key, value)
            
            # Confirmation des modifications
            self.db.commit()
            self.db.refresh(contract)
            
            # Journalisation du succès
            log_success(
                action="update_contract",
                extra_data={
                    "contract_id": contract_id,
                    "client_id": contract.client_id,
                    "updated_fields": list(kwargs.keys()),
                    "initial_state": initial_state,
                    "new_state": {k: getattr(contract, k) for k in kwargs.keys() if hasattr(contract, k)}
                },
                message=f"Contrat #{contract_id} mis à jour avec succès"
            )
            
            return contract
            
        except SQLAlchemyError as e:
            self.db.rollback()
            
            log_error(
                action="update_contract",
                exception=e,
                extra_data={
                    "contract_id": contract_id,
                    "updated_fields": list(kwargs.keys()) if 'kwargs' in locals() else None
                }
            )
            
            raise e
    
    def delete_contract(self, contract_id):
        """
        Supprime un contrat de la base de données.
        
        Cette méthode effectue des vérifications importantes avant la suppression:
        - Le contrat doit exister
        - Le contrat ne doit pas être associé à des événements
        
        La suppression est définitive et ne peut pas être annulée.
        
        Args:
            contract_id (int): ID du contrat à supprimer
            
        Returns:
            bool: True si la suppression a réussi
            
        Raises:
            ValueError: Si le contrat n'existe pas ou a des événements associés
            SQLAlchemyError: En cas d'erreur d'accès à la base de données
        """
        try:
            # Récupération du contrat à supprimer
            contract = self.get_contract_by_id(contract_id)
            if not contract:
                raise ValueError(f"Contrat avec ID {contract_id} non trouvé")
            
            # Vérification des dépendances: événements associés
            # Règle métier: on ne peut pas supprimer un contrat lié à des événements
            events = self.db.query(Event).filter(Event.contract_id == contract_id).all()
            if events:
                raise ValueError(f"Impossible de supprimer ce contrat car il est associé à {len(events)} événement(s)")
            
            # Sauvegarde des informations pour la journalisation
            contract_info = {
                "contract_id": contract.id,
                "client_id": contract.client_id,
                "commercial_id": contract.sales_contact_id,
                "total_amount": contract.total_amount,
                "is_signed": contract.is_signed
            }            
            # Suppression du contrat
            self.db.delete(contract)
            self.db.commit()
            
            # Journalisation du succès
            log_success(
                action="delete_contract",
                extra_data=contract_info,
                message=f"Contrat #{contract_id} supprimé avec succès"
            )
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            
            log_error(
                action="delete_contract",
                exception=e,
                extra_data={"contract_id": contract_id}
            )
            
            raise e
        
    def get_unsigned_contracts(self):
        """
        Récupère tous les contrats qui n'ont pas encore été signés.
        
        Cette méthode est particulièrement utile pour les commerciaux et 
        le département Gestion afin de suivre les contrats en attente de signature
        et prioriser les actions commerciales.
        
        Returns:
            list: Liste des contrats dont le champ is_signed est False
            
        """
        return self.db.query(Contract).filter(Contract.is_signed == False).all()
    
    def get_unpaid_contracts(self):
        """
        Récupère tous les contrats qui n'ont pas été entièrement payés.
        
        Cette méthode est essentielle pour le suivi financier, notamment pour:
        - Le recouvrement des paiements
        - L'analyse de la trésorerie
        - Le reporting financier
        
        Returns:
            list: Liste des contrats dont le montant restant à payer est supérieur à zéro
        """
        return self.db.query(Contract).filter(Contract.remaining_amount > 0).all()
    
    def get_contracts_by_commercial(self, commercial_id):
        """
        Récupère tous les contrats dont un commercial est responsable.
        
        Cette méthode est un alias de get_commercial_contracts() maintenu pour
        la compatibilité avec le code existant. Elle est utilisée notamment dans
        les tableaux de bord des commerciaux.
        
        Args:
            commercial_id (int): ID du commercial
            
        Returns:
            list: Liste des contrats associés au commercial
        """
        try:
            return self.db.query(Contract).filter(Contract.sales_contact_id == commercial_id).all()
        except Exception as e:
            self.db.rollback()
            raise e 