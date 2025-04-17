from InquirerPy import inquirer

from utils.inquire_utils import select_with_back


class UserController:
    """
    Contrôleur responsable de la coordination entre les vues et les services
    pour la gestion des utilisateurs.
    """
    
    def __init__(self, user_service, user_view, db_session):
        """
        Initialise le contrôleur utilisateur.
        
        Args:
            user_service (UserService): Service de gestion des utilisateurs
            user_view (UserView): Vue pour l'affichage et la collecte des informations
            db_session: Session de base de données pour les validateurs
        """
        self.service = user_service
        self.view = user_view
        self.db = db_session
    
    def list_users(self):
        """
        Affiche la liste de tous les utilisateurs.
        """
        try:
            users = self.service.get_all_users()
            self.view.display_users_list(users)
            return users
            
        except Exception as e:
            self.view.show_error_message(f"Erreur lors de la récupération des utilisateurs: {str(e)}")
    
    def create_user(self):
        """
        Gère le processus de création d'un nouvel utilisateur.
        Inclut la gestion des interruptions (Ctrl+C) avec reprise de la saisie.
        """
        try:
            # Affichage du formulaire de création et collecte des données
            user_data = self.view.show_user_creation_form(self.db)
            
            # Si l'utilisateur a annulé l'opération
            if user_data is None:
                return
            
            # Si nous arrivons ici, c'est que nous avons les données qui sont valides
            try:
                # Création de l'utilisateur via le service
                user = self.service.create_user(**user_data)
                                
                # Affichage de la liste mise à jour
                users = self.service.get_all_users()
                self.view.display_users_list(users)
                
                self.view.show_success_message(f"Utilisateur {user.name} créé avec succès!")


                from InquirerPy import inquirer
                from InquirerPy.base.control import Choice
                inquirer.select(
                    message="",
                    choices=[
                        Choice(value="back", name="Retour au menu principal"),
                    ],
                    default=None,
                    style=self.view.custom_style,
                    qmark="",
                    amark="",
                    show_cursor=False,
                ).execute()
                
            except Exception as e:
                # Afficher l'erreur et proposer d'annuler ou de réessayer
                self.view.show_error_message(f"Erreur lors de la création de l'utilisateur: {str(e)}")
                from InquirerPy import inquirer
                retry = inquirer.confirm(
                    message="Voulez-vous réessayer?",
                    default=True,
                    style=self.view.custom_style,
                    qmark="",
                ).execute()
                
                if retry:
                    # Réessayer la création sans perdre les données déjà saisies
                    self.create_user()
            
        except Exception as e:
            self.view.show_error_message(f"Erreur lors de la création de l'utilisateur: {str(e)}")
    
    def update_user(self):
        """
        Gère le processus de mise à jour d'un utilisateur existant.
        Permet de modifier plusieurs champs en une seule session.
        """
        try:
            # Récupération de tous les utilisateurs
            users = self.service.get_all_users()
            
            # Sélection de l'utilisateur à modifier
            user_id = self.view.select_user_to_update(users)
            
            # Si l'utilisateur a annulé
            if not user_id:
                return
            
            # Récupération de l'utilisateur sélectionné
            user = self.service.get_user_by_id(user_id)
            
            # Boucle pour permettre des modifications multiples
            while True:
                # Affichage du formulaire de modification
                updated_data = self.view.show_user_update_form(user, self.db)
                
                # Si l'utilisateur a choisi "Retour au menu" ou annulé
                if not updated_data:
                    break
                
                # Mise à jour de l'utilisateur
                self.service.update_user(user_id, **updated_data)
                
                # Mettre à jour l'objet user pour les modifications suivantes
                user = self.service.get_user_by_id(user_id)

        except Exception as e:
            self.view.show_error_message(f"Erreur lors de la mise à jour de l'utilisateur: {str(e)}") 
    
    def delete_user(self):
        """
        Gère le processus de suppression d'un utilisateur existant.
        """
        try:
            # Récupération de tous les utilisateurs
            users = self.service.get_all_users()
            
            # Sélection de l'utilisateur à supprimer
            user_id = self.view.select_user_to_delete(users)
            
            # Si l'utilisateur a annulé
            if not user_id:
                return
            
            # Récupération de l'utilisateur sélectionné
            user = self.service.get_user_by_id(user_id)
            
            # Demande de confirmation
            confirmed = self.view.confirm_deletion(user)
            
            # Si la suppression n'est pas confirmée
            if not confirmed:
                return
            
            # Suppression de l'utilisateur
            self.service.delete_user(user_id)
            
            # Affichage d'un message de succès
            self.view.show_success_message(f"Utilisateur {user.name} supprimé avec succès!")
            
            select_with_back()
        except ValueError as ve:
            self.view.show_error_message(str(ve))
            select_with_back()
        except Exception as e:
            self.view.show_error_message(f"Erreur lors de la suppression de l'utilisateur: {str(e)}") 