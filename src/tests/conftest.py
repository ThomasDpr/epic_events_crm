import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.config import Base
from models.user import DepartmentType, User
from services.user_service import UserService


@pytest.fixture
def in_memory_db():
    """Crée une base de données SQLite en mémoire pour les tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


@pytest.fixture
def user_service(in_memory_db):
    """Crée un service utilisateur avec une session de BD en mémoire."""
    return UserService(in_memory_db)