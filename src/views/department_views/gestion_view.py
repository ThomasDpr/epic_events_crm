from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from rich.console import Console
from rich.table import Table, box

from utils.inquire_utils import select_with_back

from .base_department_view import BaseDepartmentView


class GestionView(BaseDepartmentView):
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
                Choice("user_management", "Gestion des utilisateurs"),
                Choice("contract_management", "Gestion des contrats"),
                Choice("event_management", "Gestion des événements"),
            ]
            
            longest_choice_length = max(len(choice.name) for choice in choices)
            choices.append(Separator(line="─" * longest_choice_length))
            choices.append(Choice("logout", "Se déconnecter"))
            choices.append(Choice("exit", "Quitter l'application"))
            
            action = inquirer.select(
                message="\nQue souhaitez-vous faire ?\n",
                long_instruction="Vous pouvez gérer les utilisateurs, les contrats et les événements.",
                show_cursor=False,
                choices=choices,
                style=self.custom_style,
                qmark=""
            ).execute()
            
            if action == "user_management":
                self.show_user_management_menu()
            elif action == "contract_management":
                self.show_contract_management_menu()
            elif action == "event_management":
                self.show_event_management_menu()
            elif action == "logout":
                return "logout"
            elif action == "exit":
                return "exit"
    
    def show_user_management_menu(self):
        """Sous-menu de gestion des utilisateurs"""
        stay_in_menu = True
        
        while stay_in_menu:
            self.main_view.clear_screen()
            
            title_table = self.create_title_table("GESTION DES UTILISATEURS")
            self.console.print(title_table)
            self.console.print("\n")
            
            choices = [
                Choice(value="create_user", name="Créer un utilisateur"),
                Choice(value="update_user", name="Modifier un utilisateur"),
                Choice(value="delete_user", name="Supprimer un utilisateur"),
                Choice(value="back", name="Retour au menu principal"),
            ]
            
            action = self.create_submenu(
                choices,
                "Que souhaitez-vous faire ?\n",
                "Vous pouvez lister, créer, modifier ou supprimer des utilisateurs."
            )
            
                
            if action == "create_user":
                self.parent.user_controller.create_user()
                
            elif action == "update_user":
                self.parent.user_controller.update_user()
                
            elif action == "delete_user":
                self.parent.user_controller.delete_user()
                
            elif action == "back":
                stay_in_menu = False
                return
    
    def show_contract_management_menu(self):
        """Sous-menu de gestion des contrats"""
        stay_in_menu = True
        
        while stay_in_menu:
            self.main_view.clear_screen()
            
            title_table = self.create_title_table("GESTION DES CONTRATS")
            self.console.print(title_table)
            self.console.print("\n")
            
            choices = [
                Choice(value="create_contract", name="Créer un contrat"),
                Choice(value="update_contract", name="Modifier un contrat"),
                Choice(value="back", name="Retour au menu principal"),
            ]
            
            action = self.create_submenu(
                choices,
                "Que souhaitez-vous faire ?\n",
                "Vous pouvez créer, ou modifier un contrat."
            )
                
            if action == "create_contract":
                self.parent.contract_controller.create_contract()
                
            elif action == "update_contract":
                self.parent.contract_controller.update_contract()
                
            elif action == "back":
                stay_in_menu = False
                return
    
    def show_event_management_menu(self):
        """Sous-menu de gestion des événements"""
        stay_in_menu = True
        
        while stay_in_menu:
            self.main_view.clear_screen()
            
            
            title_table = self.create_title_table(title="GESTION DES ÉVÉNEMENTS", color="magenta")
            self.console.print(title_table)
            self.console.print("\n")
            
            choices = [
                Choice(value="list_all_events", name="Liste de tous les événements"),
                Choice(value="assign_event", name="Assigner/réassigner un événement à un support"),
                Choice(value="back", name="Retour au menu principal"),
            ]
            
            action = self.create_submenu(
                choices,
                "Que souhaitez-vous faire ?\n",
                "Vous pouvez consulter ou assigner un événement à un membre du support."
            )
            
            if action == "list_all_events":
                self.parent.event_controller.list_events(all=True)
                select_with_back()
                
            elif action == "assign_event":
                self.parent.event_controller.assign_event()

            elif action == "back":
                stay_in_menu = False
                return