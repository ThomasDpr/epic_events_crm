"""
Tests pour le service événement (EventService).
"""
from datetime import datetime, timedelta

import pytest

from models.client import Client
from models.contract import Contract
from models.event import Event
from models.user import DepartmentType, User
from services.client_service import ClientService
from services.contract_service import ContractService
from services.event_service import EventService


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
def support_user(user_service):
    """Crée un utilisateur support pour les tests."""
    return user_service.create_user(
        name="Support Test",
        email="support@test.com",
        employee_number="654321",
        department="support",
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


@pytest.fixture
def signed_contract(contract_service, test_client):
    """Crée un contrat signé pour les tests."""
    return contract_service.create_contract(
        client_id=test_client.id,
        total_amount=10000.0,
        remaining_amount=5000.0,
        is_signed=True  # note a moi meme : le contrat doit être signé pour créer un événement
    )


@pytest.fixture
def event_service(in_memory_db):
    """Crée un service événement avec une session de BD en mémoire."""
    return EventService(in_memory_db)


def test_create_event(event_service, signed_contract):
    """Test de la création d'un événement."""
    # Définition des dates de l'événement
    start_date = datetime.now() + timedelta(days=30)
    end_date = start_date + timedelta(hours=4)
    
    # Création d'un événement
    event = event_service.create_event(
        contract_id=signed_contract.id,
        event_start_date=start_date,
        event_end_date=end_date,
        location="Salle des Fêtes, Paris",
        attendees=100,
        notes="Test event notes"
    )
    
    # Vérification que l'événement a été créé correctement
    assert event is not None
    assert event.id is not None
    assert event.contract_id == signed_contract.id
    assert event.event_start_date == start_date
    assert event.event_end_date == end_date
    assert event.location == "Salle des Fêtes, Paris"
    assert event.attendees == 100
    assert event.notes == "Test event notes"
    assert event.support_contact_id is None  # Pas encore assigné


def test_get_event_by_id(event_service, signed_contract):
    """Test de la récupération d'un événement par son ID."""
    # Création d'un événement
    start_date = datetime.now() + timedelta(days=30)
    end_date = start_date + timedelta(hours=4)
    
    event = event_service.create_event(
        contract_id=signed_contract.id,
        event_start_date=start_date,
        event_end_date=end_date,
        location="Salle des Fêtes, Paris",
        attendees=100,
        notes="Test event notes"
    )
    
    # Récupération de l'événement par son ID
    retrieved_event = event_service.get_event_by_id(event.id)
    
    # Vérification que l'événement récupéré est correct
    assert retrieved_event is not None
    assert retrieved_event.id == event.id
    assert retrieved_event.contract_id == signed_contract.id
    assert retrieved_event.location == "Salle des Fêtes, Paris"


def test_update_event(event_service, signed_contract):
    """Test de la mise à jour d'un événement."""
    # Création d'un événement
    start_date = datetime.now() + timedelta(days=30)
    end_date = start_date + timedelta(hours=4)
    
    event = event_service.create_event(
        contract_id=signed_contract.id,
        event_start_date=start_date,
        event_end_date=end_date,
        location="Original Location",
        attendees=100,
        notes="Original notes"
    )
    
    # Nouvelles dates pour la mise à jour
    new_start_date = start_date + timedelta(days=1)
    new_end_date = new_start_date + timedelta(hours=6)
    
    # Mise à jour de l'événement
    updated_event = event_service.update_event(
        event.id,
        event_start_date=new_start_date,
        event_end_date=new_end_date,
        location="Updated Location",
        attendees=150,
        notes="Updated notes"
    )
    
    # Vérification que l'événement a été mis à jour correctement
    assert updated_event.event_start_date == new_start_date
    assert updated_event.event_end_date == new_end_date
    assert updated_event.location == "Updated Location"
    assert updated_event.attendees == 150
    assert updated_event.notes == "Updated notes"
    assert updated_event.contract_id == signed_contract.id  # Inchangé


def test_assign_event(event_service, signed_contract, support_user):
    """Test de l'assignation d'un événement à un membre de l'équipe support."""
    # Création d'un événement
    start_date = datetime.now() + timedelta(days=30)
    end_date = start_date + timedelta(hours=4)
    
    event = event_service.create_event(
        contract_id=signed_contract.id,
        event_start_date=start_date,
        event_end_date=end_date,
        location="Salle des Fêtes, Paris",
        attendees=100,
        notes="Test event notes"
    )
    
    # Assignation de l'événement à un membre du support
    assigned_event = event_service.assign_event(event.id, support_user.id)
    
    # Vérification que l'événement a été assigné correctement
    assert assigned_event.support_contact_id == support_user.id
    
    # Récupération de l'événement pour confirmer la persistance du changement
    retrieved_event = event_service.get_event_by_id(event.id)
    assert retrieved_event.support_contact_id == support_user.id


def test_get_events_by_support(event_service, signed_contract, support_user, user_service):
    """Test de la récupération des événements assignés à un membre du support."""
    # Création d'un second membre du support
    other_support = user_service.create_user(
        name="Other Support",
        email="other@support.com",
        employee_number="999999",
        department="support",
        password="Password123"
    )
    
    # Création d'événements et assignation à différents membres du support
    start_date = datetime.now() + timedelta(days=30)
    end_date = start_date + timedelta(hours=4)
    
    event1 = event_service.create_event(
        contract_id=signed_contract.id,
        event_start_date=start_date,
        event_end_date=end_date,
        location="Location 1",
        attendees=100,
        notes="Event 1"
    )
    event_service.assign_event(event1.id, support_user.id)
    
    event2 = event_service.create_event(
        contract_id=signed_contract.id,
        event_start_date=start_date + timedelta(days=1),
        event_end_date=end_date + timedelta(days=1),
        location="Location 2",
        attendees=200,
        notes="Event 2"
    )
    event_service.assign_event(event2.id, other_support.id)
    
    # Récupération des événements du premier membre du support
    events = event_service.get_events_by_support(support_user.id)
    
    # Vérification que seuls les événements du premier support sont retournés
    assert len(events) >= 1
    assert any(e.id == event1.id for e in events)
    assert not any(e.id == event2.id for e in events)
    assert all(e.support_contact_id == support_user.id for e in events)


def test_get_events_by_contract(event_service, contract_service, test_client):
    """Test de la récupération des événements associés à un contrat."""
    # Création de deux contrats
    contract1 = contract_service.create_contract(
        client_id=test_client.id,
        total_amount=10000.0,
        remaining_amount=5000.0,
        is_signed=True
    )
    
    contract2 = contract_service.create_contract(
        client_id=test_client.id,
        total_amount=20000.0,
        remaining_amount=20000.0,
        is_signed=True
    )
    
    # Création d'événements pour chaque contrat
    start_date = datetime.now() + timedelta(days=30)
    end_date = start_date + timedelta(hours=4)
    
    event1 = event_service.create_event(
        contract_id=contract1.id,
        event_start_date=start_date,
        event_end_date=end_date,
        location="Location 1",
        attendees=100,
        notes="Event for contract 1"
    )
    
    event2 = event_service.create_event(
        contract_id=contract2.id,
        event_start_date=start_date + timedelta(days=1),
        event_end_date=end_date + timedelta(days=1),
        location="Location 2",
        attendees=200,
        notes="Event for contract 2"
    )
    
    # Récupération des événements du premier contrat
    events = event_service.get_events_by_contract(contract1.id)
    
    # Vérification que seuls les événements du premier contrat sont retournés
    assert len(events) >= 1
    assert any(e.id == event1.id for e in events)
    assert not any(e.id == event2.id for e in events)
    assert all(e.contract_id == contract1.id for e in events)
