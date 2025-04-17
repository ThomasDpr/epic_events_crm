import os
from datetime import datetime

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from rich.console import Console
from rich.table import Table, box

from models.user import DepartmentType
from utils.inquire_utils import select_with_back
from utils.print_utils import PrintUtils
from validators import (
    AttendeesValidator,
    DateTimeFormatValidator,
    EndDateValidator,
    FutureDateValidator,
    LocationValidator,
)
from views.components.rich_components import RichComponents


class EventView:
    """
    Vue qui gère l'affichage et l'interaction pour les événements.
    """
    
    def __init__(self, custom_style=None):
        """
        Initialise la vue des événements.
        
        Args:
            custom_style (dict, optional): Style personnalisé pour InquirerPy
        """
        self.custom_style = custom_style
        self.console = Console()
        self.rich_components = RichComponents()
        self.print_utils = PrintUtils()
    def clear_screen(self):
        """Efface l'écran de la console."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_events_list(self, events, db_session=None, show_message=True, department_type=None):
        
        self.clear_screen()        
        title_table = self.rich_components.create_title_table("LISTE DES ÉVÉNEMENTS")
        self.console.print(title_table)        
        if not events and show_message:
            from models.user import DepartmentType

            if department_type == DepartmentType.COMMERCIAL:    
                self.print_utils.print_error("Aucun événement trouvé pour vos contrats.")
                self.print_utils.print_warning("Créez d'abord un contrat signé avant de pouvoir créer des événements.")
                
            elif department_type == DepartmentType.SUPPORT:    
                self.print_utils.print_error("Aucun événement ne vous a été assigné pour le moment.")
                self.print_utils.print_warning("Prenez contact avec l'équipe de gestion pour qu'ils vous assignent un événement.")
                
            elif department_type == DepartmentType.GESTION:    
                self.print_utils.print_error("Aucun événement n'existe dans le système.")
                self.print_utils.print_warning("Demandez aux commerciaux de créer des événements pour les contrats signés.")
            else:    
                self.print_utils.print_error("Aucun événement n'existe dans le système.")
                self.print_utils.print_warning("Les événements apparaîtront ici une fois créés.")
            return
                
        events_table = self.rich_components.create_events_table(events, db_session)
        self.console.print(events_table)
    
    def select_contract_for_event(self, contracts, db_session=None):
        """
        Permet la sélection d'un contrat pour la création d'un événement.
        
        Args:
            contracts (list): Liste des contrats disponibles
            db_session (Session, optional): Session de base de données pour les requêtes additionnelles
            
        Returns:
            int: ID du contrat sélectionné ou None si annulé
        """
        self.clear_screen()
                
        title_table = self.rich_components.create_title_table("SÉLECTION D'UN CONTRAT POUR L'ÉVÉNEMENT")
        self.console.print(title_table)
        
        if not contracts:
            self.print_utils.print_error("Aucun contrat disponible pour la création d'un évènement.\n")
            self.print_utils.print_warning("Vérifiez que les contrats sont bien signés.\n")
            select_with_back()
            return None
        
        
        contract_table = self.rich_components.create_contracts_table(contracts, db_session)
        self.console.print(contract_table)
        self.console.print("\n")
        
        
        choices = []
        for contract in contracts:
            client_name = "Client inconnu"
            if contract.client:
                client_name = contract.client.full_name
            
            choices.append(
                Choice(
                    value=contract.id,
                    name=f"ID: {contract.id} | Client: {client_name} | Montant: {contract.total_amount:.2f} €"
                )
            )
        
        choices.append(Choice(value=None, name="Annuler"))
        
        
        contract_id = inquirer.fuzzy(
            message="Sélectionnez un contrat pour l'événement :\n",
            choices=choices,
            style=self.custom_style,
            long_instruction="Le contrat doit être signé pour créer un événement",
            qmark="",
            amark="",
            mandatory=False,
            
        ).execute()
        
        return contract_id
    
    def collect_event_data(self):
        """
        Collecte les données pour la création d'un événement.
        
        Returns:
            dict: Données de l'événement ou None si annulé
        """
        self.clear_screen()
        
        title_table = self.rich_components.create_title_table("CRÉATION D'UN NOUVEL ÉVÉNEMENT")
        self.console.print(title_table)
        self.console.print("\n")
        
        
        try:
            start_date_str = inquirer.text(
                message="Date et heure de début (JJ/MM/AAAA HH:MM):",
                validate=FutureDateValidator(),
                style=self.custom_style,
                qmark="",
                amark="",
                long_instruction="Saisissez la date et l'heure de début de l'événement (JJ/MM/AAAA HH:MM)",
            ).execute()
        except KeyboardInterrupt:
            return None
        
        
        start_date = datetime.strptime(start_date_str, "%d/%m/%Y %H:%M")
        
        
        try:
            end_date_str = inquirer.text(
                message="Date et heure de fin (JJ/MM/AAAA HH:MM):",
                validate=EndDateValidator(start_date),
                default=start_date_str,
                style=self.custom_style,
                qmark="",
                amark="",
                long_instruction="La date et l'heure de fin doivent être postérieures à la date de début",
            ).execute()
        except KeyboardInterrupt:
            return None
        
        
        end_date = datetime.strptime(end_date_str, "%d/%m/%Y %H:%M")
        
        
        try:
            location = inquirer.text(
                message="Lieu de l'événement:",
                validate=LocationValidator(),
                style=self.custom_style,
                qmark="",
                amark="",
                long_instruction="Spécifiez l'adresse ou le lieu où se déroulera l'événement",
            ).execute()
        except KeyboardInterrupt:
            return None
        
        
        try:
            attendees_str = inquirer.number(
                message="Nombre de participants:",
                validate=AttendeesValidator(),
                min_allowed=1,
                default=1,
                float_allowed=False,
                style=self.custom_style,
                qmark="",
                amark="",
                long_instruction="Indiquez le nombre de personnes attendues à l'événement",
            ).execute()
            
            attendees = int(attendees_str)
        except KeyboardInterrupt:
            return None
        
        
        try:
            notes = inquirer.text(
                message="Notes (optionnel):",
                style=self.custom_style,
                qmark="",
                amark="",
                long_instruction="Vous pouvez ajouter des informations supplémentaires concernant l'événement",
            ).execute()
            
            
            if notes.strip() == "":
                notes = None
        except KeyboardInterrupt:
            return None
        
        
        try:
            from utils.date_utils import format_datetime

            
            recap_table = Table(title="Récapitulatif de l'événement",             
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            expand=False,
            border_style="blue", )

            
            recap_table.add_column("Date de début", style="bright_white")
            recap_table.add_column("Date de fin", style="bright_white")
            recap_table.add_column("Lieu", style="bright_white")
            recap_table.add_column("Participants", style="bright_white")
            if notes:
                recap_table.add_column("Notes", style="bright_white")

            
            if notes:
                recap_table.add_row(
                    format_datetime(start_date),
                    format_datetime(end_date),
                    location,
                    str(attendees),
                    notes
                )
            else:
                recap_table.add_row(
                    format_datetime(start_date),
                    format_datetime(end_date),
                    location,
                    str(attendees)
                )

            self.console.print(recap_table)
            
            confirm = inquirer.select(
                message="\nVoulez-vous créer cet événement ? \n",
                choices=[
                    Choice(value=True, name="Oui"),
                    Choice(value=False, name="Non")
                ],
                default=True,
                style=self.custom_style,
                qmark="",
                amark="",
                show_cursor=False,
                long_instruction="Sélectionnez Oui pour créer l'événement ou Non pour annuler",
            ).execute()
            
            if not confirm:
                return None
        except KeyboardInterrupt:
            return None
        
        return {
            "event_start_date": start_date,
            "event_end_date": end_date,
            "location": location,
            "attendees": attendees,
            "notes": notes
        }
    
    def select_event_to_modify(self, events, db_session=None):
        """
        Affiche la liste des événements pour en sélectionner un à modifier.
        
        Args:
            events (list): Liste des événements disponibles
            db_session (Session, optional): Session de base de données pour les requêtes additionnelles
            
        Returns:
            int: ID de l'événement sélectionné ou None si annulé
        """
        self.clear_screen()
        
        
        title_table = self.rich_components.create_title_table("MODIFICATION D'UN ÉVÉNEMENT")
        self.console.print(title_table)
        self.console.print("\n")
        
        if not events:
            self.console.print("[yellow]Aucun événement disponible.[/yellow]")
            return None
        
        
        events_table = self.rich_components.create_events_table(events, db_session)
        self.console.print(events_table)
        self.console.print("\n")
        
        
        choices = []
        for event in events:
            
            client_name = "Client inconnu"
            
            if db_session and event.contract_id:
                from models.client import Client
                from models.contract import Contract
                
                contract = db_session.get(Contract, event.contract_id)
                if contract and contract.client_id:
                    client = db_session.get(Client, contract.client_id)
                    if client:
                        client_name = client.company_name or client.full_name
            
            
            start_date = event.event_start_date.strftime("%d/%m/%Y %H:%M") if event.event_start_date else "N/A"
            
            choices.append(
                {"name": f"ID: {event.id} | Client: {client_name} | Date: {start_date} | Lieu: {event.location}", "value": event.id}
            )
        
        
        choices.append({"name": "Annuler", "value": None})
        
        
        event_id = inquirer.select(
            message="Sélectionnez un événement à modifier:",
            choices=choices,
            style=self.custom_style,
            qmark="",
            amark=""
        ).execute()
        
        return event_id
    
    def display_event_details(self, event, db_session=None):
        """
        Affiche les détails d'un événement en utilisant la même table que la liste des événements.
        
        Args:
            event (Event): L'événement à afficher
            db_session (Session, optional): Session de base de données pour les requêtes additionnelles
        """
        self.clear_screen()
        
        
        title_table = self.rich_components.create_title_table("DÉTAILS DE L'ÉVÉNEMENT")
        self.console.print(title_table)
        self.console.print("\n")
        
        
        events = [event]
        
        
        events_table = self.rich_components.create_events_table(events, db_session)
        self.console.print(events_table)
    
    def select_field_to_modify(self):
        """
        Affiche les options pour modifier un événement.
        
        Returns:
            str: Le champ à modifier ou None si annulé
        """
        choices = [
            Choice(value="event_start_date", name="Date et heure de début"),
            Choice(value="event_end_date", name="Date et heure de fin"),
            Choice(value="location", name="Lieu"),
            Choice(value="attendees", name="Nombre de participants"),
            Choice(value="notes", name="Notes"),
            Separator(),
            Choice(value=None, name="Terminer les modifications")
        ]
        
        field = inquirer.select(
            message="Que souhaitez-vous modifier?",
            choices=choices,
            style=self.custom_style,
            qmark="",
            amark=""
        ).execute()
        
        return field
    
    def _validate_date_format(self, date_str):
        """
        Valide le format d'une date.
        
        Args:
            date_str (str): Chaîne de date à valider
            
        Returns:
            bool: True si le format est valide, False sinon
        """
        try:
            datetime.strptime(date_str, "%d/%m/%Y %H:%M")
            return True
        except ValueError:
            return False
    
    def collect_new_value(self, field, current_value, event=None):
        """
        Collecte une nouvelle valeur pour un champ spécifique d'un événement.
        
        Args:
            field (str): Nom du champ à modifier
            current_value: Valeur actuelle du champ
            event (Event, optional): L'événement complet si nécessaire pour la validation
            
        Returns:
            La nouvelle valeur du champ ou None si annulé
        """
        if field == "event_start_date":
            
            current_date_str = current_value.strftime("%d/%m/%Y %H:%M") if current_value else ""
            
            
            new_date_str = inquirer.text(
                message=f"Nouvelle date et heure de début (actuelle: {current_date_str}):",
                default=current_date_str,
                validate=lambda value: self._validate_date_format(value) or "Format de date invalide. Utilisez JJ/MM/AAAA HH:MM",
                style=self.custom_style,
                qmark="",
                amark=""
            ).execute()
            
            
            new_date = datetime.strptime(new_date_str, "%d/%m/%Y %H:%M")
            
            
            if event and event.event_end_date and new_date >= event.event_end_date:
                self.show_error_message("La date de début doit être antérieure à la date de fin.")
                return None
            
            return new_date
            
        elif field == "event_end_date":
            
            current_date_str = current_value.strftime("%d/%m/%Y %H:%M") if current_value else ""
            
            
            new_date_str = inquirer.text(
                message=f"Nouvelle date et heure de fin (actuelle: {current_date_str}):",
                default=current_date_str,
                validate=lambda value: self._validate_date_format(value) or "Format de date invalide. Utilisez JJ/MM/AAAA HH:MM",
                style=self.custom_style,
                qmark="",
                amark=""
            ).execute()
            
            
            new_date = datetime.strptime(new_date_str, "%d/%m/%Y %H:%M")
            
            
            if event and event.event_start_date and new_date <= event.event_start_date:
                self.show_error_message("La date de fin doit être postérieure à la date de début.")
                return None
            
            return new_date
            
        elif field == "location":
            return inquirer.text(
                message=f"Nouveau lieu (actuel: {current_value}):",
                default=current_value or "",
                validate=lambda value: len(value.strip()) > 0 or "Le lieu ne peut pas être vide",
                style=self.custom_style,
                qmark="",
                amark=""
            ).execute()
            
        elif field == "attendees":
            return inquirer.number(
                message=f"Nouveau nombre de participants (actuel: {current_value}):",
                default=int(current_value) if isinstance(current_value, (int, str)) else 1,
                min_allowed=1,
                style=self.custom_style,
                qmark="",
                amark=""
            ).execute()
            
        elif field == "notes":
            new_notes = inquirer.text(
                message=f"Nouvelles notes (actuelles: {current_value}):",
                default=current_value or "",
                style=self.custom_style,
                qmark="",
                amark=""
            ).execute()
            
            
            if new_notes.strip() == "":
                return None
                
            return new_notes
        
        return None
    
    def select_event_for_assignment(self, events, db_session=None):
        """
        Affiche une liste d'événements et permet à l'utilisateur d'en sélectionner un pour l'assigner
        à un membre de l'équipe support.
        
        Args:
            events (list): Liste des événements
            db_session (Session, optional): Session de base de données pour les requêtes additionnelles
            
        Returns:
            int: L'ID de l'événement sélectionné ou None si l'utilisateur annule
        """
        self.clear_screen()
        
        
        title_table = self.rich_components.create_title_table("ASSIGNATION D'UN ÉVÉNEMENT")
        self.console.print(title_table)
        
        
        if not events:
            self.print_utils.print_error("Aucun événement disponible pour assignation.")
            select_with_back()
            return None
        
        
        events_table = self.rich_components.create_events_table(events, db_session)
        self.console.print(events_table)
        self.console.print("\n")
        
        
        choices = []
        for event in events:
            
            client_name = "Client inconnu"
            
            if db_session and event.contract_id:
                from models.client import Client
                from models.contract import Contract
                
                contract = db_session.get(Contract, event.contract_id)
                if contract and contract.client_id:
                    client = db_session.get(Client, contract.client_id)
                    if client:
                        client_name = client.company_name
            
            
            if event.support_contact_id:
                support_status = "🟢 Assigné"  
            else:
                support_status = "🔴 Non assigné"  
            
            
            choice_text = f"ID: {event.id} - Client: {client_name} - Support: {support_status}"
            choices.append(Choice(value=event.id, name=choice_text))
        
        
        
        choices.append(Choice(value=None, name="Annuler"))
        
        
        event_id = inquirer.fuzzy(
            message="Sélectionnez un événement à assigner:\n",
            choices=choices,
            style=self.custom_style,
            amark="",
            qmark="",
            long_instruction="Ici, veuillez sélectionner l'événement à assigner à un membre de l'équipe support",
            mandatory=False
        ).execute()
        
        return event_id
    
    def select_support_staff(self, support_staff, db_session=None):
        """
        Affiche une liste des membres de l'équipe support et permet à l'utilisateur d'en sélectionner un.
        
        Args:
            support_staff (list): Liste des membres de l'équipe support
            db_session (Session, optional): Session de base de données pour les requêtes additionnelles
            
        Returns:
            int: L'ID du membre de l'équipe support sélectionné ou None si l'utilisateur annule
        """
        self.clear_screen()
        
        
        title_table = self.rich_components.create_title_table("SÉLECTION D'UN MEMBRE DE L'ÉQUIPE SUPPORT")
        self.console.print(title_table)
        self.console.print("\n")
        
        if not support_staff:
            self.console.print("[yellow]Aucun membre de l'équipe support disponible.[/yellow]")
            return None
        
        
        users_table = self.rich_components.create_users_table(support_staff)
        self.console.print(users_table)
        self.console.print("\n")
        
        
        choices = []
        for staff in support_staff:
            choice_text = f"ID: {staff.id} - Nom: {staff.name} - Email: {staff.email}"
            choices.append({"name": choice_text, "value": staff.id})
        
        choices.append({"name": "Annuler", "value": None})
        
        
        support_id = inquirer.fuzzy(
            message="Sélectionnez un membre de l'équipe support:",
            choices=choices,
            style=self.custom_style,
            qmark="",
            amark="",
            long_instruction="Ici, veuillez sélectionner le membre de l'équipe support à assigner à l'événement",
            mandatory=False
        ).execute()
        
        return support_id
    
    def select_event_to_delete(self, events, db_session=None):
        """
        Affiche une liste d'événements et permet à l'utilisateur d'en sélectionner un pour suppression.
        
        Args:
            events (list): Liste des événements
            db_session (Session, optional): Session de base de données pour les requêtes additionnelles
            
        Returns:
            int: L'ID de l'événement sélectionné ou None si l'utilisateur annule
        """
        self.clear_screen()
        
        title_table = self.rich_components.create_title_table("SUPPRESSION D'UN ÉVÉNEMENT", style="bold red")
        self.console.print(title_table)
        self.console.print("\n")
        
        if not events:
            self.console.print("[yellow]Aucun événement disponible.[/yellow]")
            return None
        
        events_table = self.rich_components.create_events_table(events, db_session)
        self.console.print(events_table)
        
        choices = []
        for event in events:
            client_name = "Client inconnu"
            
            if db_session and event.contract_id:
                from models.client import Client
                from models.contract import Contract
                
                contract = db_session.get(Contract, event.contract_id)
                if contract and contract.client_id:
                    client = db_session.get(Client, contract.client_id)
                    if client:
                        client_name = client.company_name or client.full_name
            
            start_date = event.event_start_date.strftime("%d/%m/%Y %H:%M") if event.event_start_date else "N/A"
            
            choice_text = f"ID: {event.id} - Client: {client_name} - Date: {start_date} - Lieu: {event.location}"
            choices.append(Choice(value=event.id, name=choice_text))
        
        choices.append(Separator())
        choices.append(Choice(value=None, name="Annuler"))
        
        event_id = inquirer.select(
            message="Sélectionnez un événement à supprimer:",
            choices=choices,
            style=self.custom_style,
            show_cursor=False,
            qmark=""
        ).execute()
        
        return event_id
    
    def confirm_deletion(self, event, db_session=None):
        """
        Demande confirmation avant de supprimer un événement.
        
        Args:
            event (Event): L'événement à supprimer
            db_session (Session, optional): Session de base de données pour les requêtes additionnelles
            
        Returns:
            bool: True si l'utilisateur confirme la suppression, False sinon
        """
        self.clear_screen()
        
        self.display_event_details(event, db_session)
        

        self.console.print("\n[bold red]ATTENTION: Cette action est irréversible![/bold red]")
        confirm = inquirer.confirm(
            message="Êtes-vous sûr de vouloir supprimer cet événement?",
            default=False,
            style=self.custom_style,
            qmark="",
            amark=""
        ).execute()
        
        return confirm
    
    def show_success_message(self, message):
        """
        Affiche un message de succès.
        
        Args:
            message (str): Le message à afficher
        """
        self.console.print(f"[bold green]{message}[/bold green]")
    
    def show_error_message(self, message):
        """
        Affiche un message d'erreur.
        
        Args:
            message (str): Le message à afficher
        """
        self.console.print(f"[bold red]{message}[/bold red]")
    
    def show_warning_message(self, message):
        """
        Affiche un message d'avertissement.
        
        Args:
            message (str): Le message à afficher
        """
        self.console.print(f"[bold yellow]{message}[/bold yellow]")
    
    def show_info_message(self, message):
        """
        Affiche un message d'information.
        
        Args:
            message (str): Le message à afficher
        """
        self.console.print(f"[bold blue]{message}[/bold blue]")