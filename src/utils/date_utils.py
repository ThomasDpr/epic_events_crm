"""Utilitaires pour la manipulation et le formatage des dates."""

def format_datetime(datetime_obj, format_str="%d/%m/%Y %H:%M"):
    """
    Formate un objet datetime en chaîne de caractères selon le format spécifié.
    
    Args:
        datetime_obj: L'objet datetime à formater
        format_str (str): Format de date à utiliser (par défaut: JJ/MM/AAAA HH:MM)
        
    Returns:
        str: La date formatée ou "N/A" si datetime_obj est None
    """
    if not datetime_obj:
        return "N/A"
    
    return datetime_obj.strftime(format_str)


def format_date(datetime_obj, format_str="%d/%m/%Y"):
    """
    Formate un objet datetime en date simple sans l'heure.
    
    Args:
        datetime_obj: L'objet datetime à formater
        format_str (str): Format de date à utiliser (par défaut: JJ/MM/AAAA)
        
    Returns:
        str: La date formatée ou "N/A" si datetime_obj est None
    """
    return format_datetime(datetime_obj, format_str)


def get_relative_date(datetime_obj):
    """
    Retourne une représentation relative de la date par rapport à aujourd'hui.
    Par exemple: "Aujourd'hui", "Hier", "Il y a 2 jours", etc.
    
    Args:
        datetime_obj: L'objet datetime à évaluer
        
    Returns:
        str: La date relative ou "N/A" si datetime_obj est None
    """
    if not datetime_obj:
        return "N/A"
        
    from datetime import datetime, timezone
    
    now = datetime.now(timezone.utc)
    delta = now - datetime_obj
    
    if delta.days == 0:
        return "Aujourd'hui"
    elif delta.days == 1:
        return "Hier"
    elif delta.days < 7:
        return f"Il y a {delta.days} jours"
    else:
        return format_date(datetime_obj)