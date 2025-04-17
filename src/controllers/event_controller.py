from models.user import DepartmentType
from utils.inquire_utils import select_with_back
from utils.print_utils import PrintUtils


class EventController:
    """
    Contrôleur qui gère les opérations sur les événements.
    """
    
    def __init__(self, event_service, contract_service, user_service, event_view, db, current_user=None):
        """
        Initialise le contrôleur des événements.
        
        Args:
            event_service: Service pour les opérations sur les événements
            contract_service: Service pour les opérations sur les contrats
            user_service: Service pour les opérations sur les utilisateurs
            event_view: Vue pour l'affichage des événements
            db: Session de base de données
            current_user: Utilisateur actuellement connecté
        """
        self.event_service = event_service
        self.contract_service = contract_service
        self.user_service = user_service
        self.view = event_view
        self.db = db
        self.current_user = current_user
        self.print_utils = PrintUtils()
    
    def list_events(self, all=False, read_only=False):
        try:
            events = []

            if read_only:
                events = self.event_service.get_all_events()
                self.view.display_events_list(events, self.db, show_message=True, department_type=None)
                return
            
            department = self.current_user.department
            
            if department == DepartmentType.COMMERCIAL:
                if all:
                    events = self.event_service.get_all_events()                    
            elif department == DepartmentType.SUPPORT:
                if all:
                    events = self.event_service.get_all_events()
                else:
                    events = self.event_service.get_events_by_support(self.current_user.id)
                    
            elif department == DepartmentType.GESTION:
                if all:
                    events = self.event_service.get_all_events()
 
            
            self.view.display_events_list(events, self.db, department_type=department)
            
        except Exception as e:
            self.view.show_error_message(f"Erreur lors de l'affichage des événements: {str(e)}")
    
    def create_event(self):
        """
        Gère le processus de création d'un événement.
        """
        try:
            # Vérifier que l'utilisateur courant est connecté
            if not self.current_user:
                self.view.show_error_message("Vous devez être connecté pour créer un événement.")
                input("\nAppuyez sur Entrée pour continuer...")
                return
            
            # Vérifier les permissions
            if self.current_user.department not in [DepartmentType.COMMERCIAL, DepartmentType.GESTION]:
                self.view.show_error_message("Seuls les commerciaux et l'équipe de gestion peuvent créer des événements.")
                input("\nAppuyez sur Entrée pour continuer...")
                return
            
            # Récupérer les contrats selon le rôle
            contracts = []
            if self.current_user.department == DepartmentType.GESTION:
                # Pour la gestion, tous les contrats signés
                all_contracts = self.contract_service.get_all_contracts()
                contracts = [c for c in all_contracts if c.is_signed]
            elif self.current_user.department == DepartmentType.COMMERCIAL:
                # Pour un commercial, ses contrats signés
                commercial_contracts = self.contract_service.get_contracts_by_commercial(self.current_user.id)
                contracts = [c for c in commercial_contracts if c.is_signed]
            
            # Sélection d'un contrat
            contract_id = self.view.select_contract_for_event(contracts, self.db)
            
            # Si l'utilisateur a annulé l'opération
            if not contract_id:
                return
            
            # Collecter les données pour l'événement
            event_data = self.view.collect_event_data()
            
            # Si l'utilisateur a annulé l'opération
            if not event_data:
                return
            
            # Créer l'événement
            new_event = self.event_service.create_event(
                contract_id=contract_id,
                event_start_date=event_data["event_start_date"],
                event_end_date=event_data["event_end_date"],
                location=event_data["location"],
                attendees=event_data["attendees"],
                notes=event_data["notes"]
            )
            
            # Afficher le message de succès
            self.print_utils.print_success(f"Événement créé avec succès! ID: {new_event.id}")
            
            from utils.logging_utils import log_success
            log_success(
                action="create_event",
                message=f"Événement créé avec succès (ID: {new_event.id})",
                user_id=self.current_user.id,
                event_id=new_event.id,
                contract_id=contract_id,
                location=event_data["location"],
                start_date=event_data["event_start_date"].strftime("%d/%m/%Y %H:%M"),
                end_date=event_data["event_end_date"].strftime("%d/%m/%Y %H:%M"),
                attendees=event_data["attendees"]
            )
            
            input("\nAppuyez sur Entrée pour continuer...")
            
        except ValueError as e:
            # Erreur métier contrôlée
            self.print_utils.print_error(str(e))
            from utils.logging_utils import log_error
            log_error(
                action="create_event",
                exception=e,
                user_id=self.current_user.id if self.current_user else None,
                contract_id=contract_id if 'contract_id' in locals() else None,
                event_data=event_data if 'event_data' in locals() else None
            )
            input("\nAppuyez sur Entrée pour continuer...")
        except Exception as e:
            # Autres erreurs
            self.print_utils.print_error(f"Erreur lors de la création de l'événement: {str(e)}")
            from utils.logging_utils import log_error
            log_error(
                action="create_event",
                exception=e,
                user_id=self.current_user.id if self.current_user else None
            )
            input("\nAppuyez sur Entrée pour continuer...")
    
    def update_event(self):
        """
        Gère le processus de modification d'un événement, de façon similaire à la modification d'un client.
        """
        try:
            # Vérifier que l'utilisateur courant est connecté
            if not self.current_user:
                self.print_utils.print_error("Vous devez être connecté pour modifier un événement.")
                input("\nAppuyez sur Entrée pour continuer...")
                return
            
            # Récupérer les événements selon le rôle
            events = []
            
            if self.current_user.department == DepartmentType.GESTION:
                # Pour la gestion, tous les événements
                events = self.event_service.get_all_events()
            elif self.current_user.department == DepartmentType.COMMERCIAL:
                # Pour un commercial, les événements liés à ses clients
                contracts = self.contract_service.get_contracts_by_commercial(self.current_user.id)
                
                for contract in contracts:
                    contract_events = self.event_service.get_events_by_contract(contract.id)
                    events.extend(contract_events)
            elif self.current_user.department == DepartmentType.SUPPORT:
                # Pour un support, les événements qui lui sont assignés
                events = self.event_service.get_events_by_support(self.current_user.id)
            
            # Si aucun événement n'est disponible
            if not events:
                self.print_utils.print_warning("Aucun événement disponible pour modification.")
                input("\nAppuyez sur Entrée pour continuer...")
                return
            
            # Sélection d'un événement
            event_id = self.view.select_event_to_modify(events, self.db)
            
            # Si l'utilisateur a annulé l'opération
            if not event_id:
                return
            
            # Récupérer l'événement sélectionné
            event = self.event_service.get_event_by_id(event_id)
            
            # Vérifier les permissions spécifiques
            if self.current_user.department == DepartmentType.SUPPORT and event.support_contact_id != self.current_user.id:
                self.print_utils.print_error("Vous ne pouvez modifier que les événements qui vous sont assignés.")
                input("\nAppuyez sur Entrée pour continuer...")
                return
            
            # Affichage des détails actuels
            self.view.display_event_details(event, self.db)
                        
            from InquirerPy import inquirer
            from InquirerPy.base.control import Choice
            
            choices = [
                Choice(value="event_start_date", name="Date et heure de début"),
                Choice(value="event_end_date", name="Date et heure de fin"),
                Choice(value="location", name="Lieu"),
                Choice(value="attendees", name="Nombre de participants"),
                Choice(value="notes", name="Notes"),
                Choice(value=None, name="Annuler")
            ]
            
            field = inquirer.select(
                message="Que souhaitez-vous modifier ?",
                choices=choices,
                style=self.view.custom_style,
                qmark="",
                amark=""
            ).execute()
            
            # Si l'utilisateur a annulé
            if not field:
                return
            
            # Collecter la nouvelle valeur
            current_value = getattr(event, field)
            new_value = self.view.collect_new_value(field, current_value, event)
            
            # Si l'utilisateur a annulé ou la validation a échoué
            if new_value is None:
                self.view.show_warning_message("Modification annulée ou valeur invalide.")
                input("\nAppuyez sur Entrée pour continuer...")
                return
            
            # Mettre à jour l'événement
            updates = {field: new_value}
            updated_event = self.event_service.update_event(event_id, **updates)
            
            # Afficher les détails mis à jour
            self.view.clear_screen()
            self.print_utils.print_success(f"Champ '{field}' mis à jour avec succès!")
            self.view.console.print("\n[bold cyan]DÉTAILS MIS À JOUR[/bold cyan]")
            self.view.display_event_details(updated_event, self.db)
            
            input("\nAppuyez sur Entrée pour continuer...")
            
        except ValueError as e:
            self.print_utils.print_error(str(e))
            input("\nAppuyez sur Entrée pour continuer...")
        except Exception as e:
            self.print_utils.print_error(f"Erreur lors de la modification de l'événement: {str(e)}")
            input("\nAppuyez sur Entrée pour continuer...")
    
    def assign_event(self):
        """
        Gère le processus d'assignation d'un événement à un membre de l'équipe support.
        """
        try:
            # Vérifier que l'utilisateur courant est connecté
            if not self.current_user:
                self.print_utils.print_error("Vous devez être connecté pour assigner un événement.")
                input("\nAppuyez sur Entrée pour continuer...")
                return
            
            # Vérifier les permissions
            if self.current_user.department != DepartmentType.GESTION:
                self.print_utils.print_error("Seule l'équipe de gestion peut assigner des événements.")
                input("\nAppuyez sur Entrée pour continuer...")
                return
            
            # Récupération des événements
            events = self.event_service.get_all_events()
            
            # Sélection de l'événement à assigner
            event_id = self.view.select_event_for_assignment(events, self.db)
            
            # Si l'utilisateur a annulé l'opération
            if not event_id:
                return
            
            # Récupération de l'événement sélectionné
            event = self.event_service.get_event_by_id(event_id)
            
            # Récupération des membres de l'équipe support
            support_staff = self.user_service.get_users_by_department(DepartmentType.SUPPORT)
            
            if not support_staff:
                self.print_utils.print_error("Il semble qu'aucun membre de l'équipe support n'est été créé.\n")
                self.print_utils.print_warning("Veuillez au préalable créer un membre de l'équipe support.")
                select_with_back()
                return
            
            old_support_id = event.support_contact_id
            old_support_name = "Aucun"
            
            # Afficher le contact support actuel si l'événement en a un
            if old_support_id:
                old_support = self.user_service.get_user_by_id(old_support_id)
                old_support_name = old_support.name if old_support else f"ID: {old_support_id}"
                self.print_utils.print_warning(f"Contact support actuel: {old_support_name}")
            
            # Sélection du membre de l'équipe support
            support_id = self.view.select_support_staff(support_staff, self.db)
            
            # Si l'utilisateur a annulé l'opération
            if not support_id:
                return
            
            # Assignation de l'événement
            updated_event = self.event_service.assign_event(event_id, support_id)
            
            # Récupération du nom du support pour l'affichage
            support_user = self.user_service.get_user_by_id(support_id)
            support_name = support_user.name if support_user else f"Support ID: {support_id}"
            
            # Affichage du message de succès
            action = "réassigné" if event.support_contact_id else "assigné"
            self.print_utils.print_success(f"Événement {action} avec succès à {support_name}!")
            
            from utils.logging_utils import log_success
            log_success(
                action="assign_event",
                message=f"Événement {event_id} {action} à {support_name}",
                user_id=self.current_user.id,
                event_id=event_id,
                old_support_id=old_support_id,
                old_support_name=old_support_name,
                new_support_id=support_id,
                new_support_name=support_name
            )

            input("\nAppuyez sur Entrée pour continuer...")
            
        except ValueError as e:
            # Erreur métier contrôlée
            self.print_utils.print_error(str(e))
            
            from utils.logging_utils import log_error
            log_error(
                action="assign_event",
                exception=e,
                user_id=self.current_user.id if self.current_user else None,
                event_id=event_id if 'event_id' in locals() else None,
                support_id=support_id if 'support_id' in locals() else None
            )
            
            input("\nAppuyez sur Entrée pour continuer...")
        except Exception as e:
            # Autres erreurs
            self.print_utils.print_error(f"Erreur lors de l'assignation de l'événement: {str(e)}")
            from utils.logging_utils import log_error
            log_error(
                action="assign_event",
                exception=e,
                user_id=self.current_user.id if self.current_user else None,
                event_id=event_id if 'event_id' in locals() else None
            )
            input("\nAppuyez sur Entrée pour continuer...")
    
    def delete_event(self):
        """
        Gère le processus de suppression d'un événement.
        """
        try:
            # Vérifier que l'utilisateur courant est connecté
            if not self.current_user:
                self.print_utils.print_error("Vous devez être connecté pour supprimer un événement.")
                input("\nAppuyez sur Entrée pour continuer...")
                return
            
            # Vérifier les permissions
            if self.current_user.department not in [DepartmentType.GESTION]:
                self.print_utils.print_error("Seule l'équipe de gestion peut supprimer des événements.")
                input("\nAppuyez sur Entrée pour continuer...")
                return
            
            # Récupération des événements
            events = self.event_service.get_all_events()
            
            # Sélection de l'événement à supprimer
            event_id = self.view.select_event_to_delete(events, self.db)
            
            # Si l'utilisateur a annulé l'opération
            if not event_id:
                return
            
            # Récupération de l'événement sélectionné
            event = self.event_service.get_event_by_id(event_id)
            
            # Demander confirmation
            confirmed = self.view.confirm_deletion(event, self.db)
            
            if not confirmed:
                self.print_utils.print_warning("Suppression annulée.")
                input("\nAppuyez sur Entrée pour continuer...")
                return
            
            # Supprimer l'événement
            self.event_service.delete_event(event_id)
            
            # Afficher le message de succès
            self.print_utils.print_success(f"Événement {event_id} supprimé avec succès!")
            
            input("\nAppuyez sur Entrée pour continuer...")
            
        except ValueError as e:
            # Erreur métier contrôlée
            self.print_utils.print_error(str(e))
            input("\nAppuyez sur Entrée pour continuer...")
        except Exception as e:
            # Autres erreurs
            self.print_utils.print_error(f"Erreur lors de la suppression de l'événement: {str(e)}")
            input("\nAppuyez sur Entrée pour continuer...") 