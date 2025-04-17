
from core.auth import AuthManager
from database.config import SessionLocal
from utils.logging_utils import log_error, log_success
from utils.print_utils import PrintUtils


class AuthComponent:
    """
    Composant responsable de la gestion de l'authentification.
    """
    
    def __init__(self, auth_view, user_view, user_service):
        """
        Initialise le composant d'authentification.
        
        Args:
            auth_view: Vue d'authentification
            user_view: Vue utilisateur pour les formulaires
            user_service: Service de gestion des utilisateurs
        """
        self.auth_view = auth_view
        self.user_view = user_view
        self.user_service = user_service
        self.db = SessionLocal()
        self.auth_manager = AuthManager(self.db)
        self.print_utils = PrintUtils()
        
    def login(self):
        """
        Gère le processus de connexion.
        
        Returns:
            User: L'utilisateur connecté ou None si échec
        """
        email, password = self.auth_view.show_login_form(self.db)
        
        if email is None or password is None:
            return None
        
        user = self.auth_manager.authenticate(email, password)
        
        
        return user
    
    def logout(self, user):
        """
        Déconnecte l'utilisateur actuel.
        
        Args:
            user: L'utilisateur à déconnecter
            
        Returns:
            bool: True si la déconnexion a réussi
        """
        if user:
            self.auth_manager.logout()
            return True
        return False
    
    def signup(self):
        """
        Gère la création du premier compte administrateur.
        
        Returns:
            User: L'utilisateur créé ou None si échec
        """
        user_data = self.user_view.show_user_creation_form(self.db, is_first_admin=True)
        
        if user_data is None:
            return None
        
        try:
            user = self.user_service.create_user(**user_data)
            
            self.auth_view.show_signup_success()
            return user
            
        except Exception as e:
            self.print_utils.print_error(f"Erreur lors de la création du compte: {str(e)}")
            return None
    
    def get_current_user(self):
        """
        Récupère l'utilisateur actuellement connecté.
        
        Returns:
            User: L'utilisateur connecté ou None
        """
        return self.auth_manager.get_current_user()
    
    def show_auth_menu(self):
        """
        Affiche le menu d'authentification.
        
        Returns:
            str: Action sélectionnée ('login', 'create_first_user' ou 'exit')
        """
        return self.auth_view.show_auth_menu()
    
    def close(self):
        """Ferme la connexion à la base de données"""
        self.db.close()