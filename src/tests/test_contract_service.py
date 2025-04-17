"""
Tests pour le service contrat (ContractService).
"""
from datetime import datetime

import pytest

from models.client import Client
from models.contract import Contract
from models.event import Event
from models.user import User
from services.client_service import ClientService
from services.contract_service import ContractService


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


@pytest.fixture
def test_client(client_service, commercial_user):
    """Crée un client pour les tests."""
    return client_service.create_client(
        full_name="Client Test",
        email="client@company.com",
        phone="+33123456789",
        company_name="Company Test",
        sales_contact_id=commercial_user.id
    )


@pytest.fixture
def contract_service(in_memory_db):
    """Crée un service contrat avec une session de BD en mémoire."""
    return ContractService(in_memory_db)


def test_create_contract(contract_service, test_client):
    """Test de la création d'un contrat."""
    # Création d'un contrat
    contract = contract_service.create_contract(
        client_id=test_client.id,
        total_amount=10000.0,
        remaining_amount=10000.0,
        is_signed=False
    )
    
    # Vérification que le contrat a été créé correctement
    assert contract is not None
    assert contract.id is not None
    assert contract.client_id == test_client.id
    assert contract.sales_contact_id == test_client.sales_contact_id
    assert contract.total_amount == 10000.0
    assert contract.remaining_amount == 10000.0
    assert contract.is_signed is False


def test_get_contract_by_id(contract_service, test_client):
    """Test de la récupération d'un contrat par son ID."""
    # Création d'un contrat
    contract = contract_service.create_contract(
        client_id=test_client.id,
        total_amount=5000.0,
        remaining_amount=2500.0,
        is_signed=True
    )
    
    # Récupération du contrat par son ID
    retrieved_contract = contract_service.get_contract_by_id(contract.id)
    
    # Vérification que le contrat récupéré est correct
    assert retrieved_contract is not None
    assert retrieved_contract.id == contract.id
    assert retrieved_contract.client_id == test_client.id
    assert retrieved_contract.total_amount == 5000.0
    assert retrieved_contract.remaining_amount == 2500.0
    assert retrieved_contract.is_signed is True


def test_get_client_contracts(contract_service, test_client, client_service, commercial_user):
    """Test de la récupération des contrats d'un client."""
    # Création d'un second client
    other_client = client_service.create_client(
        full_name="Other Client",
        email="other@company.com",
        phone="+33987654321",
        company_name="Other Company",
        sales_contact_id=commercial_user.id
    )
    
    # Création de contrats pour chaque client
    contract1 = contract_service.create_contract(
        client_id=test_client.id,
        total_amount=10000.0,
        remaining_amount=10000.0,
        is_signed=False
    )
    
    contract2 = contract_service.create_contract(
        client_id=other_client.id,
        total_amount=5000.0,
        remaining_amount=5000.0,
        is_signed=False
    )
    
    # Récupération des contrats du premier client
    contracts = contract_service.get_client_contracts(test_client.id)
    
    # Vérification que seuls les contrats du premier client sont retournés
    assert len(contracts) >= 1
    assert any(c.id == contract1.id for c in contracts)
    assert not any(c.id == contract2.id for c in contracts)
    assert all(c.client_id == test_client.id for c in contracts)


def test_update_contract(contract_service, test_client):
    """Test de la mise à jour d'un contrat."""
    # Création d'un contrat
    contract = contract_service.create_contract(
        client_id=test_client.id,
        total_amount=10000.0,
        remaining_amount=10000.0,
        is_signed=False
    )
    
    # Mise à jour du contrat
    updated_contract = contract_service.update_contract(
        contract.id,
        total_amount=12000.0,
        remaining_amount=8000.0,
        is_signed=True
    )
    
    # Vérification que le contrat a été mis à jour correctement
    assert updated_contract.total_amount == 12000.0
    assert updated_contract.remaining_amount == 8000.0
    assert updated_contract.is_signed is True
    assert updated_contract.client_id == test_client.id  # Inchangé


def test_get_unsigned_contracts(contract_service, test_client):
    """Test de la récupération des contrats non signés."""
    # Création de contrats avec différents statuts
    signed_contract = contract_service.create_contract(
        client_id=test_client.id,
        total_amount=5000.0,
        remaining_amount=5000.0,
        is_signed=True
    )
    
    unsigned_contract = contract_service.create_contract(
        client_id=test_client.id,
        total_amount=10000.0,
        remaining_amount=10000.0,
        is_signed=False
    )
    
    # Récupération des contrats non signés
    unsigned_contracts = contract_service.get_unsigned_contracts()
    
    # Vérification que seuls les contrats non signés sont retournés
    assert len(unsigned_contracts) >= 1
    assert any(c.id == unsigned_contract.id for c in unsigned_contracts)
    assert not any(c.id == signed_contract.id for c in unsigned_contracts)
    assert all(c.is_signed is False for c in unsigned_contracts)


def test_get_unpaid_contracts(contract_service, test_client):
    """Test de la récupération des contrats non entièrement payés."""
    # Création de contrats avec différents montants restants
    paid_contract = contract_service.create_contract(
        client_id=test_client.id,
        total_amount=5000.0,
        remaining_amount=0.0,  # Entièrement payé
        is_signed=True
    )
    
    unpaid_contract = contract_service.create_contract(
        client_id=test_client.id,
        total_amount=10000.0,
        remaining_amount=5000.0,  # Partiellement payé
        is_signed=True
    )
    
    # Récupération des contrats non entièrement payés
    unpaid_contracts = contract_service.get_unpaid_contracts()
    
    # Vérification que seuls les contrats non entièrement payés sont retournés
    assert len(unpaid_contracts) >= 1
    assert any(c.id == unpaid_contract.id for c in unpaid_contracts)
    assert not any(c.id == paid_contract.id for c in unpaid_contracts)
    assert all(c.remaining_amount > 0 for c in unpaid_contracts)
