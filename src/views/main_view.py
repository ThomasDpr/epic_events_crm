
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

from database.config import SessionLocal
from models.user import User
from utils.logging_utils import log_error
from views.base_view import BaseView


class MainView(BaseView):
    def __init__(self):
        """Initialise la vue principale"""
        super().__init__()


    def show_success_message(self, message):
        """Affiche un message de succès"""
        self.console.print(f"\n✅ {message}", style="bold green")
        
    def show_error_message(self, message):
        """Affiche un message d'erreur"""
        self.console.print(f"❌ {message}", style="red")

    def create_dashboard_table(self, department, user):
        """
        Crée un tableau de bord adapté au département de l'utilisateur.
        
        Args:
            department: Le département de l'utilisateur (DepartmentType)
            user: L'utilisateur connecté
            
        Returns:
            Table: Un tableau rich formaté avec les données du dashboard
        """
        from rich.table import Table, box

        # Configuration spécifique par département
        department_configs = {
            "COMMERCIAL": {
                "border_style": "dark_green",
                "icon": "",
                "title_style": "dark_green"
            },
            "SUPPORT": {
                "border_style": "blue",
                "icon": "",
                "title_style": "blue"
            },
            "GESTION": {
                "border_style": "magenta", 
                "icon": "",
                "title_style": "magenta"
            },
            "DEFAULT": {  # Configuration de repli
                "border_style": "white",
                "icon": "",
                "title_style": "white"
            }
        }
        
        config = department_configs.get(department.value.upper(), department_configs["DEFAULT"])
        
        dashboard_table = Table(
            show_header=False,
            show_footer=False,
            box=box.ROUNDED,
            padding=(0, 1),
            expand=False,
            border_style=config["border_style"],
            show_lines=True
        )
        
        dashboard_table.add_column()
        
        dashboard_table.add_row(
            f"[{config['title_style']}]TABLEAU DE BORD DEPARTMENT {department.value.upper()}[/{config['title_style']}] {config['icon']}"
        )
        
        # Informations de l'utilisateur connecté
        user_info = (
            f"[bright_white]Nom[/bright_white]          : [bright_black]{user.name}[/bright_black]\n"
            f"[bright_white]Email[/bright_white]        : [bright_black]{user.email}[/bright_black]\n"
            f"[bright_white]N° Employé[/bright_white]   : [bright_black]{user.employee_number}[/bright_black]\n"
            f"[bright_white]Département[/bright_white]  : [bright_black]{user.department.value}[/bright_black]"
        )
        
        dashboard_table.add_row(user_info)
        
        return dashboard_table 