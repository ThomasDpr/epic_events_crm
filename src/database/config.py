import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Charger les variables d'environnement
load_dotenv(Path(__file__).parent / '.env.db')

# Créer l'engine avec l'URL depuis les variables d'environnement
engine = create_engine(os.getenv('DATABASE_URL'))

# Créer une classe de session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Créer une classe de base pour les modèles
Base = declarative_base()

# Fonction pour obtenir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

def init_db():
    """Initialise la base de données."""
    Base.metadata.create_all(bind=engine)