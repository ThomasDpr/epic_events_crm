from typing import Optional

import bcrypt
import click


def hash_password(password: str) -> str:
    """Hash un mot de passe avec bcrypt."""
    # Génère un salt et hash le mot de passe
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si un mot de passe correspond au hash."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

def validate_password(ctx, param, value):
    """
    Valide la complexité du mot de passe.
    Retourne un message d'erreur si le mot de passe n'est pas valide,
    None sinon.
    """
    if len(value) < 8:
        raise click.BadParameter("Le mot de passe doit contenir au moins 8 caractères")
    if not any(c.isupper() for c in value):
        raise click.BadParameter("Le mot de passe doit contenir au moins une majuscule")
    if not any(c.islower() for c in value):
        raise click.BadParameter("Le mot de passe doit contenir au moins une minuscule")
    if not any(c.isdigit() for c in value):
        raise click.BadParameter("Le mot de passe doit contenir au moins un chiffre")
    return value