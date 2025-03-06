from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database.config import Base


class Event(Base):
    """Modèle pour les événements d'Epic Events"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    
    # Relations
    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=False)
    contract = relationship("Contract", back_populates="events")
    
    support_contact_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Nullable car assigné plus tard
    support_contact = relationship("User", back_populates="supported_events")
    
    # Informations de l'événement
    event_start_date = Column(DateTime, nullable=False)
    event_end_date = Column(DateTime, nullable=False)
    location = Column(String, nullable=False)
    attendees = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Event(contract_id={self.contract_id}, start_date={self.event_start_date})>"