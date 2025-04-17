from rich.console import Console
from rich.table import Table, box

from utils.date_utils import format_datetime


class RichComponents:
    """
    Classe utilitaire fournissant des composants d'interface utilisateur réutilisables
    basés sur la bibliothèque Rich.
    """
    
    @staticmethod
    def create_title_table(title_text, style="bold magenta"):
        """
        Crée un tableau pour afficher un titre avec un style attrayant.
        
        Args:
            title_text (str): Le texte du titre à afficher
            style (str): Le style Rich à appliquer au titre
        
        Returns:
            Table: Un tableau Rich contenant le titre formaté
        """
        title_table = Table(
            show_header=False,
            show_footer=False,
            box=box.ROUNDED,
            style=style,
            padding=(0, 1),
            expand=False,
            border_style="magenta"
        )
        
        title_table.add_column()
        title_table.add_row(f"[{style}]{title_text}[/{style}]")
        
        return title_table
    
    @staticmethod
    def create_users_table(users):
        """
        Crée un tableau formaté pour afficher la liste des utilisateurs.
        
        Args:
            users (list): Liste d'objets User à afficher
        
        Returns:
            Table: Un tableau Rich formaté avec les données des utilisateurs
        """
        users_table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            expand=False,
            border_style="blue"
        )
        
        # Définition des colonnes
        users_table.add_column("ID", style="dim", width=5)
        users_table.add_column("Nom", style="bright_white", width=25)
        users_table.add_column("Email", style="bright_white", width=30)
        users_table.add_column("Département", style="bright_white", width=15)
        users_table.add_column("N° Employé", style="bright_white", width=15)
        users_table.add_column("Date de création", style="bright_white", width=20),
        # Ajout des utilisateurs
        for user in users:
            users_table.add_row(
                str(user.id),
                user.name,
                user.email,
                user.department.value,
                user.employee_number,
                format_datetime(user.created_at)
            )
        
        return users_table
    
    @staticmethod
    def create_clients_table(clients, db_session=None):
        """
        Crée un tableau formaté pour afficher la liste des clients.
        
        Args:
            clients (list): Liste d'objets Client à afficher
            db_session: Session de base de données pour récupérer des informations complémentaires
            
        Returns:
            Table: Un tableau Rich formaté avec les données des clients
        """
        from models.user import User
        
        clients_table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            expand=False,
            border_style="blue"
        )
        
        # Définition des colonnes
        clients_table.add_column("ID", style="dim", width=5)
        clients_table.add_column("Nom", style="bright_white", width=25)
        clients_table.add_column("Email", style="bright_white", width=30)
        clients_table.add_column("Téléphone", style="bright_white", width=15)
        clients_table.add_column("Entreprise", style="bright_white", width=25)
        clients_table.add_column("Commercial", style="bright_white", width=20)
        
        # Ajout des clients
        for client in clients:
            # Récupération du commercial
            commercial_name = "Non assigné"
            commercial_id = None
            
            if client.sales_contact_id and db_session:
                commercial = db_session.get(User, client.sales_contact_id)
                if commercial:
                    commercial_name = commercial.name
                    commercial_id = commercial.id
            
            clients_table.add_row(
                str(client.id),
                client.full_name,
                client.email,
                client.phone,
                client.company_name,
                f"({commercial_id}) {commercial_name}" if commercial_id else commercial_name
            )
        
        return clients_table
    
    @staticmethod
    def create_client_info_table(client, db_session=None):
        """
        Crée un tableau pour afficher les détails d'un client spécifique.
        
        Args:
            client (Client): L'objet client à afficher
            db_session: Session de base de données pour récupérer des informations complémentaires
            
        Returns:
            Table: Un tableau Rich formaté avec les détails du client
        """
        from models.user import User
        
        client_info_table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            expand=False,
            border_style="blue"
        )
        
        # Configuration des colonnes
        client_info_table.add_column("ID", style="dim", width=5)
        client_info_table.add_column("Nom", style="bright_white", width=25)
        client_info_table.add_column("Email", style="bright_white", width=30)
        client_info_table.add_column("Téléphone", style="bright_white", width=15)
        client_info_table.add_column("Entreprise", style="bright_white", width=25)
        
        # Ajout de la ligne d'information
        client_info_table.add_row(
            str(client.id),
            client.full_name,
            client.email,
            client.phone,
            client.company_name
        )
        
        return client_info_table
    
    @staticmethod
    def create_contracts_table(contracts, db_session=None):
        """
        Crée un tableau formaté pour afficher la liste des contrats.
        
        Args:
            contracts (list): Liste d'objets Contract à afficher
            db_session: Session de base de données pour récupérer des informations complémentaires
            
        Returns:
            Table: Un tableau Rich formaté avec les données des contrats
        """
        from models.client import Client
        from models.user import User
        
        contracts_table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            expand=False,
            border_style="blue"
        )
        
        # Définition des colonnes
        contracts_table.add_column("ID", style="dim", width=5)
        contracts_table.add_column("Client", style="bright_white", width=25)
        contracts_table.add_column("Commercial", style="bright_white", width=20)
        contracts_table.add_column("Montant total", style="bright_white", width=15)
        contracts_table.add_column("Montant restant", style="bright_white", width=15)
        contracts_table.add_column("Signé", style="bright_white", width=10)
        contracts_table.add_column("Date création", style="bright_white", width=20)
        
        # Ajout des contrats
        for contract in contracts:
            # Récupérer le client
            client_name = "N/A"
            if db_session and contract.client_id:
                client = db_session.get(Client, contract.client_id)
                if client:
                    client_name = client.full_name
            
            # Récupérer le commercial
            commercial_name = "N/A"
            if db_session and contract.sales_contact_id:
                commercial = db_session.get(User, contract.sales_contact_id)
                if commercial:
                    commercial_name = commercial.name
            
            if contract.remaining_amount > 0:
                if contract.remaining_amount > (contract.total_amount * 0.5):
                    remaining_amount_display = f"[red]{contract.remaining_amount:.2f} €[/red]"
                else:
                    remaining_amount_display = f"[yellow]{contract.remaining_amount:.2f} €[/yellow]"
            else:
                remaining_amount_display = f"[green]{contract.remaining_amount:.2f} €[/green]"
            
            # Format pour le statut (signé ou non)
            signed_status = "[green]Oui[/green]" if contract.is_signed else "[red]Non[/red]"
            
            # Formater la date de création
            
            contracts_table.add_row(
                str(contract.id),
                client_name,
                commercial_name,
                f"{contract.total_amount:.2f} €",
                remaining_amount_display,
                signed_status,
                format_datetime(contract.creation_date)
            )
        
        return contracts_table
    
    @staticmethod
    def create_contract_info_table(contract, db_session=None):
        """
        Crée un tableau pour afficher les détails d'un contrat spécifique.
        
        Args:
            contract (Contract): L'objet contrat à afficher
            db_session: Session de base de données pour récupérer des informations complémentaires
            
        Returns:
            Table: Un tableau Rich formaté avec les détails du contrat
        """
        from models.client import Client
        from models.user import User
        
        contract_info_table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            expand=False,
            border_style="blue"
        )
        
        # Configuration des colonnes
        contract_info_table.add_column("ID", style="dim", width=5)
        contract_info_table.add_column("Client", style="bright_white", width=25)
        contract_info_table.add_column("Commercial", style="bright_white", width=20)
        contract_info_table.add_column("Montant total", style="bright_white", width=15)
        contract_info_table.add_column("Montant restant", style="bright_white", width=15)
        contract_info_table.add_column("Signé", style="bright_white", width=10)
        contract_info_table.add_column("Date création", style="bright_white", width=20)
        
        # Récupérer le client
        client_name = "N/A"
        if db_session and contract.client_id:
            client = db_session.get(Client, contract.client_id)
            if client:
                client_name = client.full_name
        
        # Récupérer le commercial
        commercial_name = "N/A"
        if db_session and contract.sales_contact_id:
            commercial = db_session.get(User, contract.sales_contact_id)
            if commercial:
                commercial_name = commercial.name
        
        # Format pour le montant restant avec couleur
        if contract.remaining_amount > 0:
            # Rouge si plus de 50% du montant total reste à payer
            if contract.remaining_amount > (contract.total_amount * 0.5):
                remaining_amount_display = f"[bold red]{contract.remaining_amount:.2f} €[/bold red]"
            # Orange si entre 1% et 50% du montant total reste à payer
            else:
                remaining_amount_display = f"[bold orange]{contract.remaining_amount:.2f} €[/bold orange]"
        else:
            # Vert si tout est payé
            remaining_amount_display = f"[bold green]{contract.remaining_amount:.2f} €[/bold green]"
        
        # Format pour le statut (signé ou non)
        signed_status = "[green]Oui[/green]" if contract.is_signed else "[red]Non[/red]"
        
        # Formater la date de création
        
        # Ajout de la ligne d'information
        contract_info_table.add_row(
            str(contract.id),
            client_name,
            commercial_name,
            f"{contract.total_amount:.2f} €",
            remaining_amount_display,
            signed_status,
            format_datetime(contract.creation_date)
        )
        
        return contract_info_table
    
    @staticmethod
    def create_client_contracts_table(contracts, db_session=None):
        """
        Crée un tableau pour afficher les contrats d'un client spécifique.
        
        Args:
            contracts (list): Liste des contrats du client
            db_session: Session de base de données pour récupérer des informations complémentaires
            
        Returns:
            Table: Un tableau Rich formaté avec les contrats du client
        """
        contracts_table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            expand=False,
            border_style="blue"
        )
        
        # Configuration des colonnes
        contracts_table.add_column("ID", style="dim", width=5)
        contracts_table.add_column("Montant total", style="bright_white", width=15)
        contracts_table.add_column("Montant restant", style="bright_white", width=15)
        contracts_table.add_column("Signé", style="bright_white", width=10)
        contracts_table.add_column("Date création", style="bright_white", width=20)
        
        # Ajout des contrats
        for contract in contracts:
            # Format pour le statut (signé ou non)
            signed_status = "[green]Oui[/green]" if contract.is_signed else "[red]Non[/red]"
            
            
            contracts_table.add_row(
                str(contract.id),
                f"{contract.total_amount:.2f} €",
                f"{contract.remaining_amount:.2f} €",
                signed_status,
                format_datetime(contract.creation_date)
            )
        
        return contracts_table
    
    @staticmethod
    def create_events_table(events, db_session=None):
        """
        Crée un tableau formaté pour afficher la liste des événements.
        
        Args:
            events (list): Liste d'objets Event à afficher
            db_session: Session de base de données pour récupérer des informations complémentaires
            
        Returns:
            Table: Un tableau Rich formaté avec les données des événements
        """
        from models.client import Client
        from models.contract import Contract
        from models.user import User
        
        events_table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            expand=False,
            border_style="blue"
        )
        
        # Définition des colonnes
        events_table.add_column("ID", style="dim", width=5)
        events_table.add_column("Client", style="bright_white", width=20)
        events_table.add_column("Contrat", style="bright_white", width=10)
        events_table.add_column("Support", style="bright_white", width=20)
        events_table.add_column("Début", style="bright_white", width=16)
        events_table.add_column("Fin", style="bright_white", width=16)
        events_table.add_column("Lieu", style="bright_white", width=20)
        events_table.add_column("Participants", style="bright_white", width=12)
        
        # Ajout des événements
        for event in events:
            # Récupérer le contrat et le client
            client_name = "N/A"
            contract_id = "N/A"
            
            if db_session and event.contract_id:
                contract = db_session.get(Contract, event.contract_id)
                if contract:
                    contract_id = str(contract.id)
                    if contract.client_id:
                        client = db_session.get(Client, contract.client_id)
                        if client:
                            client_name = client.full_name
            
            # Récupérer le support assigné et l'afficher en rouge si non assigné, en vert sinon
            if db_session and event.support_contact_id:
                support = db_session.get(User, event.support_contact_id)
                if support:
                    support_name = f"[green]{support.name}[/green]"
                else:
                    support_name = "[red]Support introuvable[/red]"
            else:
                support_name = "[red]Non assigné[/red]"
            
            
            events_table.add_row(
                str(event.id),
                client_name,
                contract_id,
                support_name,
                format_datetime(event.event_start_date),
                format_datetime(event.event_end_date),
                event.location or "N/A",
                str(event.attendees) if event.attendees is not None else "N/A"
            )
        
        return events_table
    
    @staticmethod
    def create_event_info_table(event, db_session=None):
        """
        Crée un tableau pour afficher les détails d'un événement spécifique.
        
        Args:
            event (Event): L'objet événement à afficher
            db_session: Session de base de données pour récupérer des informations complémentaires
            
        Returns:
            Table: Un tableau Rich formaté avec les détails de l'événement
        """
        from models.client import Client
        from models.contract import Contract
        from models.user import User
        
        event_info_table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            expand=False,
            border_style="blue"
        )
        
        # Configuration des colonnes
        event_info_table.add_column("Champ", style="bright_white", width=15)
        event_info_table.add_column("Valeur", style="bright_white", width=40)
        
        # Récupérer les informations associées
        client_name = "N/A"
        contract_id = "N/A"
        commercial_name = "N/A"
        
        if db_session and event.contract_id:
            contract = db_session.get(Contract, event.contract_id)
            if contract:
                contract_id = str(contract.id)
                if contract.client_id:
                    client = db_session.get(Client, contract.client_id)
                    if client:
                        client_name = client.full_name
                if contract.sales_contact_id:
                    commercial = db_session.get(User, contract.sales_contact_id)
                    if commercial:
                        commercial_name = commercial.name
            
        # Récupérer le support assigné et l'afficher en rouge si non assigné, en vert sinon
        if db_session and event.support_contact_id:
            support = db_session.get(User, event.support_contact_id)
            if support:
                support_name = f"[green]{support.name}[/green]"
            else:
                support_name = "[red]Support introuvable[/red]"
        else:
            support_name = "[red]Non assigné[/red]"
        

        # Ajout des lignes d'information
        event_info_table.add_row("ID", str(event.id))
        event_info_table.add_row("Client", client_name)
        event_info_table.add_row("Contrat", contract_id)
        event_info_table.add_row("Commercial", commercial_name)
        event_info_table.add_row("Support", support_name)
        event_info_table.add_row("Date de début", format_datetime(event.event_start_date))
        event_info_table.add_row("Date de fin", format_datetime(event.event_end_date))
        event_info_table.add_row("Lieu", event.location or "N/A")
        event_info_table.add_row("Participants", str(event.attendees) if event.attendees is not None else "N/A")
        event_info_table.add_row("Notes", event.notes or "Aucune note")
        
        return event_info_table
    
    @staticmethod
    def create_user_info_table(user):
        """
        Crée un tableau pour afficher les détails d'un utilisateur spécifique.
        
        Args:
            user (User): L'objet utilisateur à afficher
            
        Returns:
            Table: Un tableau Rich formaté avec les détails de l'utilisateur
        """
        user_table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.SIMPLE,
            expand=False,
            border_style="blue"
        )
        
        # Ajouter la colonne pour la date de création
        user_table.add_column("ID", style="dim", width=5)
        user_table.add_column("Nom", style="bright_white", width=25)
        user_table.add_column("Email", style="bright_white", width=30)
        user_table.add_column("N° Employé", style="bright_white", width=15)
        user_table.add_column("Département", style="bright_white", width=20)
        user_table.add_column("Date de création", style="bright_white", width=20)
        

        user_table.add_row(
            str(user.id),
            user.name,
            user.email,
            user.employee_number,
            user.department.value,
            format_datetime(user.created_at)
        )
        
        return user_table
    
    