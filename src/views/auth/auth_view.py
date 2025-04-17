from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from rich.console import Console

from database.config import SessionLocal
from models.user import User
from utils.logging_utils import log_error
from utils.print_utils import PrintUtils
from validators import PasswordValidator, UserExistsValidator
from views.base_view import BaseView


class AuthView(BaseView):
    """
    Vue responsable de l'affichage et de la collecte des informations
    liées à l'authentification.
    """
    
    def __init__(self, custom_style=None):
        """
        Initialise la vue d'authentification.
        
        Args:
            custom_style (dict, optional): Style personnalisé pour InquirerPy
        """
        super().__init__()
        self.custom_style = custom_style or {}
        self.print_utils = PrintUtils()
    def show_auth_menu(self):
        """
        Affiche le menu d'authentification.
        
        Returns:
            str: Action sélectionnée ('login', 'create_first_user' ou 'exit')
        """
        self.clear_screen()
        
        # Vérifier si des utilisateurs existent dans la base de données
        db = SessionLocal()
        user_exists = db.query(User).first() is not None
        db.close()
        
        self.header_title(title_text="Bienvenue dans l'application Epic Events.", color="green")
        
        if not user_exists:
            self.console.print("[bold yellow]Aucun utilisateur n'a été créé. Vous devez configurer un compte administrateur pour commencer.[/bold yellow]\n")
        
        choices = []
        
        if user_exists:
            choices.append(Choice(value="login", name="Se connecter"))
        else:
            choices.append(Choice(value="create_first_user", name="Créer un compte"))
        
        longest_choice_length = max(len(choice.name) for choice in choices) if choices else 30
        
        choices.append(Separator(line="─" * longest_choice_length))        
        choices.append(Choice(value="exit", name="Quitter l'application"))
        
        action = inquirer.select(
            message="Que souhaitez-vous faire ?\n",
            choices=choices,
            style=self.custom_style,
            qmark="",
            amark="",
            show_cursor=False,
            long_instruction="Le système de gestion Epic Events vous permet de gérer vos événements, vos clients et vos contacts.",
        ).execute()
        
        return action
    
    def show_login_form(self, db):
        """
        Affiche le formulaire de connexion avec validation à chaque étape.
        
        Args:
            db: Session de base de données pour les validateurs
            
        Returns:
            tuple: (email, password) ou (None, None) si annulé
        """
        self.clear_screen()
        
        self.header_title("Connexion à Epic Events", "green")
        
        # Boucle pour l'email
        email = None
        try:
            email = inquirer.text(
                message="Email:",
                style=self.custom_style,
                qmark="",
                amark="",
                validate=UserExistsValidator(db),
                long_instruction="\nVeuillez saisir l'adresse email associée à votre compte Epic Events.\nAppuyez sur Ctrl+C pour revenir au menu principal",
            ).execute()
        except KeyboardInterrupt:
            return None, None
        
        # Boucle pour le mot de passe
        password = None
        attempts = 0
        max_attempts = 3
        
        while password is None and attempts < max_attempts:
            try:
                # Afficher le nombre de tentatives restantes
                remaining = max_attempts - attempts
                instruction = f"Entrez votre mot de passe. {remaining} tentative(s) restante(s).\nAppuyez sur Ctrl+C pour revenir au menu principal"
                
                password_input = inquirer.secret(
                    message="Mot de passe:",
                    long_instruction=instruction,
                    style=self.custom_style,
                    validate=PasswordValidator(),
                    qmark="",
                    amark="",
                ).execute()
                
                # Vérifier manuellement si le mot de passe est correct
                from core.auth import AuthManager
                auth_manager = AuthManager(db)
                user = auth_manager.authenticate(email, password_input)
                
                if user:
                    password = password_input
                else:
                    attempts += 1
                    if attempts < max_attempts:
                        self.print_utils.print_error(f"Mot de passe incorrect. {max_attempts - attempts} tentative(s) restante(s).")
            
            except KeyboardInterrupt:
                return None, None
        
        # Si on a atteint le nombre maximum de tentatives sans succès
        if password is None:
            self.print_utils.print_error("Nombre maximal de tentatives atteint. Veuillez réessayer plus tard.")
            
            error = ValueError(f"Tentatives de connexion maximales atteintes pour {email}")

            log_error(
                action="login_lockout",
                message=f"{attempts} tentatives échouées pour la connexion avec l'email: {email}",
                exception=error,
                extra_data={
                    "email": email,
                    "failed_attempts": attempts,
                    "max_attempts": max_attempts
                }
            )
            # Afficher le sélecteur pour revenir au menu principal
            inquirer.select(
                message="",
                choices=[
                    Choice("cancel", "Retour au menu principal")
                ],
                style=self.custom_style,
                qmark="",
                amark="",
                show_cursor=False,
            ).execute()
            
            return None, None
        
        return email, password
    
    
    def show_signup_success(self):
        self.clear_screen()
        self.header_title("Inscription réussie !", "green")
        self.console.print("Le premier compte administrateur a été créé avec succès ! Vous pouvez maintenant vous connecter.", style="bold green")
        
        inquirer.select(
            message="",
            choices=[
                Choice("back_to_login", "Retour au menu principal")
            ],
            style=self.custom_style,
            qmark="",
            amark="",
            show_cursor=False,
            long_instruction="Retournez au menu principal pour vous connecter.",
        ).execute()

