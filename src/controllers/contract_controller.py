from models.user import DepartmentType
from utils.inquire_utils import select_with_back
from utils.print_utils import PrintUtils


class ContractController:
    """
    Contrôleur responsable de la coordination entre les vues et les services
    pour la gestion des contrats.
    """
    
    def __init__(self, contract_service, client_service, contract_view, db_session, current_user=None):
        """
        Initialise le contrôleur contrat.
        
        Args:
            contract_service: Service de gestion des contrats
            client_service: Service de gestion des clients
            contract_view: Vue pour l'affichage et la collecte des informations
            db_session: Session de base de données pour les requêtes
            current_user: Utilisateur actuellement connecté
        """
        self.contract_service = contract_service
        self.client_service = client_service
        self.view = contract_view
        self.db = db_session
        self.current_user = current_user
        self.print_utils = PrintUtils()

    def list_contracts(self, all=False):
        """
        Affiche la liste des contrats.
        
        Args:
            all (bool): Si True, affiche tous les contrats, sinon uniquement ceux de l'utilisateur courant
        """
        try:
            # Récupération des contrats selon les permissions
            if not all and self.current_user and self.current_user.department == DepartmentType.COMMERCIAL:
                # Pour un commercial, uniquement ses contrats
                contracts = self.contract_service.get_commercial_contracts(self.current_user.id)
            else:
                # Pour les autres, tous les contrats
                contracts = self.contract_service.get_all_contracts()
            
            # Affichage des contrats
            self.view.display_contracts_list(contracts, self.db)
            
                        
        except Exception as e:
            self.print_utils.print_error(f"Erreur lors de la récupération des contrats: {str(e)}")
            input("\nAppuyez sur Entrée pour continuer...")
    
    def create_contract(self):
        """
        Gère le processus de création d'un nouveau contrat.
        """
        try:
            # Vérifier que l'utilisateur courant est connecté
            if not self.current_user:
                self.print_utils.print_error("Vous devez être connecté pour créer un contrat.")
                input("\nAppuyez sur Entrée pour continuer...")
                return
            
            # Vérifier les permissions
            if self.current_user.department not in [DepartmentType.COMMERCIAL, DepartmentType.GESTION]:
                self.print_utils.print_error("Seuls les commerciaux et l'équipe de gestion peuvent créer des contrats.")
                input("\nAppuyez sur Entrée pour continuer...")
                return
            
            # Récupération des clients selon le département
            if self.current_user.department == DepartmentType.COMMERCIAL:
                # Pour un commercial, uniquement ses clients
                clients = self.client_service.get_commercial_clients(self.current_user.id)
            else:
                # Pour la gestion, tous les clients
                clients = self.client_service.get_all_clients()
            
            # Sélection du client pour le contrat
            client_id = self.view.select_client_for_contract(
                clients, 
                self.db, 
                is_management=(self.current_user.department == DepartmentType.GESTION)
            )
            
            # Si l'utilisateur a annulé l'opération
            if not client_id:
                return
            
            # Récupération du client sélectionné
            client = self.client_service.get_client_by_id(client_id)
            
            # Affichage des contrats existants pour ce client
            existing_contracts = self.contract_service.get_client_contracts(client_id)
            self.view.display_client_contracts(client, existing_contracts, self.db)
            
            # Collecte des données du contrat
            contract_data = self.view.collect_contract_data()
            
            # Si l'utilisateur a annulé l'opération
            if not contract_data:
                return
            
            # Création du contrat
            contract = self.contract_service.create_contract(
                client_id=client_id,
                total_amount=contract_data["total_amount"],
                remaining_amount=contract_data["remaining_amount"],
                is_signed=contract_data["is_signed"]
            )
            
            # Affichage du message de succès dans un tableau Rich
            self.print_utils.print_success(f"Contrat créé avec succès pour {client.full_name}!")
            
            # Création d'un tableau pour afficher les détails du contrat
            
            self.view.display_contract_details(contract, client, self.db)
            
            select_with_back()
            
        except Exception as e:
            self.print_utils.print_error(f"Erreur lors de la création du contrat: {str(e)}")
            select_with_back()
    
    def update_contract(self):
        """
        Gère le processus de modification d'un contrat existant.
        """
        try:
            # Vérifier que l'utilisateur courant est connecté
            if not self.current_user:
                self.print_utils.print_error("Vous devez être connecté pour modifier un contrat.")
                input("\nAppuyez sur Entrée pour continuer...")
                return
            
            # Récupération des contrats selon le département
            if self.current_user.department == DepartmentType.COMMERCIAL:
                # Pour un commercial, uniquement ses contrats
                contracts = self.contract_service.get_commercial_contracts(self.current_user.id)
            else:
                # Pour la gestion, tous les contrats
                contracts = self.contract_service.get_all_contracts()
            
            # Sélection du contrat à modifier
            contract_id = self.view.select_contract_to_modify(contracts, self.db)
            
            # Si l'utilisateur a annulé l'opération
            if not contract_id:
                return
            
            # Récupération du contrat sélectionné
            contract = self.contract_service.get_contract_by_id(contract_id)
            
            # Récupération du client associé
            client = self.client_service.get_client_by_id(contract.client_id)
            
            # Boucle de modification
            while True:
                self.view.clear_screen()
                
                # Affichage du titre
                title_table = self.view.rich_components.create_title_table("MODIFICATION D'UN CONTRAT")
                self.view.console.print(title_table)
                self.view.console.print("\n")
                
                # Affichage des détails du contrat actuel
                contract_info_table = self.view.rich_components.create_contract_info_table(contract, self.db)
                self.view.console.print(contract_info_table)
                self.view.console.print("\n")
                
                # Sélection du champ à modifier
                field_to_modify = self.view.select_field_to_modify()
                
                # Si l'utilisateur a choisi de revenir au menu
                if not field_to_modify:
                    break
                
                # Récupération de la valeur actuelle
                current_value = getattr(contract, field_to_modify)
                
                # Collecte de la nouvelle valeur
                new_value = self.view.collect_new_value(field_to_modify, current_value, contract)
                
                # Si l'utilisateur a annulé ou la validation a échoué
                if new_value is None:
                    continue
                
                # Mise à jour du contrat
                update_data = {field_to_modify: new_value}
                contract = self.contract_service.update_contract(contract.id, **update_data)
                
                
        except Exception as e:
            self.print_utils.print_error(f"Erreur lors de la modification du contrat: {str(e)}")
            input("\nAppuyez sur Entrée pour continuer...")
    
    def delete_contract(self):
        """
        Gère le processus de suppression d'un contrat existant.
        """
        try:
            # Vérifier que l'utilisateur courant est connecté
            if not self.current_user:
                self.print_utils.print_error("Vous devez être connecté pour supprimer un contrat.")
                input("\nAppuyez sur Entrée pour continuer...")
                return
            
            # Vérifier les permissions
            if self.current_user.department != DepartmentType.GESTION:
                self.print_utils.print_error("Seule l'équipe de gestion peut supprimer des contrats.")
                input("\nAppuyez sur Entrée pour continuer...")
                return
            
            # Récupération de tous les contrats
            contracts = self.contract_service.get_all_contracts()
            
            # Sélection du contrat à supprimer
            contract_id = self.view.select_contract_to_delete(contracts, self.db)
            
            # Si l'utilisateur a annulé l'opération
            if not contract_id:
                return
            
            # Récupération du contrat sélectionné
            contract = self.contract_service.get_contract_by_id(contract_id)
            
            # Récupération du client associé
            client = self.client_service.get_client_by_id(contract.client_id)
            client_name = client.full_name if client else "Client inconnu"
            
            # Demande de confirmation
            if not self.view.confirm_deletion(contract, client_name):
                self.print_utils.print_warning("Suppression annulée.")
                input("\nAppuyez sur Entrée pour continuer...")
                return
            
            # Suppression du contrat
            success = self.contract_service.delete_contract(contract_id)
            
            if success:
                # Affichage du message de succès
                self.print_utils.print_success(f"Contrat {contract_id} supprimé avec succès!")
            else:
                self.print_utils.print_error("Échec de la suppression du contrat.")
            
            input("\nAppuyez sur Entrée pour continuer...")
            
        except ValueError as e:
            # Erreur métier contrôlée (par exemple, contrat avec événements associés)
            self.print_utils.print_error(str(e))
            input("\nAppuyez sur Entrée pour continuer...")
        except Exception as e:
            # Autres erreurs
            self.print_utils.print_error(f"Erreur lors de la suppression du contrat: {str(e)}")
            input("\nAppuyez sur Entrée pour continuer...") 