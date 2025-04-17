from models.user import DepartmentType
from utils.inquire_utils import select_with_back
from utils.print_utils import PrintUtils


class ClientController:
    """
    Contrôleur responsable de la coordination entre les vues et les services
    pour la gestion des clients.
    """
    
    def __init__(self, client_service, client_view, db_session, current_user=None):
        """
        Initialise le contrôleur client.
        
        Args:
            client_service (ClientService): Service de gestion des clients
            client_view (ClientView): Vue pour l'affichage et la collecte des informations
            db_session: Session de base de données pour les requêtes
            current_user: Utilisateur actuellement connecté
        """
        self.service = client_service
        self.view = client_view
        self.db = db_session
        self.current_user = current_user
        self.print_utils = PrintUtils()
    
    def list_clients(self, all=False):
        """
        Affiche la liste des clients.
        
        Args:
            all (bool): Si True, affiche tous les clients, sinon uniquement ceux de l'utilisateur courant
        """
        try:
            # Récupération des clients selon le filtre
            if all or not self.current_user:
                clients = self.service.get_all_clients()
            else:
                clients = self.service.get_commercial_clients(self.current_user.id)
            
            # Affichage des clients
            self.view.display_clients_list(clients, self.db)
            
            select_with_back()
            
        except Exception as e:
            self.print_utils.print_error(f"Erreur lors de la récupération des clients: {str(e)}")
            input("\nAppuyez sur Entrée pour continuer...")
    
    def create_client(self):
        """
        Gère le processus de création d'un nouveau client.
        """
        try:
            # Vérifier que l'utilisateur courant est connecté
            if not self.current_user:
                self.print_utils.print_error("Vous devez être connecté pour créer un client.")
                select_with_back()
                return
            
            # Vérifier si l'utilisateur est un commercial
            if self.current_user.department != DepartmentType.COMMERCIAL:
                self.print_utils.print_error("Seuls les commerciaux peuvent créer des clients.")
                select_with_back()
                return
            
            # Affichage du formulaire de création et collecte des données
            client_data = self.view.show_client_creation_form(self.current_user.id, self.db)
            
            # Si l'utilisateur a annulé l'opération
            if not client_data:
                return
            
            # Création du client via le service
            client = self.service.create_client(**client_data)
            
            
            # Affichage de la liste mise à jour
            clients = self.service.get_commercial_clients(self.current_user.id)
            self.view.display_clients_list(clients, self.db)
            
            # Affichage du message de succès
            self.print_utils.print_success(f"Client {client.full_name} créé avec succès!")
            
            # Affichage du message de succès pour Sentry
            from utils.logging_utils import log_success
            log_success(
                action="create_client",
                message=f"Client {client.full_name} créé avec succès!",
                user_id=self.current_user.id,
                client_id=client.id,
                client_name=client.full_name,
                client_email=client.email
            )    
            select_with_back()
        except Exception as e:
            self.print_utils.print_error(f"Erreur lors de la création du client: {str(e)}")
            from utils.logging_utils import log_error
            log_error(
                action="create_client",
                exception=e,
                user_id=self.current_user.id if self.current_user else None,
                client_data=client_data if 'client_data' in locals() else None
            )
    
    def update_client(self):
        """
        Gère le processus de modification d'un client existant.
        """
        try:
            
            if not self.current_user:
                self.print_utils.print_error("Vous devez être connecté pour modifier un client.")
                select_with_back()
                return
            
            # Récupération des clients selon les permissions
            if self.current_user.department != DepartmentType.COMMERCIAL:
                self.print_utils.print_error("Seuls les commerciaux peuvent modifier des clients.")
                select_with_back()
                return
            
            # Récupération des clients dont l'utilisateur est le commercial
            clients = self.service.get_commercial_clients(self.current_user.id)

            if not clients:
                self.print_utils.print_error("Vous n'avez pas de client à modifier")
                select_with_back()
                return
            
             # Sélection du client à modifier
            client_id = self.view.select_client_to_update(clients)
            
            if not client_id:
                return
            
            # Récupération du client sélectionné
            client = self.service.get_client_by_id(client_id)
            
            if not client:
                self.print_utils.print_error(f"Client avec ID {client_id} non trouvé")
                input("\nAppuyez sur Entrée pour continuer...")
                return
            
            if client.sales_contact_id != self.current_user.id:
                self.print_utils.print_error("Vous n'avez pas le droit de modifier ce client.")
                select_with_back()
                return
            
            # Boucle de modification
            while True:
                # Affichage du formulaire de modification
                update_data = self.view.show_client_update_form(client, self.db)
                
                # Si l'utilisateur a choisi de revenir au menu ou n'a pas modifié le champ
                if not update_data:
                    break
                
                # Mise à jour du client via le service
                try:
                    field_name = list(update_data.keys())[0]
                    old_value = getattr(client, field_name)
                    updated_client = self.service.update_client(client.id, **update_data)
                    
                    # Mise à jour de la référence locale
                    client = updated_client
                    
                    # Affichage du message de succès
                    field_display = {
                        "full_name": "Nom complet",
                        "email": "Email",
                        "phone": "Téléphone",
                        "company_name": "Nom de l'entreprise"
                    }
                    self.print_utils.print_success(f"{field_display.get(field_name, field_name)} modifié avec succès!")
                    
                    # Journalisation avec logging_utils
                    from utils.logging_utils import log_success
                    log_success(
                        action="update_client",
                        message=f"Client {client.full_name} mis à jour - champ: {field_display.get(field_name, field_name)}",
                        user_id=self.current_user.id,
                        client_id=client.id,
                        client_name=client.full_name,
                        field_modified=field_name,
                        old_value=old_value,
                        new_value=update_data[field_name]
                    )
                                        
                except Exception as e:
                    self.print_utils.print_error(f"Erreur lors de la modification: {str(e)}")
                    from utils.logging_utils import log_error
                    log_error(
                        action="update_client",
                        exception=e,
                        user_id=self.current_user.id,
                        client_id=client.id if 'client' in locals() else None,
                        field_name=field_name if 'field_name' in locals() else None,
                        update_data=update_data if 'update_data' in locals() else None
                    )
                    input("\nAppuyez sur Entrée pour continuer...")
            
        except Exception as e:
            self.print_utils.print_error(f"Erreur lors de la modification du client: {str(e)}")
            input("\nAppuyez sur Entrée pour continuer...")
    
    def reassign_client(self):
        """
        Gère le processus de réassignation d'un client à un autre commercial.
        """
        try:
            
            # Vérifier que l'utilisateur est connecté
            if not self.current_user:
                self.print_utils.print_error("Vous devez être connecté pour réassigner un client.")
                select_with_back()
                return
        
            # Vérifier que l'utilisateur est du département Gestion
            if self.current_user.department != DepartmentType.GESTION:
                self.print_utils.print_error("Seule la gestion peut réassigner des clients.")
                select_with_back()
                return
            
            # Récupération de tous les clients
            clients = self.service.get_all_clients()
            
            if not clients:
                self.print_utils.print_error("Aucun client trouvé dans la base de données")
                input("\nAppuyez sur Entrée pour continuer...")
                return
            
            # Sélection du client à réassigner
            client_id = self.view.select_client_to_reassign(clients, self.db)
            
            if not client_id:
                return
            
            # Récupération du client sélectionné
            client = self.service.get_client_by_id(client_id)
            
            if not client:
                self.print_utils.print_error(f"Client avec ID {client_id} non trouvé")
                input("\nAppuyez sur Entrée pour continuer...")
                return
            
            # Récupération de tous les commerciaux
            commercials = self.service.get_available_commercials()
            
            if not commercials:
                self.print_utils.print_error("Aucun commercial trouvé dans la base de données")
                input("\nAppuyez sur Entrée pour continuer...")
                return
            
            # Sélection du nouveau commercial
            commercial_id = self.view.select_commercial_for_reassignment(commercials)
            
            if not commercial_id:
                return
            
            # Réassignation du client via le service
            try:
                old_commercial_id = client.sales_contact_id
                
                updated_client = self.service.reassign_client(client_id, commercial_id)
                
                # Récupérer les informations du nouveau commercial pour le message
                commercial = next((c for c in commercials if c.id == commercial_id), None)
                
                # Affichage du message de succès
                self.print_utils.print_success(f"Client {updated_client.full_name} réassigné à {commercial.name} avec succès!")
                
                from utils.logging_utils import log_success
                log_success(
                    action="reassign_client",
                    message=f"Client {updated_client.full_name} réassigné à {commercial.name}",
                    user_id=self.current_user.id,
                    client_id=updated_client.id,
                    client_name=updated_client.full_name,
                    old_commercial_id=old_commercial_id,
                    new_commercial_id=commercial_id,
                    new_commercial_name=commercial.name
                )
                input("\nAppuyez sur Entrée pour continuer...")
                
            except Exception as e:
                self.print_utils.print_error(f"Erreur lors de la réassignation du client: {str(e)}")
                
                from utils.logging_utils import log_error
                log_error(
                    action="reassign_client",
                    exception=e,
                    user_id=self.current_user.id,
                    client_id=client_id,
                    commercial_id=commercial_id
                )
                input("\nAppuyez sur Entrée pour continuer...")
            
        except Exception as e:
            self.print_utils.print_error(f"Erreur lors de la réassignation du client: {str(e)}")
            input("\nAppuyez sur Entrée pour continuer...")