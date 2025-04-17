import os

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from InquirerPy.validator import EmptyInputValidator
from rich.console import Console
from rich.panel import Panel
from rich.table import Table, box
from rich.text import Text

from models.user import DepartmentType
from utils.inquire_utils import select_with_back
from utils.print_utils import PrintUtils
from views.components.rich_components import RichComponents


class ContractView:
    """
    Vue responsable de l'affichage et de la collecte des informations
    liées aux contrats.
    """
    
    def __init__(self, custom_style=None):
        """
        Initialise la vue contrat.
        
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
    
    def display_contracts_list(self, contracts, db_session=None):
        """
        Affiche la liste des contrats.
        
        Args:
            contracts (list): Liste d'objets Contract à afficher
            db_session: Session de base de données pour récupérer des informations complémentaires
        """
        self.clear_screen()
        
        
        title_table = self.rich_components.create_title_table("LISTE DES CONTRATS")
        self.console.print(title_table)
        
        if not contracts:
            self.print_utils.print_error("Vous n'avez aucun contrat enregistré")
        else:
            
            contracts_table = self.rich_components.create_contracts_table(contracts, db_session)
            self.console.print(contracts_table)
            self.console.print("\n")

        
    
    def select_client_for_contract(self, clients, db_session=None, is_management=False):
        """
        Permet de sélectionner un client pour la création d'un contrat.
        
        Args:
            clients: Liste des clients disponibles
            db_session: Session de base de données pour les requêtes supplémentaires
            is_management: Indique si l'utilisateur est de l'équipe de gestion
            
        Returns:
            int: ID du client sélectionné ou None si annulé
        """
        self.clear_screen()
        
        
        title_table = self.rich_components.create_title_table("SÉLECTION D'UN CLIENT POUR UN CONTRAT")
        self.console.print(title_table)
        
        if not clients:
            self.print_utils.print_error("Aucun client disponible.")
            select_with_back()
            return None
        
        
        clients_table = self.rich_components.create_clients_table(clients, db_session)
        self.console.print(clients_table)
        self.console.print("\n")
        
        
        client_choices = []
        for client in clients:
            client_choices.append(
                Choice(
                    value=client.id,
                    name=f"ID: {client.id} | {client.full_name} | {client.company_name}"
                )
            )
        
        
        client_choices.append(Choice(value=None, name="Annuler"))
        

        client_id = inquirer.fuzzy(
            message="Recherchez et sélectionnez un client pour ce contrat :\n",
            choices=client_choices,
            style=self.custom_style,
            qmark="",
            amark="",
            long_instruction="Sélectionnez un client pour créer un contrat"
        ).execute()
        
        return client_id
    
    def display_client_contracts(self, client, contracts, db_session=None):
        """
        Affiche les informations du client et ses contrats existants.
        
        Args:
            client: L'objet client
            contracts: Liste des contrats du client
            db_session: Session de base de données
        """
        self.clear_screen()
        
        
        title_table = self.rich_components.create_title_table("Informations du client")
        self.console.print(title_table)
        
        
        client_info_table = self.rich_components.create_client_info_table(client, db_session)
        self.console.print(client_info_table)
        self.console.print("\n")
        

        title_table = self.rich_components.create_title_table("Contrats existants pour ce client")
        self.console.print(title_table)
        
        contracts_table = self.rich_components.create_client_contracts_table(contracts)
        self.console.print(contracts_table)
        self.console.print("\n")
        
    
    def collect_contract_data(self):
        """
        Collecte les données pour un nouveau contrat.
        
        Returns:
            dict: Dictionnaire contenant les données du contrat ou None si annulé
        """
        self.console.print("[bold cyan]Saisissez les informations du contrat:[/bold cyan]\n")
        
        try:
            
            total_amount = inquirer.number(
                message="Montant total du contrat (€) :",
                min_allowed=float(0.00),
                float_allowed=True,
                invalid_message="Le montant doit être supérieur à 0",
                style=self.custom_style,
                qmark="",
                amark="",
                long_instruction="Saisissez le montant total du contrat (€)\nAppuyer sur Ctrl+C pour annuler",
            ).execute()
            
            if total_amount is None:
                return None
            
            
            remaining_amount = inquirer.number(
                message="Montant restant à payer (€) :",
                min_allowed=float(0.00),
                max_allowed=float(total_amount),
                float_allowed=True,
                default=float(total_amount),
                invalid_message=f"Le montant doit être compris entre 0 et {total_amount}",
                style=self.custom_style,
                qmark="",
                amark="",
                long_instruction="Saisissez le montant restant à payer (€)\nAppuyer sur Ctrl+C pour annuler",
            ).execute()
            
            if remaining_amount is None:
                return None
            
            
            is_signed = inquirer.select(
                message="Le contrat est-il signé ?",
                choices=[
                    Choice(value=True, name="Oui"),
                    Choice(value=False, name="Non")
                ],
                default=False,
                style=self.custom_style,
                qmark="",
                amark="",
                show_cursor=False,
                long_instruction="Choisissez si le contrat est signé ou non\nAppuyer sur Ctrl+C pour annuler",
            ).execute()
            
            if is_signed is None:
                return None
            
            
            return {
                "total_amount": total_amount,
                "remaining_amount": remaining_amount,
                "is_signed": is_signed
            }
        
        except KeyboardInterrupt:
            self.console.print("\n[bold red]Saisie annulée.[/bold red]")
            return None
        except Exception as e:
            self.console.print(f"\n[bold red]Erreur lors de la saisie: {str(e)}[/bold red]")
            return None
    
    def select_contract_to_modify(self, contracts, db_session=None):
        """
        Affiche les contrats pour sélection et modification.
        
        Args:
            contracts: Liste des contrats disponibles
            db_session: Session de base de données pour les requêtes supplémentaires
            
        Returns:
            int: ID du contrat sélectionné ou None si annulé
        """
        self.clear_screen()
        
        
        title_table = self.rich_components.create_title_table("MODIFICATION D'UN CONTRAT")
        self.console.print(title_table)
        
        if not contracts:
            self.print_utils.print_error("Vous n'avez aucun contrat à modifier.")
            select_with_back()
            return None
        
        
        contracts_table = self.rich_components.create_contracts_table(contracts, db_session)
        self.console.print(contracts_table)
        self.console.print("\n")
        
        
        contract_choices = []
        
        for contract in contracts:
            
            client_name = "Client inconnu"
            if db_session and contract.client_id:
                from models.client import Client
                client = db_session.get(Client, contract.client_id)
                if client:
                    client_name = client.full_name
            
            contract_choices.append(
                Choice(
                    value=contract.id,
                    name=f"ID: {contract.id} | Client: {client_name} | Montant: {contract.total_amount:.2f} €"
                )
            )
        
        longest_choice_length = max(len(choice.name) for choice in contract_choices)
        contract_choices.append(Separator(line="─" * longest_choice_length))
        
        
        
        contract_choices.append(Choice(value=None, name="Retour au menu précédent"))
        
        
        contract_id = inquirer.select(
            message="Sélectionnez un contrat à modifier :\n", 
            choices=contract_choices,
            style=self.custom_style,
            qmark="",
            amark="",
            show_cursor=False,
            long_instruction="\nSélectionnez un contrat pour modifier ses informations\n"
        ).execute()
        
        return contract_id
    
    def display_contract_details(self, contract, client, db_session=None):
        """
        Affiche les détails d'un contrat.
        
        Args:
            contract: L'objet contrat
            client: L'objet client associé
            db_session: Session de base de données
        """
        
        contract_info_table = self.rich_components.create_contract_info_table(contract, db_session)
        self.console.print(contract_info_table)
        self.console.print("\n")
    
    def select_field_to_modify(self):
        """
        Affiche les options pour modifier un contrat.
        
        Returns:
            str: Nom du champ à modifier ou None si annulé
        """
        field_choices = [
            Choice(value="total_amount", name="Modifier le montant total"),
            Choice(value="remaining_amount", name="Modifier le montant restant"),
            Choice(value="is_signed", name="Modifier le statut (signé/non signé)"),
            Separator(),
            Choice(value=None, name="Retour au menu précédent")
        ]
        
        field = inquirer.select(
            message="Quel champ souhaitez-vous modifier ?\n",
            choices=field_choices,
            style=self.custom_style,
            qmark="",
            amark="",
            show_cursor=False,
            

        ).execute()
        
        return field
    
    def collect_new_value(self, field, current_value, contract=None):
        """
        Collecte une nouvelle valeur pour un champ spécifié d'un contrat.
        
        Args:
            field: Nom du champ à modifier
            current_value: Valeur actuelle du champ
            contract: Contrat en cours de modification (pour les validations)
            
        Returns:
            mixed: Nouvelle valeur pour le champ ou None si annulé
        """
        try:
            if field == "total_amount":
                
                current_total = float(current_value)
                current_remaining = float(contract.remaining_amount) if contract else 0
                
                new_value = inquirer.number(
                    message=f"Nouveau montant total (actuel: {current_total:.2f} €):",
                    min_allowed=current_remaining,
                    float_allowed=True,
                    default=current_total,
                    invalid_message=f"Le montant doit être supérieur ou égal au montant restant ({current_remaining:.2f} €)",
                    style=self.custom_style
                ).execute()
                
                return new_value
                
            elif field == "remaining_amount":
                
                current_remaining = float(current_value)
                current_total = float(contract.total_amount) if contract else float("inf")
                
                new_value = inquirer.number(
                    message=f"Nouveau montant restant (actuel: {current_remaining:.2f} €):",
                    min_allowed=float(0),
                    max_allowed=current_total,
                    float_allowed=True,
                    default=current_remaining,
                    invalid_message=f"Le montant doit être compris entre 0 et {current_total:.2f} €",
                    style=self.custom_style
                ).execute()
                
                return new_value
                
            elif field == "is_signed":
                
                current_status = "signé" if current_value else "non signé"
                
                new_value = inquirer.select(
                    message=f"Nouveau statut (actuel: {current_status}):",
                    choices=[
                        Choice(value=True, name="Signé"),
                        Choice(value=False, name="Non signé")
                    ],
                    default=current_value,
                    style=self.custom_style,
                    qmark="",
                    amark="",
                    show_cursor=False,
                ).execute()
                
                return new_value
                
            return None
            
        except Exception as e:
            self.console.print(f"\n[bold red]Erreur lors de la saisie: {str(e)}[/bold red]")
            return None
    
    def select_contract_to_delete(self, contracts, db_session=None):
        """
        Affiche les contrats pour sélection et suppression.
        
        Args:
            contracts: Liste des contrats disponibles
            db_session: Session de base de données pour les requêtes supplémentaires
            
        Returns:
            int: ID du contrat sélectionné ou None si annulé
        """
        self.clear_screen()
        
        
        title_table = self.rich_components.create_title_table("SUPPRESSION D'UN CONTRAT", style="bold red")
        self.console.print(title_table)
        self.console.print("\n")
        
        if not contracts:
            self.console.print("[yellow]Aucun contrat disponible.[/yellow]")
            input("\nAppuyez sur Entrée pour continuer...")
            return None
        
        
        contracts_table = self.rich_components.create_contracts_table(contracts, db_session)
        self.console.print(contracts_table)
        self.console.print("\n")
        
        
        contract_choices = []
        
        for contract in contracts:
            
            client_name = "Client inconnu"
            if db_session and contract.client_id:
                from models.client import Client
                client = db_session.get(Client, contract.client_id)
                if client:
                    client_name = client.full_name
            
            contract_choices.append(
                Choice(
                    value=contract.id,
                    name=f"ID: {contract.id} | Client: {client_name} | Montant: {contract.total_amount:.2f} €"
                )
            )
        
        
        contract_choices.append(Separator())
        contract_choices.append(Choice(value=None, name="Annuler"))
        
        
        contract_id = inquirer.select(
            message="Sélectionnez un contrat à supprimer:",
            choices=contract_choices,
            style=self.custom_style
        ).execute()
        
        return contract_id
    
    def confirm_deletion(self, contract, client_name):
        """
        Demande confirmation avant de supprimer un contrat.
        
        Args:
            contract: Le contrat à supprimer
            client_name: Nom du client associé au contrat
            
        Returns:
            bool: True si la suppression est confirmée, False sinon
        """
        self.console.print("\n[bold red]ATTENTION: Cette action est irréversible![/bold red]\n")
        
        
        self.console.print(f"[bold]Contrat #{contract.id}[/bold]")
        self.console.print(f"Client: {client_name}")
        self.console.print(f"Montant total: {contract.total_amount:.2f} €")
        self.console.print(f"Montant restant: {contract.remaining_amount:.2f} €")
        self.console.print(f"Statut: {'signé' if contract.is_signed else 'non signé'}")
        self.console.print("\n")
        
        
        confirmation = inquirer.confirm(
            message="Êtes-vous sûr de vouloir supprimer ce contrat?",
            default=False,
            style=self.custom_style
        ).execute()
        
        return confirmation
    