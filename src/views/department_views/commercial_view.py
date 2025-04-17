from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from rich.console import Console
from rich.table import Table, box

from utils.inquire_utils import select_with_back

from .base_department_view import BaseDepartmentView


class CommercialView(BaseDepartmentView):
    def show_department_menu(self):
        """
        Affiche le menu principal pour le département commercial.
        Cette méthode remplace show_commercial_menu dans main.py.
        """
        while True:
            self.main_view.clear_screen()
            
            console = Console()
            
            dashboard_table = self.main_view.create_dashboard_table(
                self.user.department, 
                self.user
            )
            
            console.print(dashboard_table)
            
            choices = [
                Choice(value="client_management", name="Gestion des clients"),
                Choice(value="contract_management", name="Gestion de mes contrats"),
                Choice(value="event_management", name="Gestion des événements"),
            ]
            
            longest_choice_length = max(len(choice.name) for choice in choices)
            choices.append(Separator(line="─" * (longest_choice_length)))
            choices.append(Choice("logout", "Se déconnecter"))
            choices.append(Choice("exit", "Quitter l'application"))
            
            action = inquirer.select(
                message="\nQue souhaitez-vous faire ?\n",
                choices=choices,
                style=self.custom_style,
                qmark="",
                amark="",
                show_cursor=False,
                long_instruction="\nDans le département commercial, vous pouvez gérer vos clients, vos contrats et voir tous les événements."
            ).execute()
            
            # Traiter l'action sélectionnée
            if action == "client_management":
                self.show_client_management_menu()
            elif action == "contract_management":
                self.show_contract_management_menu()
            elif action == "event_management":
                self.show_event_management_menu()
            elif action == "logout":
                return "logout"
            elif action == "exit":
                return "exit"
    
    def show_client_management_menu(self):
        """Sous-menu de gestion des clients pour les commerciaux"""
        stay_in_menu = True
        
        while stay_in_menu:
            self.main_view.clear_screen()
            
            title_table = self.create_title_table("GESTION DES CLIENTS", "dark_green")
            self.console.print(title_table)
            self.console.print("\n")
            
            choices = [
                Choice(value="list_owned_clients", name="Liste de mes clients"),
                Choice(value="list_all_clients", name="Liste de tous les clients"),
                Choice(value="create_client", name="Créer un nouveau client"),
                Choice(value="update_client", name="Modifier un client"),
                Choice(value="back", name="Retour au menu principal"),
            ]
            
            action = self.create_submenu(
                choices,
                "Que souhaitez-vous faire ?\n",
                "Vous pouvez consulter la liste de tous les clients ainsi que la liste de vos clients, créer ou modifier vos clients."
            )
            
            if action == "list_owned_clients":
                self.parent.client_controller.list_clients()
                
            elif action == "list_all_clients":
                self.parent.client_controller.list_clients(all=True)
                
            elif action == "create_client":
                self.parent.client_controller.create_client()
                
                
            elif action == "update_client":
                self.parent.client_controller.update_client()
                
            elif action == "back":
                stay_in_menu = False
                return
    
    def show_contract_management_menu(self):
        """Sous-menu de gestion des contrats pour les commerciaux"""
        stay_in_menu = True
        
        while stay_in_menu:
            self.main_view.clear_screen()
            
            title_table = self.create_title_table("GESTION DE MES CONTRATS", "dark_green")
            self.console.print(title_table)
            self.console.print("\n")
            
            choices = [
                Choice(value="list_contracts", name="Liste de mes contrats"),
                Choice(value="create_contract", name="Créer un nouveau contrat"),
                Choice(value="update_contract", name="Modifier un contrat"),
                Choice(value="back", name="Retour au menu principal"),
            ]
            
            #
            action = self.create_submenu(
                choices,
                "Que souhaitez-vous faire ?\n",
                "Vous pouvez consulter, créer ou modifier vos contrats."
            )
            
            if action == "list_contracts":
                self.parent.contract_controller.list_contracts()
                select_with_back()
                
            elif action == "create_contract":
                self.parent.contract_controller.create_contract()
                
            elif action == "update_contract":
                self.parent.contract_controller.update_contract()
                
            elif action == "back":
                stay_in_menu = False
                return
    
    def show_event_management_menu(self):
        stay_in_menu = True
        
        while stay_in_menu:
            self.main_view.clear_screen()
            
            
            title_table = self.create_title_table("GESTION DES ÉVÉNEMENTS", "dark_green")
            self.console.print(title_table)
            self.console.print("\n")
            
            choices = [
                Choice(value="list_all_events", name="Liste de tous les événements"),
                Choice(value="create_event", name="Créer un nouvel événement"),
                Choice(value="back", name="Retour au menu principal"),
            ]
            
            
            action = self.create_submenu(
                choices,
                "Que souhaitez-vous faire ?\n",
                "Vous pouvez consulter tous les événements ou créer un nouvel événement lié à vos contrats."
            )
            
            if action == "list_all_events":
                self.parent.event_controller.list_events(all=True, read_only=True)
                select_with_back()
                
            elif action == "create_event":
                self.parent.event_controller.create_event()
                
            elif action == "back":
                stay_in_menu = False
                return
    
