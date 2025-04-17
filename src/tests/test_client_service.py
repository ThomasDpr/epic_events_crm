"""
Tests pour le service client (ClientService).
"""
import pytest

from models.client import Client
from models.contract import Contract
from models.event import Event
from models.user import DepartmentType, User
from services.client_service import ClientService


@pytest.fixture
def commercial_user(user_service):
    """Crée un utilisateur commercial pour les tests."""
    return user_service.create_user(
        name="Commercial Test",
        email="commercial@test.com",
        employee_number="123456",
        department="commercial",
        password="Password123"
    )


@pytest.fixture
def client_service(in_memory_db):
    """Crée un service client avec une session de BD en mémoire."""
    return ClientService(in_memory_db)


def test_create_client(client_service, commercial_user):
    """Test de la création d'un client."""
    # Création d'un client
    client = client_service.create_client(
        full_name="Client Test",
        email="client@company.com",
        phone="+33123456789",
        company_name="Company Test",
        sales_contact_id=commercial_user.id
    )
    
    # Vérification que le client a été créé correctement
    assert client is not None
    assert client.id is not None
    assert client.full_name == "Client Test"
    assert client.email == "client@company.com"
    assert client.phone == "+33123456789"
    assert client.company_name == "Company Test"
    assert client.sales_contact_id == commercial_user.id


def test_get_client_by_id(client_service, commercial_user):
    """Test de la récupération d'un client par son ID."""
    # Création d'un client
    client = client_service.create_client(
        full_name="Client Test",
        email="client@company.com",
        phone="+33123456789",
        company_name="Company Test",
        sales_contact_id=commercial_user.id
    )
    
    # Récupération du client par son ID
    retrieved_client = client_service.get_client_by_id(client.id)
    
    # Vérification que le client récupéré est correct
    assert retrieved_client is not None
    assert retrieved_client.id == client.id
    assert retrieved_client.full_name == "Client Test"
    assert retrieved_client.email == "client@company.com"


def test_get_commercial_clients(client_service, commercial_user, user_service):
    """Test de la récupération des clients d'un commercial."""
    # Création d'un second commercial
    other_commercial = user_service.create_user(
        name="Other Commercial",
        email="other@test.com",
        employee_number="654321",
        department="commercial",
        password="Password123"
    )
    
    # Création de clients pour chaque commercial
    client1 = client_service.create_client(
        full_name="Client 1",
        email="client1@company.com",
        phone="+33111111111",
        company_name="Company 1",
        sales_contact_id=commercial_user.id
    )
    
    client2 = client_service.create_client(
        full_name="Client 2",
        email="client2@company.com",
        phone="+33222222222",
        company_name="Company 2",
        sales_contact_id=other_commercial.id
    )
    
    # Récupération des clients du premier commercial
    clients = client_service.get_commercial_clients(commercial_user.id)
    
    # Vérification que seuls les clients du premier commercial sont retournés
    assert len(clients) >= 1
    assert any(c.id == client1.id for c in clients)
    assert not any(c.id == client2.id for c in clients)
    
    # Vérification que tous les clients appartiennent au commercial
    assert all(c.sales_contact_id == commercial_user.id for c in clients)


def test_update_client(client_service, commercial_user):
    """Test de la mise à jour d'un client."""
    # Création d'un client
    client = client_service.create_client(
        full_name="Original Name",
        email="original@company.com",
        phone="+33123456789",
        company_name="Original Company",
        sales_contact_id=commercial_user.id
    )
    
    # Mise à jour du client
    updated_client = client_service.update_client(
        client.id,
        full_name="Updated Name",
        email="updated@company.com",
        company_name="Updated Company"
    )
    
    # Vérification que le client a été mis à jour correctement
    assert updated_client.full_name == "Updated Name"
    assert updated_client.email == "updated@company.com"
    assert updated_client.company_name == "Updated Company"
    # Les champs non mis à jour ne devraient pas changer
    assert updated_client.phone == "+33123456789"
    assert updated_client.sales_contact_id == commercial_user.id


def test_reassign_client(client_service, commercial_user, user_service):
    """Test de la réassignation d'un client à un autre commercial."""
    # Création d'un second commercial
    new_commercial = user_service.create_user(
        name="New Commercial",
        email="new@test.com",
        employee_number="987654",
        department="commercial",
        password="Password123"
    )
    
    # Création d'un client
    client = client_service.create_client(
        full_name="Client Test",
        email="client@company.com",
        phone="+33123456789",
        company_name="Company Test",
        sales_contact_id=commercial_user.id
    )
    
    # Réassignation du client au nouveau commercial
    reassigned_client = client_service.reassign_client(client.id, new_commercial.id)
    
    # Vérification que le client a été réassigné correctement
    assert reassigned_client.sales_contact_id == new_commercial.id
    
    # Récupération du client pour confirmer la persistance du changement
    retrieved_client = client_service.get_client_by_id(client.id)
    assert retrieved_client.sales_contact_id == new_commercial.id


def test_get_available_commercials(client_service, user_service):
    """Test de la récupération des commerciaux disponibles."""
    # Création d'utilisateurs dans différents départements
    commercial1 = user_service.create_user(
        name="Commercial 1",
        email="commercial1@test.com",
        employee_number="111111",
        department="commercial",
        password="Password1"
    )
    
    support = user_service.create_user(
        name="Support User",
        email="support@test.com",
        employee_number="222222",
        department="support",
        password="Password2"
    )
    
    # Récupération des commerciaux disponibles
    commercials = client_service.get_available_commercials()
    
    # Vérification que seuls les commerciaux sont retournés
    assert len(commercials) >= 1
    assert any(c.id == commercial1.id for c in commercials)
    assert not any(c.id == support.id for c in commercials)
    assert all(c.department == DepartmentType.COMMERCIAL for c in commercials)
