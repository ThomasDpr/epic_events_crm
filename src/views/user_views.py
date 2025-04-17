import os

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from rich.console import Console

from validators import (
    EmailValidator,
    EmployeeNumberValidator,
    NameValidator,
    PasswordComplexityValidator,
)
from views.base_view import BaseView
from views.components.rich_components import RichComponents


class UserView(BaseView):
    """
    Vue responsable de l'affichage et de la collecte des informations
    liées aux utilisateurs.
    """
    
    def __init__(self, custom_style=None):
        """
        Initialise la vue utilisateur.
        
        Args:
            custom_style (dict, optional): Style personnalisé pour InquirerPy
        """
        self.console = Console()
        self.custom_style = custom_style or {}
        self.rich_components = RichComponents()
    
    
    def display_users_list(self, users):
        """
        Affiche la liste des utilisateurs.
        
        Args:
            users (list): Liste d'objets utilisateur à afficher
        """
        self.clear_screen()
        
        # Affichage du titre
        title_table = self.rich_components.create_title_table("LISTE DES UTILISATEURS")
        self.console.print(title_table)
        
        
        if not users:
            self.console.print("[bold red]Aucun utilisateur trouvé[/bold red]")
        else:
            # Création et affichage du tableau des utilisateurs
            users_table = self.rich_components.create_users_table(users)
            self.console.print(users_table)
        
    
    def show_user_creation_form(self, db, partial_data=None, is_first_admin=False):
        """
        Affiche le formulaire de création d'un utilisateur et collecte les données.
        Intercepte Ctrl+C pour proposer d'annuler ou de continuer.
        
        Args:
            db: Session de base de données pour les validateurs
            partial_data (dict, optional): Données partiellement saisies en cas de reprise
            is_first_admin (bool, optional): Indique s'il s'agit du premier administrateur
            
        Returns:
            dict: Dictionnaire contenant les données du nouvel utilisateur ou None si annulé
        """
        self.clear_screen()
        
        # Affichage du titre adapté
        title = "CRÉATION DU COMPTE ADMINISTRATEUR" if is_first_admin else "CRÉATION D'UN NOUVEL UTILISATEUR"

        
        self.header_title(title, "magenta")
        
        # Message spécifique pour le premier admin
        if is_first_admin:
            self.console.print("[yellow]Vous allez créer le premier compte utilisateur avec des droits d'administration.[/yellow]\n")
        
        # Initialiser les données de l'utilisateur
        user_data = partial_data or {}
        
        try:
            # Collecte du nom si non déjà fourni
            if "name" not in user_data:
                name = inquirer.text(
                    message="Nom complet :",
                    validate=NameValidator(),
                    style=self.custom_style,
                    qmark="",
                    amark="",
                    long_instruction="Le nom doit contenir au moins 2 caractères",
                ).execute()
                user_data["name"] = name
            else:
                self.console.print(f"[cyan]Nom complet:[/cyan] [green]{user_data['name']}[/green]")
            
            # Collecte de l'email si non déjà fourni
            if "email" not in user_data:
                email = inquirer.text(
                    message="Email :",
                    validate=EmailValidator(db),
                    style=self.custom_style,
                    qmark="",
                    amark="",
                    long_instruction="L'email doit être valide et unique",
                ).execute()
                user_data["email"] = email
            else:
                self.console.print(f"[cyan]Email:[/cyan] [green]{user_data['email']}[/green]")
            
            # Collecte du numéro d'employé si non déjà fourni
            if "employee_number" not in user_data:
                employee_number = inquirer.text(
                    message="Numéro d'employé (6 chiffres) :",
                    validate=EmployeeNumberValidator(db),
                    style=self.custom_style,
                    qmark="",
                    amark="",
                    long_instruction="Le numéro d'employé doit être composé exactement de 6 chiffres (ex: 123456)",
                ).execute()
                user_data["employee_number"] = employee_number
            else:
                self.console.print(f"[cyan]Numéro d'employé:[/cyan] [green]{user_data['employee_number']}[/green]")
            
            # Collecte du département si non déjà fourni et si ce n'est pas le premier admin
            if "department" not in user_data:
                if is_first_admin:
                    # Pour le premier admin, on force le département à Gestion
                    user_data["department"] = "gestion"
                    self.console.print(f"[cyan]Département:[/cyan] [green]Gestion[/green]")
                else:
                    # Choix normal pour les autres utilisateurs
                    department = inquirer.select(
                        message="Département :",
                        choices=[
                            Choice("commercial", "Commercial"),
                            Choice("support", "Support"),
                            Choice("gestion", "Gestion"),
                        ],
                        style=self.custom_style,
                        qmark="",
                        amark="",
                        long_instruction="Choisissez le département de l'utilisateur",
                        show_cursor=False,
                    ).execute()
                    user_data["department"] = department
            else:
                self.console.print(f"[cyan]Département:[/cyan] [green]{user_data['department']}[/green]")
            
            # Collecte du mot de passe si non déjà fourni
            if "password" not in user_data:
                # Boucle pour permettre de recommencer la saisie du mot de passe
                while True:
                    password = inquirer.secret(
                        message="Mot de passe :",
                        validate=PasswordComplexityValidator(),
                        style=self.custom_style,
                        qmark="",
                        amark="",
                        long_instruction="Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule et un chiffre",
                    ).execute()
                    
                    confirm_password = inquirer.secret(
                        message="Confirmer le mot de passe :",
                        style=self.custom_style,
                        qmark="",
                        amark="",
                        long_instruction="Les mots de passe doivent correspondre",
                    ).execute()
                    
                    # Vérification manuelle de la correspondance
                    if password != confirm_password:
                        self.console.print("[bold red]Les mots de passe ne correspondent pas. Veuillez recommencer.[/bold red]")
                        continue
                    
                    # Si on arrive ici, c'est que les mots de passe correspondent
                    user_data["password"] = password
                    break
            else:
                self.console.print("[cyan]Mot de passe:[/cyan] [green]********[/green]")
            
            # Retourner les données complètes de l'utilisateur
            return user_data
            
        except KeyboardInterrupt:
            # Récupérer le nom du prochain champ à saisir
            next_field = self._get_next_field_to_collect(user_data)
            
            # Proposer à l'utilisateur d'annuler ou de continuer
            choice = self.handle_keyboard_interrupt("création d'un utilisateur")
            
            if choice == "cancel":
                return None
            else:
                # Continuer la saisie avec les données partielles
                return self.show_user_creation_form(db, user_data, is_first_admin)

    def _get_next_field_to_collect(self, user_data):
        """
        Détermine le prochain champ à collecter.
        
        Args:
            user_data (dict): Données utilisateur partiellement collectées
            
        Returns:
            str: Nom du prochain champ à collecter
        """
        fields = ["name", "email", "employee_number", "department", "password"]
        
        for field in fields:
            if field not in user_data:
                return field
            
        return None  # Tous les champs sont remplis

    def handle_keyboard_interrupt(self, action_name):
        """
        Gère l'interruption clavier (Ctrl+C) pendant une action.
        
        Args:
            action_name (str): Nom de l'action en cours
            
        Returns:
            str: "cancel" pour annuler, "continue" pour continuer
        """
        self.clear_screen()
        self.header_title("INTERRUPTION", "magenta")
        
        # Message d'option
        self.console.print(f"[yellow]Vous avez interrompu la {action_name}.[/yellow]")
        self.console.print("\n")
        
        # Proposer les options à l'utilisateur
        from InquirerPy import inquirer
        from InquirerPy.base.control import Choice
        
        choice = inquirer.select(
            message="Que souhaitez-vous faire ?\n",
            choices=[
                Choice("continue", "Continuer la saisie"),
                Choice("cancel", "Annuler et revenir au menu")
            ],
            style=self.custom_style,
            qmark="",
            amark="",
            show_cursor=False,
            long_instruction="Choisissez une option",
        ).execute()
        
        return choice
    
    def show_success_message(self, message):
        """
        Affiche un message de succès.
        
        Args:
            message (str): Le message à afficher
        """
        self.console.print(f"\n[bold green]✅ {message}[/bold green]")
    
    def show_error_message(self, message):
        """
        Affiche un message d'erreur.
        
        Args:
            message (str): Le message d'erreur à afficher
        """
        self.console.print(f"\n[bold red]❌ {message}[/bold red]")
    
    def select_user_to_update(self, users):
        """
        Affiche la liste des utilisateurs et permet d'en sélectionner un à modifier avec recherche fuzzy.
        
        Args:
            users (list): Liste des utilisateurs disponibles
            
        Returns:
            int: ID de l'utilisateur sélectionné ou None si annulé
        """
        self.clear_screen()
        self.header_title("MODIFICATION D'UN UTILISATEUR", "magenta")
        
        if not users:
            self.console.print("[bold red]Aucun utilisateur trouvé[/bold red]")
            return None
        
        # Affichage des utilisateurs
        users_table = self.rich_components.create_users_table(users)
        self.console.print(users_table)
        self.console.print("\n")
        
        # Préparation des choix pour la recherche fuzzy
        from InquirerPy import inquirer

        # Préparation des choix pour le fuzzy search
        choices = [
            {
                "name": f"ID: {user.id} | 👤 {user.name} | 📧 {user.email} | 🪪  {user.employee_number} | 🏢 {user.department.value}",
                "value": user.id
            }
            for user in users
        ]
        
        choices.append({"name": "Annuler", "value": None})
        
        # Utilisation de fuzzy search pour sélectionner un utilisateur
        user_id = inquirer.fuzzy(
            message="Rechercher et sélectionner un utilisateur à modifier (tapez pour filtrer) :\n",
            choices=choices,
            style=self.custom_style,
            default="",
            qmark="",
            amark="",
            mandatory=False,
            long_instruction="Choisissez un utilisateur à modifier"
        ).execute()
    
        
        return user_id
    
    def show_user_update_form(self, user, db):
        """
        Affiche le formulaire de modification d'un utilisateur.
        
        Args:
            user (User): L'utilisateur à modifier
            db: Session de base de données pour les validateurs
            
        Returns:
            dict: Données mises à jour ou un dictionnaire vide si aucune modification
            None: Seulement si l'utilisateur a choisi "Retour au menu"
        """
        self.clear_screen()
        
        # Affichage du titre
        self.header_title("MODIFICATION D'UN UTILISATEUR", "magenta")
        
        # Affichage des informations actuelles de l'utilisateur
        user_info_table = self.rich_components.create_user_info_table(user)
        self.console.print(user_info_table)
        self.console.print("\n")
        
        # Options de modification
        field_choices = [
            Choice(value="name", name="Modifier le nom"),
            Choice(value="email", name="Modifier l'email"),
            Choice(value="employee_number", name="Modifier le numéro d'employé"),
            Choice(value="department", name="Modifier le département"),
            Choice(value="password", name="Modifier le mot de passe"),
        ]
        longest_choice_length = max(len(choice.name) for choice in field_choices) if field_choices else 30
        field_choices.append(Separator(line="─" * longest_choice_length))
        field_choices.append(Choice(value="back", name="Retour au menu précédent"))
        
        
        
        # Sélection du champ à modifier
        field_to_modify = inquirer.select(
            message="Que souhaitez-vous modifier ?\n",
            choices=field_choices,
            style=self.custom_style,
            qmark="",
            amark="",
            show_cursor=False,
            long_instruction="Choisissez le champ à modifier"
        ).execute()
        
        # Retour au menu de gestion des utilisateurs
        if field_to_modify == "back":
            return None
        
        # Récupération de la valeur actuelle
        current_value = getattr(user, field_to_modify) if field_to_modify != "password" else ""
        
        # Texte d'affichage pour chaque champ
        field_display = {
            "name": "Nom",
            "email": "Email",
            "employee_number": "N° Employé",
            "department": "Département",
            "password": "Mot de passe"
        }
        
        # Mise à jour selon le champ sélectionné
        updated_data = {}
        
        if field_to_modify == "name":
            new_value = inquirer.text(
                message=f"{field_display[field_to_modify]}:",
                default=current_value,
                validate=NameValidator(),
                style=self.custom_style,
                qmark="",
                amark="",
                long_instruction="Le nom doit contenir au moins 2 caractères",
            ).execute()
            
            updated_data["name"] = new_value
        
        elif field_to_modify == "email":
            new_value = inquirer.text(
                message=f"{field_display[field_to_modify]}:",
                default=current_value,
                validate=EmailValidator(db, user.id),
                style=self.custom_style,
                qmark="",
            ).execute()
            updated_data["email"] = new_value
        
        elif field_to_modify == "employee_number":
            new_value = inquirer.text(
                message=f"{field_display[field_to_modify]}:",
                default=current_value,
                validate=EmployeeNumberValidator(db, user.id),
                style=self.custom_style,
                qmark="",
            ).execute()
            updated_data["employee_number"] = new_value
        
        elif field_to_modify == "department":
            # Options de départements
            choices = [
                Choice(value="commercial", name="Commercial"),
                Choice(value="support", name="Support"),
                Choice(value="gestion", name="Gestion")
            ]
            
            # Calculer la longueur pour le séparateur
            longest_choice_length = max(len(choice.name) for choice in choices) if choices else 30
            
            # Ajouter un séparateur et l'option Annuler
            choices.append(Separator(line="─" * longest_choice_length))
            choices.append(Choice(value="cancel", name="Retour au menu de modification"))
            
            new_value = inquirer.select(
                message=f"{field_display[field_to_modify]}:",
                choices=choices,
                default=current_value.value if hasattr(current_value, 'value') else current_value,
                style=self.custom_style,
                qmark="",
                amark="",
                show_cursor=False,
                long_instruction="Choisissez le nouveau département de l'utilisateur",
            ).execute()
            
            # Vérifier si l'utilisateur a choisi d'annuler
            if new_value == "cancel":
                return self.show_user_update_form(user, db)
            elif new_value == "gestion" and (not hasattr(current_value, 'value') or current_value.value != "gestion"):
                self.console.print("\n[bold red]⚠️  ATTENTION :[/bold red] [yellow]Attribuer le département 'Gestion' accorde des privilèges administratifs étendus à cet utilisateur![/yellow]\n")
                confirm_choices = [
                    Choice(value="confirm", name="Je comprends et je confirme"),
                    Choice(value="cancel", name="Je ne souhaite pas modifier le département de l'utilisateur")
                ]
                
                confirmation = inquirer.select(
                    message="Voulez-vous vraiment modifier le département de cet utilisateur en 'Gestion' ?\n",
                    choices=confirm_choices,
                    style=self.custom_style,
                    qmark="",
                    amark="",
                    show_cursor=False,
                    long_instruction="Choisissez une option",
                    ).execute()  
                
                if confirmation == "cancel":
                    # Retourner au menu de modification
                    return self.show_user_update_form(user, db)
                else:
                    updated_data["department"] = new_value
            else:
                updated_data["department"] = new_value
        
        elif field_to_modify == "password":
            while True:
                password = inquirer.secret(
                    message="Nouveau mot de passe:",
                    validate=PasswordComplexityValidator(),
                    style=self.custom_style,
                    qmark="",
                ).execute()
                
                confirm_password = inquirer.secret(
                    message="Confirmer le mot de passe:",
                    style=self.custom_style,
                    qmark="",
                ).execute()
                
                if password != confirm_password:
                    self.console.print("[bold red]Les mots de passe ne correspondent pas. Veuillez recommencer.[/bold red]")
                    continue
                
                updated_data["password"] = password
                break

        
        return updated_data
    
    def show_info_message(self, message):
        """
        Affiche un message d'information.
        
        Args:
            message (str): Le message à afficher
        """
        self.console.print(f"\n[bold blue]ℹ️ {message}[/bold blue]")
    
    def select_user_to_delete(self, users):
        """
        Affiche la liste des utilisateurs et permet d'en sélectionner un à supprimer.
        
        Args:
            users (list): Liste des utilisateurs disponibles
            
        Returns:
            int: ID de l'utilisateur sélectionné ou None si annulé
        """
        self.clear_screen()
        
        # Affichage du titre
        self.header_title("SUPPRESSION D'UN UTILISATEUR", "magenta")
        
        if not users:
            self.console.print("[bold red]Aucun utilisateur trouvé[/bold red]")
            return None
        
        # Affichage des utilisateurs
        users_table = self.rich_components.create_users_table(users)
        self.console.print(users_table)
        self.console.print("\n")
        
        # Préparation des choix pour la recherche fuzzy
        from InquirerPy import inquirer

        # Préparation des choix pour le fuzzy search
        choices = [
            {
                "name": f"{user.id} | {user.name} | {user.email} | {user.department.value}",
                "value": user.id
            }
            for user in users
        ]
        
        # Ajout d'une option pour annuler
        choices.append({"name": "Annuler", "value": None})
        
        # Utilisation de fuzzy search pour sélectionner un utilisateur
        user_id = inquirer.fuzzy(
            message="Rechercher et sélectionner un utilisateur à supprimer (tapez pour filtrer):",
            choices=choices,
            style=self.custom_style,
            default="",
            mandatory=False,
            long_instruction="Choisissez un utilisateur à supprimer"
        ).execute()
        
        # Si l'utilisateur a annulé avec Escape ou a choisi "Annuler"
        if user_id is None:
            return None
        
        return user_id

    def confirm_deletion(self, user):
        """
        Demande une confirmation avant de supprimer un utilisateur.
        
        Args:
            user (User): L'utilisateur à supprimer
            
        Returns:
            bool: True si la suppression est confirmée, False sinon
        """
        self.clear_screen()
        
        # Affichage du titre
        self.header_title("CONFIRMATION DE SUPPRESSION", "magenta")
        
        # Affichage des informations de l'utilisateur
        user_info_table = self.rich_components.create_user_info_table(user)
        self.console.print(user_info_table)
        self.console.print("\n")
        
        # Message d'avertissement
        self.console.print("[bold red]ATTENTION: Cette action est irréversible![/bold red]")
        self.console.print("[yellow]Toutes les données associées à cet utilisateur seront perdues.[/yellow]\n")
        
        # Demande de confirmation
        from InquirerPy import inquirer
        from InquirerPy.base.control import Choice
        
        confirm = inquirer.select(
            message="Êtes-vous sûr de vouloir supprimer cet utilisateur ?",
            choices=[
                Choice(value=True, name="Oui"),
                Choice(value=False, name="Non")
            ],
            style=self.custom_style,
            qmark="",
            amark="",
            show_cursor=False,
            long_instruction="Choisissez une option",
        ).execute()
        
        return confirm 
    