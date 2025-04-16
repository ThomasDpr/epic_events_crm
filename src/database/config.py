"""
Configuration de la base de données pour l'application Epic Events CRM.

Ce module établit la connexion à la base de données PostgreSQL et configure les éléments
essentiels de SQLAlchemy (engine, session, Base) utilisés dans toute l'application.
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from utils.print_utils import PrintUtils

# ----------------------------------------------------------------------------------
# 1. CHARGEMENT DE LA CONFIGURATION
# ----------------------------------------------------------------------------------

# Charger les variables d'environnement depuis le fichier .env.db
load_dotenv(Path(__file__).parent / '.env.db')

# Récupérer l'URL de connexion à la base de données depuis les variables d'environnement
database_url = os.getenv('DATABASE_URL')


# ----------------------------------------------------------------------------------
# 2. GESTION DES ERREURS DE CONNEXION
# ----------------------------------------------------------------------------------

def show_docker_connection_error(error):
    """
    Affiche un message d'erreur lorsque la connexion à la base de données échoue,
    pour mon exemple :  parce que le conteneur Docker n'est pas démarré.
    
    Args:
        error: L'exception d'erreur de connexion
    """
    print_utils = PrintUtils()
    print_utils.print_error(message="ERREUR: Impossible de se connecter à la base de données PostgreSQL")
    print_utils.print_warning(message="Vérifiez que Docker est démarré et que le container de la base de données est en cours d'exécution.")
    print("\033[93mCommande pour démarrer Docker et la base de données:\033[0m")
    print("  docker-compose up -d\n")
    
    # Quitter l'application avec un code d'erreur
    # Nous devons arrêter l'application car sans base de données, elle ne peut pas fonctionner
    sys.exit(1)


# ----------------------------------------------------------------------------------
# 3. CRÉATION ET TEST DE L'ENGINE
# ----------------------------------------------------------------------------------

try:
    # L'engine est l'interface de bas niveau avec la base de données
    # C'est comme un "pont" entre Python et PostgreSQL qui permet d'établir des connexions
    engine = create_engine(database_url)
    
    # Test immédiat de la connexion pour vérifier que la base de données est accessible
    # Si ce test échoue, l'application s'arrêtera immédiatement avec un message d'erreur
    connection = engine.connect()
    
    # Fermeture de cette connexion de test une fois qu'on a vérifié qu'elle fonctionne
    # Cela libère la ressource, car nous n'avons plus besoin de cette connexion test
    connection.close()
    
except OperationalError as e:
    # Gestion des erreurs de connexion
    if "Connection refused" in str(e):
        # Erreur typique lorsque Docker n'est pas démarré
        show_docker_connection_error(e)
    else:
        # Autre type d'erreur de connexion, on laisse remonter l'exception
        raise


# ----------------------------------------------------------------------------------
# 4. CONFIGURATION DE SQLALCHEMY
# ----------------------------------------------------------------------------------

# SessionLocal est une "usine à sessions"
# Une session est comme une "conversation" temporaire avec la base de données
# Chaque fois qu'on appelle SessionLocal(), on crée une nouvelle session
SessionLocal = sessionmaker(
    # autocommit=False: Les changements ne sont pas automatiquement validés
    # il faut appeler explicitement session.commit() pour sauvegarder
    autocommit=False,
    
    # autoflush=False: Les changements ne sont pas automatiquement envoyés à la BD
    # avant chaque requête
    autoflush=False,
    
    # bind=engine: Associe cette session factory à notre engine de base de données
    bind=engine
)

# Base est la classe dont tous nos modèles vont hériter
# Elle contient la méta-programmation qui transforme nos classes Python
# en tables dans la base de données
Base = declarative_base()
