"""
Utilitaires de journalisation pour simplifier l'utilisation de Sentry dans l'application.
"""
from core.logging import capture_exception as sentry_capture_exception
from core.logging import capture_message as sentry_capture_message


def log_success(action, message, **extra_data):
    """
    Journalise un succès avec Sentry.
    
    Args:
        action (str): Type d'action (create_user, update_client, etc.)
        message (str): Message descriptif
        **extra_data: Données supplémentaires à logger
    """
    extra = extra_data.copy()
    extra["action"] = action
    extra["status"] = "success"
    
    sentry_capture_message(
        message=message,
        level="info",
        extra=extra
    )


def log_error(action, exception, **extra_data):
    """
    Journalise une erreur avec Sentry.
    
    Args:
        action (str): Type d'action lors de laquelle l'erreur s'est produite
        exception (Exception): L'exception à logger
        **extra_data: Données supplémentaires à logger
    """
    extra = extra_data.copy()
    extra["action"] = action
    extra["status"] = "error"
    extra["error_type"] = type(exception).__name__
    
    # Logger d'abord les détails comme un message
    sentry_capture_message(
        message=f"Erreur pendant {action}: {str(exception)}",
        level="error",
        extra=extra
    )
    
    # Puis capturer l'exception complète avec la stack trace
    sentry_capture_exception(exception)


def log_action(action, user=None, **extra_data):
    """
    Journalise une action utilisateur avec Sentry.
    
    Args:
        action (str): Type d'action (login, logout, view_clients, etc.)
        user (User, optional): L'utilisateur qui effectue l'action
        **extra_data: Données supplémentaires à logger
    """
    extra = extra_data.copy()
    extra["action"] = action
    
    if user:
        extra["user_id"] = user.id
        extra["user_name"] = user.name
        extra["user_email"] = user.email
        extra["user_department"] = user.department.value
    
    sentry_capture_message(
        message=f"Action: {action}" + (f" par {user.name}" if user else ""),
        level="info",
        extra=extra
    )
