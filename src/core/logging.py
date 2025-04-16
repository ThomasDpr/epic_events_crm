import os

import sentry_sdk
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration


def configure_sentry():
    """Configure Sentry pour la journalisation des erreurs"""
    # Récupérer la clé DSN depuis les variables d'environnement
    sentry_dsn = os.getenv("SENTRY_DSN")
    
    # Si la clé DSN n'est pas définie, retourner sans initialiser Sentry
    if not sentry_dsn:
        print("Avertissement: SENTRY_DSN n'est pas défini. La journalisation des erreurs est désactivée.")
        return
    
    # Initialiser Sentry avec les options recommandées
    sentry_sdk.init(
        dsn=sentry_dsn,
        # Activer l'envoi des données PII (personnelles identifiables) par défaut
        send_default_pii=True,
        # Définir l'environnement (développement, production, etc.)
        environment=os.getenv("ENVIRONMENT", "development"),
        # Activer le tracing des performances
        traces_sample_rate=1.0,
        # Intégration avec SQLAlchemy pour suivre les requêtes à la base de données
        integrations=[SqlalchemyIntegration()],
    )
    
    print(f"Sentry initialisé pour l'environnement: {os.getenv('ENVIRONMENT', 'development')}")


def capture_exception(exception, **kwargs):
    """Capture une exception et l'envoie à Sentry avec des données supplémentaires"""
    sentry_sdk.capture_exception(exception)


def capture_message(message, level="info", **kwargs):
    """Capture un message et l'envoie à Sentry avec un niveau spécifique
    
    Args:
        message: Le message à envoyer
        level: Le niveau de gravité (info, warning, error)
        **kwargs: Données supplémentaires à inclure dans le contexte
    """
    # La manière correcte d'ajouter des données supplémentaires est d'utiliser un scope
    with sentry_sdk.push_scope() as scope:
        # Si des données extras sont fournies, les ajouter au scope
        if 'extra' in kwargs:
            for key, value in kwargs['extra'].items():
                scope.set_extra(key, value)
        
        # Définir le niveau du message
        scope.level = level
        
        # Envoyer le message
        sentry_sdk.capture_message(message)


def set_user(user_id, email=None, username=None):
    """Définit l'utilisateur actuel pour le contexte Sentry"""
    sentry_sdk.set_user({"id": user_id, "email": email, "username": username})


def remove_user():
    """Supprime l'utilisateur du contexte Sentry"""
    sentry_sdk.set_user(None)