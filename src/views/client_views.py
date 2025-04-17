import os

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from InquirerPy.validator import EmptyInputValidator
from rich.console import Console

from models.user import DepartmentType
from utils.print_utils import PrintUtils
from validators import ClientEmailValidator, PhoneNumberValidator
from views.components.rich_components import RichComponents


class ClientView:
    """
    Vue responsable de l'affichage et de la collecte des informations
    liées aux clients.
    """
    
    def __init__(self, custom_style=None):
        """
        Initialise la vue client.
        
        Args:
            custom_style (dict, optional): Style personnalisé pour InquirerPy
        """
        self.console = Console()
        self.custom_style = custom_style or {}
        self.rich_components = RichComponents()
        self.print_utils = PrintUtils()
    def clear_screen(self):
        """Efface l'écran (compatible avec différents OS)"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_clients_list(self, clients, db_session=None):
        """
        Affiche la liste des clients.
        
        Args:
            clients (list): Liste d'objets Client à afficher
            db_session: Session de base de données pour récupérer des informations complémentaires
        """
        self.clear_screen()
        
        
        title_table = self.rich_components.create_title_table("LISTE DES CLIENTS")
        self.console.print(title_table)
                
        if not clients:
            self.print_utils.print_error("Vous ne possédez aucun client")
        else:
            
            clients_table = self.rich_components.create_clients_table(clients, db_session)
            self.console.print(clients_table)
        
    
    def show_client_creation_form(self, current_user_id, db_session):
        """
        Affiche le formulaire de création d'un client et collecte les données.
        
        Args:
            current_user_id (int): ID de l'utilisateur courant (commercial par défaut)
            db_session: Session de base de données pour les validateurs
            
        Returns:
            dict: Dictionnaire contenant les données du nouveau client ou None si annulé
        """
        self.clear_screen()
        
        
        title_table = self.rich_components.create_title_table("CRÉATION D'UN NOUVEAU CLIENT")
        self.console.print(title_table)
        self.console.print("\n")
        
        try:
            
            from validators import ClientEmailValidator

            
            full_name = inquirer.text(
                message="Nom complet:",
                validate=EmptyInputValidator("Le nom ne peut pas être vide"),
                style=self.custom_style,
                qmark="",
                amark="",
            ).execute()
            
            email = inquirer.text(
                message="Email:",
                validate=ClientEmailValidator(db_session),  
                style=self.custom_style,
                qmark="",
                amark="",
            ).execute()
            
            phone = inquirer.text(
                message="Téléphone:",
                validate=PhoneNumberValidator(),
                style=self.custom_style,
                qmark="",
                amark="",
            ).execute()
            
            company_name = inquirer.text(
                message="Nom de l'entreprise:",
                validate=EmptyInputValidator("Le nom de l'entreprise ne peut pas être vide"),
                style=self.custom_style,
                qmark="",
                amark="",
            ).execute()
            
            
            return {
                "full_name": full_name,
                "email": email,
                "phone": phone,
                "company_name": company_name,
                "sales_contact_id": current_user_id  
            }
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Opération annulée par l'utilisateur[/yellow]")
            return None
    
    def show_client_update_form(self, client, db_session):
        """
        Affiche le formulaire de modification d'un client.
        
        Args:
            client (Client): Le client à modifier
            db_session: Session de base de données
            
        Returns:
            dict: Dictionnaire contenant les attributs modifiés ou None si annulé
        """
        self.clear_screen()
        
        
        title_table = self.rich_components.create_title_table("MODIFICATION D'UN CLIENT")
        self.console.print(title_table)
        self.console.print("\n")
        
        
        client_info_table = self.rich_components.create_client_info_table(client)
        self.console.print(client_info_table)
        self.console.print("\n")
        
        
        field_choices = [
            Choice(value="full_name", name="Modifier le nom"),
            Choice(value="email", name="Modifier l'email"),
            Choice(value="phone", name="Modifier le téléphone"),
            Choice(value="company_name", name="Modifier le nom de l'entreprise"),
            Choice(value="back", name="Retour au menu de gestion des clients")
        ]
        
        longest_choice_length = max(len(choice.name) for choice in field_choices) if field_choices else 30
        
        
        field_choices.insert(-1, Separator(line="─" * longest_choice_length))
        
        
        
        field_to_modify = inquirer.select(
            message="Que souhaitez-vous modifier ?\n",
            choices=field_choices,
            style=self.custom_style,
            qmark="",
            amark="",
            show_cursor=False,
            long_instruction="Vous pouvez modifier le nom, l'email, le téléphone ou le nom de l'entreprise",
        ).execute()
        
        
        if field_to_modify == "back":
            return None
        
        
        current_value = getattr(client, field_to_modify)
        
        
        field_display = {
            "full_name": "Nom complet",
            "email": "Email",
            "phone": "Téléphone",
            "company_name": "Nom de l'entreprise"
        }
        
        
        validations = {
            "full_name": EmptyInputValidator("Le nom ne peut pas être vide"),
            "email": ClientEmailValidator(db_session, exclude_id=client.id),
            "phone": PhoneNumberValidator(),
            "company_name": EmptyInputValidator("Le nom de l'entreprise ne peut pas être vide")
        }
        
        
        new_value = inquirer.text(
            message=f"{field_display[field_to_modify]}:",
            default=current_value,
            validate=validations[field_to_modify],
            style=self.custom_style,
            qmark="",
            amark="",
        ).execute()
        
        
        if new_value == current_value:
            return self.show_client_update_form(client, db_session)
        
        
        return {field_to_modify: new_value}
    
    def select_client_to_update(self, clients):
        """
        Affiche la liste des clients pour sélection.
        
        Args:
            clients (list): Liste des clients disponibles
            
        Returns:
            int: ID du client sélectionné ou None si annulé
        """
        
        self.clear_screen()
        
        
        title_table = self.rich_components.create_title_table("CHOIX DU CLIENT À MODIFIER")
        self.console.print(title_table)
        self.console.print("\n")
        
        
        clients_info_table = self.rich_components.create_clients_table(clients)
        self.console.print(clients_info_table)
        self.console.print("\n")
        
        
        client_choices = [
            Choice(value=client.id, name=f"{client.full_name} - {client.company_name}")
            for client in clients
        ]
        
        
        longest_choice_length = max(len(choice.name) for choice in client_choices) if client_choices else 30
        
        
        client_choices.append(Separator(line="─" * longest_choice_length))
        client_choices.append(Choice(value=None, name="Retour au menu précédent"))
        
        
        client_id = inquirer.select(
            message="Sélectionnez le client à modifier:\n",
            choices=client_choices,
            style=self.custom_style,
            qmark="",
            amark="",
            show_cursor=False,
            long_instruction="Sélectionnez le client à modifier ou choisissez 'Retour' pour revenir au menu précédent",
        ).execute()
        
        return client_id
    
    def select_client_to_reassign(self, clients, db_session):
        """
        Affiche la liste des clients pour réassignation.
        
        Args:
            clients (list): Liste des clients disponibles
            db_session: Session de base de données
            
        Returns:
            int: ID du client sélectionné ou None si annulé
        """
        from models.user import User
        
        self.clear_screen()
        
        
        title_table = self.rich_components.create_title_table("CHOIX DU CLIENT À RÉASSIGNER")
        self.console.print(title_table)
        self.console.print("\n")
        

        
        client_choices = []
        for client in clients:
            
            commercial = db_session.get(User, client.sales_contact_id)
            commercial_name = commercial.name if commercial else "Non assigné"
            client_choices.append(
                Choice(value=client.id, name=f"👤 {client.full_name} | 🏢 {client.company_name} | 📞 {client.phone} | 📧 {client.email} | 👔 (Commercial assigné: {commercial_name})")
            )
        
        
        client_choices.append(Separator(line="─" * 40))
        client_choices.append(Choice(value="cancel", name="Annuler et revenir au menu"))
        
        
        client_id = inquirer.select(
            message="Sélectionnez le client à réassigner:\n",
            choices=client_choices,
            style=self.custom_style,
            qmark="",
            amark="",
            show_cursor=False,
            long_instruction="Vous pouvez réassigner un client à un autre commercial ou annuler",
        ).execute()
        
        return client_id if client_id != "cancel" else None
    
    def select_commercial_for_reassignment(self, commercials):
        """
        Affiche la liste des commerciaux pour réassignation d'un client.
        
        Args:
            commercials (list): Liste des commerciaux disponibles
            
        Returns:
            int: ID du commercial sélectionné ou None si annulé
        """
        
        self.clear_screen()
        
        
        title_table = self.rich_components.create_title_table("CHOIX DU COMMERCIAL À ATTRIBUER")
        self.console.print(title_table)
        self.console.print("\n")
        
        
        
        
        commercial_choices = [
            Choice(
                value=commercial.id, 
                name=f"ID: {commercial.id} | 👔 {commercial.name} | 📧 {commercial.email} | 🪪 {commercial.employee_number}"
            )
            for commercial in commercials
        ]
             
        commercial_choices.append(Choice(value="cancel", name="ANNULER"))
        
        
        commercial_id = inquirer.fuzzy(
            message="Recherchez et sélectionnez le nouveau commercial responsable:\n",
            choices=commercial_choices,
            style=self.custom_style,
            qmark="",
            amark="",
            long_instruction="Vous pouvez rechercher par ID, nom, email ou numéro d'employé, ou taper 'ANNULER' pour revenir au menu",
            max_height="70%",
        ).execute()
        
        return commercial_id if commercial_id != "cancel" else None
    
