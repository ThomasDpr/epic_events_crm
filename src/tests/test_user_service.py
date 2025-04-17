"""
Tests simples pour le service utilisateur (UserService).
"""
import pytest

from models.client import Client
from models.contract import Contract
from models.event import Event

# Important: importer tous les modèles pour que SQLAlchemy puisse initialiser correctement
from models.user import DepartmentType, User


def test_create_admin_user(user_service):
    """Test de la création d'un utilisateur administrateur."""
    # Création d'un utilisateur de gestion
    user = user_service.create_user(
        name="Admin Test",
        email="admin@test.com",
        employee_number="123456",
        department="gestion",
        password="Password123"
    )
    
    # Vérification que l'utilisateur a été créé correctement
    assert user is not None
    assert user.id is not None
    assert user.name == "Admin Test"
    assert user.email == "admin@test.com"
    assert user.department == DepartmentType.GESTION


def test_create_user(user_service):
    """Test de la création d'un utilisateur."""
    # Création d'un utilisateur commercial
    user = user_service.create_user(
        name="Commercial Test",
        email="commercial@test.com",
        employee_number="654321",
        department="commercial",
        password="Password123"
    )
    
    # Vérification que l'utilisateur a été créé correctement
    assert user is not None
    assert user.id is not None
    assert user.name == "Commercial Test"
    assert user.email == "commercial@test.com"
    assert user.department == DepartmentType.COMMERCIAL


def test_get_all_users(user_service):
    """Test de la récupération de tous les utilisateurs."""
    # Création de plusieurs utilisateurs
    user_service.create_user(
        name="User 1",
        email="user1@test.com",
        employee_number="111111",
        department="commercial",
        password="Password1"
    )
    
    user_service.create_user(
        name="User 2",
        email="user2@test.com",
        employee_number="222222",
        department="support",
        password="Password2"
    )
    
    # Récupération de tous les utilisateurs
    users = user_service.get_all_users()
    
    # Vérification qu'au moins 2 utilisateurs sont présents
    assert len(users) >= 2


def test_update_user(user_service):
    """Test de la mise à jour d'un utilisateur."""
    # Création d'un utilisateur
    user = user_service.create_user(
        name="Original Name",
        email="original@test.com",
        employee_number="333333",
        department="support",
        password="Password123"
    )
    
    # Mise à jour de l'utilisateur
    updated_user = user_service.update_user(
        user.id,
        name="Updated Name",
        email="updated@test.com"
    )
    
    # Vérification des modifications
    assert updated_user.name == "Updated Name"
    assert updated_user.email == "updated@test.com"
    assert updated_user.employee_number == "333333"  # Non modifié


def test_get_users_by_department(user_service):
    """Test du filtrage des utilisateurs par département."""
    # Création d'utilisateurs dans différents départements
    user_service.create_user(
        name="Commercial 1",
        email="commercial1@test.com",
        employee_number="444444",
        department="commercial",
        password="Password123"
    )
    
    user_service.create_user(
        name="Support 1",
        email="support1@test.com",
        employee_number="555555",
        department="support",
        password="Password123"
    )
    
    # Récupération des utilisateurs par département
    commercial_users = user_service.get_users_by_department(DepartmentType.COMMERCIAL)
    support_users = user_service.get_users_by_department(DepartmentType.SUPPORT)
    
    # Vérification du filtrage
    assert len(commercial_users) >= 1
    assert all(user.department == DepartmentType.COMMERCIAL for user in commercial_users)
    
    assert len(support_users) >= 1
    assert all(user.department == DepartmentType.SUPPORT for user in support_users)