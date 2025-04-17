"""Utilitaires pour l'utilisation de InquirerPy."""

from InquirerPy import inquirer
from InquirerPy.base.control import Choice


def select_with_back():
    """
    Crée un menu de sélection avec une option de retour.
    
    Args:
        message (str): Le message à afficher au début du menu
        choices (list): Liste des choix à afficher dans le menu
        
    Returns:
        str: La valeur sélectionnée par l'utilisateur
    """
    return inquirer.select(
        message="",
        choices=[
            Choice(value="back", name="Retour au menu précédent"),
        ],
        default=None,
        qmark="",
        amark="",
        show_cursor=False,
        long_instruction="Retour au menu précédent",
    ).execute()