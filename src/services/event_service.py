from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

from models.contract import Contract
from models.event import Event
from models.user import DepartmentType, User
from utils.logging_utils import log_error, log_success


class EventService:
    """
    Service responsable de la gestion des événements dans le CRM Epic Events.
    
    Cette classe implémente le pattern "Service" pour isoler la logique métier liée aux
    événements. Elle gère:
    - La création et modification des événements
    - L'assignation des membres de l'équipe support
    - La validation des dates et informations logistiques
    - Les relations entre événements, contrats et équipes
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
    
    def get_all_events(self):
        """
        Récupère l'ensemble des événements enregistrés dans le système.
        
        Cette méthode est utilisée principalement par le département Gestion
        pour avoir une vue d'ensemble de tous les événements planifiés ou réalisés.
        
        Returns:
            list: Liste de tous les objets Event avec leurs relations chargées
            
        Raises:
            SQLAlchemyError: En cas d'erreur d'accès à la base de données
        """
        try:
            return self.db.query(Event).all()
        except SQLAlchemyError as e:
            self.db.rollback()
            
            log_error(
                action="get_all_events",
                exception=e
            )
            
            raise e
    
    def get_events_by_support(self, support_id):
        """
        Récupère les événements assignés à un membre spécifique de l'équipe support.
        
        Cette méthode est essentielle pour que les membres du support puissent
        visualiser leur planning d'événements, et pour que les managers puissent
        évaluer la charge de travail de chaque membre de l'équipe.
        
        Args:
            support_id (int): ID du membre de l'équipe support
            
        Returns:
            list: Liste des événements assignés à ce membre du support
            
        Raises:
            SQLAlchemyError: En cas d'erreur d'accès à la base de données
        """
        try:
            return self.db.query(Event).filter(Event.support_contact_id == support_id).all()
        except SQLAlchemyError as e:
            self.db.rollback()
            
            log_error(
                action="get_events_by_support",
                exception=e,
                extra_data={"support_id": support_id}
            )
            
            raise e
    
    def get_events_by_contract(self, contract_id):
        """
        Récupère tous les événements associés à un contrat spécifique.
        
        Cette méthode est utilisée pour visualiser l'historique ou le planning
        des événements liés à un contrat particulier, notamment pour le suivi
        client et la gestion commerciale.
        
        Args:
            contract_id (int): ID du contrat dont on veut les événements
            
        Returns:
            list: Liste des événements associés au contrat spécifié
            
        Raises:
            SQLAlchemyError: En cas d'erreur d'accès à la base de données
        """
        try:
            return self.db.query(Event).filter(Event.contract_id == contract_id).all()
        except SQLAlchemyError as e:
            self.db.rollback()
            
            log_error(
                action="get_events_by_contract",
                exception=e,
                extra_data={"contract_id": contract_id}
            )
            
            raise e
    
    def get_event_by_id(self, event_id):
        """
        Récupère un événement spécifique par son identifiant unique.
        
        Cette méthode est utilisée pour consulter les détails d'un événement
        particulier, notamment lors de la planification logistique ou de la
        modification des détails.
        
        Args:
            event_id (int): ID de l'événement à récupérer
            
        Returns:
            Event: L'objet événement correspondant à l'ID ou None s'il n'existe pas
            
        Raises:
            SQLAlchemyError: En cas d'erreur d'accès à la base de données
        """
        try:
            return self.db.get(Event, event_id)
        except SQLAlchemyError as e:
            self.db.rollback()
            
            log_error(
                action="get_event_by_id",
                exception=e,
                extra_data={"event_id": event_id}
            )
            
            raise e
    
    def create_event(self, contract_id, event_start_date, event_end_date, location, attendees, notes=None):
        """
        Crée un nouvel événement associé à un contrat existant.
        
        Cette méthode effectue plusieurs validations importantes:
        1. Vérification de l'existence du contrat
        2. Validation des dates (cohérence chronologique)
        3. Validation du nombre de participants
        
        L'événement créé n'est pas immédiatement assigné à un membre de l'équipe support;
        cette assignation se fait dans une étape ultérieure via la méthode assign_event().
        
        Args:
            contract_id (int): ID du contrat associé à l'événement
            event_start_date (datetime): Date et heure de début de l'événement
            event_end_date (datetime): Date et heure de fin de l'événement
            location (str): Lieu où se déroulera l'événement
            attendees (int/str): Nombre de participants attendus
            notes (str, optional): Informations additionnelles ou instructions
            
        Returns:
            Event: L'objet événement créé avec son ID généré
            
        Raises:
            ValueError: Si les données sont invalides (contrat inexistant, dates incohérentes, etc.)
            SQLAlchemyError: En cas d'erreur d'accès à la base de données
        """
        try:
            # Vérifier que le contrat existe
            contract = self.db.get(Contract, contract_id)
            if not contract:
                raise ValueError(f"Contrat avec ID {contract_id} non trouvé.")
            
            # Vérifier que la date de fin est après la date de début
            if event_end_date <= event_start_date:
                raise ValueError("La date de fin doit être après la date de début.")
            
            # Convertir attendees en entier si c'est une chaîne
            if isinstance(attendees, str):
                attendees = int(attendees)
            
            # Vérifier que le nombre de participants est valide
            if attendees < 1:
                raise ValueError("Le nombre de participants doit être au moins de 1.")
            
            # Créer l'événement
            new_event = Event(
                contract_id=contract_id,
                event_start_date=event_start_date,
                event_end_date=event_end_date,
                location=location,
                attendees=attendees,
                notes=notes
                # support_contact_id restera NULL jusqu'à l'assignation                
            )
            
            # Persistance dans la base de données
            self.db.add(new_event)
            self.db.commit()
            self.db.refresh(new_event)
            
            # Journalisation du succès
            log_success(
                action="create_event",
                extra_data={
                    "event_id": new_event.id,
                    "contract_id": contract_id,
                    "start_date": event_start_date.isoformat() if event_start_date else None,
                    "end_date": event_end_date.isoformat() if event_end_date else None,
                    "location": location,
                    "attendees": attendees
                },
                message=f"Événement #{new_event.id} créé pour le contrat #{contract_id}"
            )
            
            return new_event
            
        except Exception as e:
            self.db.rollback()
            
            log_error(
                action="create_event",
                exception=e,
                extra_data={
                    "contract_id": contract_id,
                    "start_date": event_start_date.isoformat() if isinstance(event_start_date, datetime) else str(event_start_date),
                    "end_date": event_end_date.isoformat() if isinstance(event_end_date, datetime) else str(event_end_date),
                    "location": location,
                    "attendees": attendees
                }
            )
            
            raise e
    
    def update_event(self, event_id, **kwargs):
        """
        Met à jour les informations d'un événement existant.
        
        Cette méthode utilise les arguments nommés variables pour permettre
        la mise à jour sélective des champs. Elle effectue des validations spécifiques
        pour garantir la cohérence des données, notamment pour:
        - Les dates (chronologie cohérente)
        - Le nombre de participants
        - L'assignation d'un contact support (doit être du département Support)
        
        Args:
            event_id (int): ID de l'événement à mettre à jour
            **kwargs: Attributs à modifier avec leurs nouvelles valeurs
                        Clés possibles: event_start_date, event_end_date, location, 
                                        attendees, notes, support_contact_id
            
        Returns:
            Event: L'objet événement après mise à jour
            
        Raises:
            ValueError: Si l'événement n'existe pas ou si les valeurs sont invalides
            SQLAlchemyError: En cas d'erreur d'accès à la base de données
        """
        try:
            event = self.db.get(Event, event_id)
            if not event:
                raise ValueError(f"Événement avec ID {event_id} non trouvé.")
            
            # Sauvegarde de l'état initial pour la journalisation
            initial_state = {
                "event_start_date": event.event_start_date,
                "event_end_date": event.event_end_date,
                "location": event.location,
                "attendees": event.attendees,
                "notes": event.notes,
                "support_contact_id": event.support_contact_id
            }
            
            # Vérifications spécifiques pour certains champs
            if 'event_start_date' in kwargs and 'event_end_date' in kwargs:
                # Si les deux dates sont fournies, s'assurer que la fin est après le début
                if kwargs['event_end_date'] <= kwargs['event_start_date']:
                    raise ValueError("La date de fin doit être après la date de début.")
            elif 'event_start_date' in kwargs:
                # Si seule la date de début est fournie, vérifier par rapport à la date de fin existante
                if isinstance(event.event_end_date, datetime) and isinstance(kwargs['event_start_date'], datetime):
                    if kwargs['event_start_date'] >= event.event_end_date:
                        raise ValueError("La date de début doit être avant la date de fin.")
            elif 'event_end_date' in kwargs:
                # Si seule la date de fin est fournie, vérifier par rapport à la date de début existante
                if isinstance(event.event_start_date, datetime) and isinstance(kwargs['event_end_date'], datetime):
                    if kwargs['event_end_date'] <= event.event_start_date:
                        raise ValueError("La date de fin doit être après la date de début.")
            
            if 'attendees' in kwargs:
                # Convertir en int si c'est une chaîne
                if isinstance(kwargs['attendees'], str):
                    kwargs['attendees'] = int(kwargs['attendees'])
                    
                if kwargs['attendees'] < 1:
                    raise ValueError("Le nombre de participants doit être au moins de 1.")
            
            if 'support_contact_id' in kwargs and kwargs['support_contact_id'] is not None:
                support = self.db.get(User, kwargs['support_contact_id'])
                if not support:
                    raise ValueError(f"Utilisateur avec ID {kwargs['support_contact_id']} non trouvé.")
                if support.department != DepartmentType.SUPPORT:
                    raise ValueError(f"L'utilisateur {support.name} n'est pas membre de l'équipe support.")
            
            # Mettre à jour les champs
            for key, value in kwargs.items():
                if hasattr(event, key):
                    setattr(event, key, value)
            
            self.db.add(event)
            self.db.commit()
            self.db.refresh(event)
            
            # Journalisation du succès
            log_success(
                action="update_event",
                extra_data={
                    "event_id": event_id,
                    "updated_fields": list(kwargs.keys()),
                    "initial_state": {k: str(v) if isinstance(v, datetime) else v for k, v in initial_state.items() if k in kwargs},
                    "new_state": {k: str(getattr(event, k)) if isinstance(getattr(event, k), datetime) else getattr(event, k) 
                                for k in kwargs.keys() if hasattr(event, k)}
                },
                message=f"Événement #{event_id} mis à jour avec succès"
            )
            
            return event
            
        except SQLAlchemyError as e:
            self.db.rollback()
            
            log_error(
                action="update_event",
                exception=e,
                extra_data={
                    "event_id": event_id,
                    "updated_fields": list(kwargs.keys()) if 'kwargs' in locals() else None
                }
            )
            
            raise e
    
    def delete_event(self, event_id):
        """
        Supprime un événement de la base de données.
        
        Cette opération est définitive et ne peut pas être annulée. Elle devrait
        être utilisée avec précaution, généralement uniquement pour des événements
        annulés ou créés par erreur.
        
        Args:
            event_id (int): ID de l'événement à supprimer
            
        Returns:
            bool: True si la suppression a réussi
            
        Raises:
            ValueError: Si l'événement n'existe pas
            SQLAlchemyError: En cas d'erreur d'accès à la base de données
        """
        try:
            event = self.db.get(Event, event_id)
            if not event:
                raise ValueError(f"Événement avec ID {event_id} non trouvé.")
            
            # Sauvegarde des informations pour la journalisation
            event_info = {
                "event_id": event.id,
                "contract_id": event.contract_id,
                "start_date": str(event.event_start_date),
                "end_date": str(event.event_end_date),
                "location": event.location,
                "support_contact_id": event.support_contact_id
            }
            
            # Suppression de l'événement
            self.db.delete(event)
            self.db.commit()
            
            # Journalisation du succès
            log_success(
                action="delete_event",
                extra_data=event_info,
                message=f"Événement #{event_id} supprimé avec succès"
            )
            
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            
            log_error(
                action="delete_event",
                exception=e,
                extra_data={"event_id": event_id}
            )
            
            raise e
    
    def assign_event(self, event_id, support_id):
        """
        Assigne ou réassigne un événement à un membre de l'équipe support.
        
        Cette méthode est cruciale pour la gestion des ressources humaines dans le CRM.
        Elle permet au département Gestion d'attribuer la responsabilité d'un événement
        à un membre spécifique de l'équipe support.
        
        La méthode vérifie que:
        1. L'événement existe
        2. Le membre du support existe
        3. L'utilisateur appartient bien au département Support
        
        Args:
            event_id (int): L'ID de l'événement à assigner
            support_id (int): L'ID du membre de l'équipe support
            
        Returns:
            Event: L'événement mis à jour avec le nouveau contact support
            
        Raises:
            ValueError: Si l'événement n'existe pas, si le support n'existe pas,
                        ou si l'utilisateur n'est pas membre de l'équipe support
            SQLAlchemyError: En cas d'erreur d'accès à la base de données
        """
        try:
            event = self.db.get(Event, event_id)
            if not event:
                raise ValueError(f"Événement avec ID {event_id} non trouvé.")
            
            support = self.db.get(User, support_id)
            if not support:
                raise ValueError(f"Utilisateur avec ID {support_id} non trouvé.")
            
            if support.department != DepartmentType.SUPPORT:
                raise ValueError(f"L'utilisateur {support.name} n'est pas membre de l'équipe support.")
            
            # Mise à jour du contact support
            event.support_contact_id = support_id
            self.db.add(event)
            self.db.commit()
            
            return event
        except Exception as e:
            self.db.rollback()
            
            log_error(
                action="assign_event",
                exception=e,
                extra_data={
                    "event_id": event_id,
                    "support_id": support_id
                }
            )
            
            raise e
    
    def get_events_by_contract_ids(self, contract_ids):
        """
        Récupère tous les événements associés à une liste d'IDs de contrats.
        
        Args:
            contract_ids (list): Liste d'IDs de contrats
            
        Returns:
            list: Liste d'objets Event
        """
        try:
            return self.db.query(Event).filter(Event.contract_id.in_(contract_ids)).all()
        except Exception as e:
            self.db.rollback()
            
            log_error(
                action="get_events_by_contract_ids",
                exception=e,
                extra_data={"contract_ids": contract_ids}
            )
            
            raise e