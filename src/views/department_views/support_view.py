from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from rich.console import Console
from rich.table import Table, box

from utils.inquire_utils import select_with_back

from .base_department_view import BaseDepartmentView


class SupportView(BaseDepartmentView):
    def show_department_menu(self):
        while True:
            self.main_view.clear_screen()
            
            console = Console()
            
            dashboard_table = self.main_view.create_dashboard_table(
                self.user.department, 
                self.user
            )
            
            console.print(dashboard_table)
            
            choices = [
                Choice("client_management", "Gestion des clients"),
                Choice("contract_management", "Gestion des contrats"),
                Choice("event_management", "Gestion des événements"),
            ]
            
            longest_choice_length = max(len(choice.name) for choice in choices)
            choices.append(Separator(line="─" * longest_choice_length))
            choices.append(Choice("logout", "Se déconnecter"))
            choices.append(Choice("exit", "Quitter l'application"))
            
            action = inquirer.select(
                message="\nQue souhaitez-vous faire ?\n",
                choices=choices,
                style=self.custom_style,
                qmark="",
                amark="",
                show_cursor=False,
                long_instruction="\nDans le département support, vous pouvez consulter tous les clients et contrats en lecture seule, et gérer vos événements assignés."
            ).execute()
            
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
        """Sous-menu de gestion des clients pour le support"""
        stay_in_menu = True
        
        while stay_in_menu:
            self.main_view.clear_screen()
            
            title_table = self.create_title_table("GESTION DES CLIENTS", "blue")
            self.console.print(title_table)
            self.console.print("\n")
            
            choices = [
                Choice(value="list_all_clients", name="Liste de tous les clients"),
                Choice(value="back", name="Retour au menu principal"),
            ]
            
            action = self.create_submenu(
                choices,
                "Que souhaitez-vous faire ?\n",
                "Vous pouvez consulter la liste de tous les clients en lecture seule."
            )
            
            if action == "list_all_clients":
                self.parent.client_controller.list_clients(all=True)
                
            elif action == "back":
                stay_in_menu = False
                return

    def show_contract_management_menu(self):
        """Sous-menu de gestion des contrats pour le support"""
        stay_in_menu = True
        
        while stay_in_menu:
            self.main_view.clear_screen()
            
            title_table = self.create_title_table("GESTION DES CONTRATS", "blue")
            self.console.print(title_table)
            self.console.print("\n")
            
            choices = [
                Choice(value="list_all_contracts", name="Liste de tous les contrats"),
                Choice(value="back", name="Retour au menu principal"),
            ]
            
            action = self.create_submenu(
                choices,
                "Que souhaitez-vous faire ?\n",
                "Vous pouvez consulter la liste de tous les contrats en lecture seule."
            )
            
            if action == "list_all_contracts":
                self.parent.contract_controller.list_contracts(all=True)
                select_with_back()
                
            elif action == "back":
                stay_in_menu = False
                return

    def show_event_management_menu(self):
        """Sous-menu de gestion des événements pour le support"""
        stay_in_menu = True
        
        while stay_in_menu:
            self.main_view.clear_screen()
            
            title_table = self.create_title_table("GESTION DES ÉVÉNEMENTS", "blue")
            self.console.print(title_table)
            self.console.print("\n")
            
            choices = [
                Choice(value="list_all_events", name="Liste de tous les événements"),
                Choice(value="my_events", name="Mes événements assignés"),
                Choice(value="update_event", name="Mettre à jour un événement"),
                Choice(value="back", name="Retour au menu principal"),
            ]
            
            action = self.create_submenu(
                choices,
                "Que souhaitez-vous faire ?\n",
                "Vous pouvez consulter tous les événements, vos événements assignés et les mettre à jour."
            )
            
            if action == "list_all_events":
                self.parent.event_controller.list_events(all=True, read_only=True)
                select_with_back()
                
            elif action == "my_events":
                self.parent.event_controller.list_events()
                select_with_back()
                
            elif action == "update_event":
                self.parent.event_controller.update_event()
                
            elif action == "back":
                stay_in_menu = False
                return

    def create_title_table(self, title, color="blue"):
        """Crée une table de titre pour les sous-menus"""
        title_table = Table(
            show_header=False,
            show_footer=False,
            box=box.ROUNDED,
            style=f"bold {color}",
            padding=(0, 1),
            expand=False,
            border_style=color
        )
        
        title_table.add_column()
        title_table.add_row(f"[bold {color}]{title}[/bold {color}]")
        
        return title_table
