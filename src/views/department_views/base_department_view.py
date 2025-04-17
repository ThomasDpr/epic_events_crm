from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from rich.console import Console
from rich.table import Table, box


class BaseDepartmentView:
    def __init__(self, main_view, user, parent=None):
        self.main_view = main_view
        self.user = user
        self.parent = parent 
        self.console = Console()
        self.custom_style = main_view.custom_style
    
    def display_dashboard(self):
        """Affiche le tableau de bord pour le département"""
        dashboard_table = self.main_view.create_dashboard_table(
            self.user.department, 
            self.user
        )
        self.console.print(dashboard_table)
    
    def create_menu(self, choices, message, instruction=""):
        """Crée un menu avec les choix fournis"""
        longest_choice_length = max(len(choice.name) for choice in choices)
        separator_index = len(choices)
        choices.append(Separator(line="─" * longest_choice_length))
        choices.append(Choice(value="logout", name="Se déconnecter"))
        choices.append(Choice(value="exit", name="Quitter l'application"))
        
        return inquirer.select(
            message=message,
            choices=choices,
            style=self.custom_style,
            qmark="",
            amark="",
            show_cursor=False,
            long_instruction=instruction
        ).execute()
        
    def create_submenu(self, choices, message, instruction=""):
        """
        Crée un sous-menu avec séparateur avant l'option de retour.
        
        Args:
            choices (list): Liste des choix du menu
            message (str): Message à afficher pour le menu
            instruction (str): Instructions supplémentaires pour le menu
            color (str): Couleur du sous-menu (par défaut: "dark_green")
            
        Returns:
            str: La valeur de l'action sélectionnée
        """
        longest_choice_length = max(len(choice.name) for choice in choices)
        
        choices.insert(len(choices) - 1, Separator(line="─" * (longest_choice_length)))
        
        return inquirer.select(
            message=message,
            choices=choices,
            style=self.custom_style,
            qmark="",
            amark="",
            show_cursor=False,
            long_instruction=instruction,
        ).execute()
        
    def create_title_table(self, title, color="dark_green"):
        """
        Crée une table de titre pour les sous-menus.
        
        Args:
            title (str): Le titre à afficher
            color (str): La couleur du titre (par défaut: "dark_green")
            
        Returns:
            Table: Table Rich contenant le titre formaté
        """
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
        
