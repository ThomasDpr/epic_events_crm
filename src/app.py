import sys

from components.auth_component import AuthComponent
from controllers.client_controller import ClientController
from controllers.contract_controller import ContractController
from controllers.event_controller import EventController
from controllers.user_controller import UserController
from core.logging import configure_sentry
from database.config import SessionLocal
from models.user import DepartmentType
from services.client_service import ClientService
from services.contract_service import ContractService
from services.event_service import EventService
from services.user_service import UserService
from views.auth.auth_view import AuthView
from views.client_views import ClientView
from views.contract_views import ContractView
from views.department_views.commercial_view import CommercialView
from views.department_views.gestion_view import GestionView
from views.department_views.support_view import SupportView
from views.event_views import EventView
from views.main_view import MainView
from views.user_views import UserView


class EpicEvents:
    """
    Classe principale du CRM Epic Events.
    
    Point d'entrée central de l'application.
    Elle me permet de coordonner l'ensemble des composants, des services et des vues de l'application.
    """    
    def __init__(self):
        """
        Initialise l'application et tous ses composants.
        
        Ce constructeur suit un ordre précis pour garantir que les dépendances sont
        correctement initialisées avant d'être utilisées:
        1. Configuration des services techniques (Sentry, BDD)
        2. Initialisation des vues
        3. Création des services métier
        4. Configuration de l'authentification
        5. Initialisation des contrôleurs
        """        
        # Configuration de Sentry pour la journalisation des erreurs et des logs utiles
        # Permet en + la capture et l'analyse des exceptions rencontrées par les utilisateurs
        configure_sentry()
        
        # Initialisation de la session de base de données SQLAlchemy
        # Cette session est injectée dans tous les services
        self.db = SessionLocal()
        
        # Initialisation de la vue principale qui fournit le style et les utilitaires communs
        # Cette vue est utilisée par toutes les autres vues pour maintenir une
        # cohérence visuelle dans l'application
        self.main_view = MainView()
        
        # Vue d'authentification - gère l'interface utilisateur pour la connexion
        # et la création du premier compte administrateur
        self.auth_view = AuthView(self.main_view.custom_style)
        
        # Initialisation des vues spécifiques aux entités métier
        # Chaque vue est responsable de l'affichage et de l'interaction avec l'utilisateur
        # pour une entité spécifique (utilisateurs, clients, contrats, événements)
        self.user_view = UserView(self.main_view.custom_style)
        self.client_view = ClientView(self.main_view.custom_style)
        self.contract_view = ContractView(self.main_view.custom_style)
        self.event_view = EventView(self.main_view.custom_style)
        
        # Initialisation des services métier avec injection de la session BDD
        # Ces services implémentent la logique métier et l'accès aux données
        # pour chaque entité du système
        self.user_service = UserService(self.db)
        self.client_service = ClientService(self.db)
        self.contract_service = ContractService(self.db)
        self.event_service = EventService(self.db)
        
        # Configuration du composant d'authentification avec ses dépendances
        # Ce composant encapsule toute la logique liée à l'authentification,
        # la gestion des sessions et la création des utilisateurs
        self.auth_component = AuthComponent(
            self.auth_view,
            self.user_view,
            self.user_service
        )
        
        # Récupération de l'utilisateur connecté (s'il existe)
        self.current_user = self.auth_component.get_current_user()
        
        # Initialisation des contrôleurs avec leurs dépendances
        # Le contrôleur utilisateur est indépendant de l'utilisateur courant
        self.user_controller = UserController(self.user_service, self.user_view, self.db)
        
        # Initialisation des autres contrôleurs qui dépendent de l'utilisateur connecté
        # et de ses permissions
        self.update_controllers()
    
    
    def update_controllers(self):
        """
        Met à jour les contrôleurs avec l'utilisateur actuellement connecté.
        Cette méthode est appelée après chaque connexion réussie pour appliquer
        les permissions du nouvel utilisateur dans les contrôleurs.
        """
        
        # Note : On passe le self.current_user (qui est l'utilisateur connecté)
        # à tous les contrôleurs pour appliquer les permissions associées à son rôle.
        
        self.client_controller = ClientController(
            self.client_service, self.client_view, self.db, self.current_user
        )
        self.contract_controller = ContractController(
            self.contract_service, self.client_service, 
            self.contract_view, self.db, self.current_user
        )
        self.event_controller = EventController(
            self.event_service, self.contract_service, self.user_service,
            self.event_view, self.db, self.current_user
        )
    
    def start(self):
        """
        Point d'entrée principal de l'application - lance la boucle principale.
        Dirige l'utilisateur vers le menu d'authentification ou vers le menu de son département
        selon son état de connexion.
        """        # Boucle principale
        while True:
            if not self.current_user:
                # Si l'utilisateur n'est pas connecté, afficher le menu d'authentification
                self.handle_auth_menu()
            else:
                # Si l'utilisateur est connecté, afficher le menu de son département
                self.handle_department_menu()
    
    def handle_auth_menu(self):
        """
        Gère le menu d'authentification et les actions associées:
        - Connexion à un compte existant
        - Création du premier utilisateur
        - Sortie de l'application
        """
        
        # Affichage du menu d'authentification
        action = self.auth_component.show_auth_menu()
        
        if action == "login":
            # Processus de connexion via le composant d'authentification
            user = self.auth_component.login()
            if user:
                # Si connexion réussie, mettre à jour l'utilisateur courant et les contrôleurs
                self.current_user = user
                self.update_controllers()
        elif action == "create_first_user":
            # Création du premier utilisateur administrateur (département Gestion)
            self.auth_component.signup()
        elif action == "exit":
            # Sortie de l'application
            self.exit()
    
    def handle_department_menu(self):
        """
        Affiche le menu correspondant au département de l'utilisateur connecté.
        Chaque département (Commercial, Support, Gestion) a son propre menu
        avec des fonctionnalités spécifiques adaptées à son rôle suivant le cahier des charges.
        """
        result = None
        
        # Sélection et instanciation de la vue départementale appropriée
        if self.current_user.department == DepartmentType.COMMERCIAL:
            commercial_view = CommercialView(self.main_view, self.current_user, self)
            result = commercial_view.show_department_menu()
            
        elif self.current_user.department == DepartmentType.SUPPORT:
            support_view = SupportView(self.main_view, self.current_user, self)
            result = support_view.show_department_menu()
            
        elif self.current_user.department == DepartmentType.GESTION:
            gestion_view = GestionView(self.main_view, self.current_user, self)
            result = gestion_view.show_department_menu()
        
        # Action commune à tous les départements retournées par les menus
        if result == "logout":
            # Déconnexion de l'utilisateur courant
            if self.auth_component.logout(self.current_user):
                self.current_user = None
        elif result == "exit":
            self.exit()
    
    def exit(self):
        """
        Ferme proprement l'application en:
        - Déconnectant l'utilisateur actuel si nécessaire
        - Fermant toutes les connexions et ressources
        - Affichant un message de sortie
        - Terminant le processus
        """
        
        # Déconnexion de l'utilisateur s'il est connecté
        if self.current_user:
            self.auth_component.logout(self.current_user)
        
        # Fermeture de la base de données
        self.auth_component.close()
        
        # Nettoyage de l'écran
        self.main_view.clear_screen()
        
        # Affichage du message de sortie
        print("\nMerci d'avoir utilisé Epic Events CRM. À bientôt !\n")
        
        # Termination du processus
        sys.exit(0)
