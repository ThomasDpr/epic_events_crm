from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from database.config import Base


class Contract(Base):
    """Modèle pour les contrats d'Epic Events"""
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True)
    
    # Relations
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    client = relationship("Client", back_populates="contracts")
    
    sales_contact_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    sales_contact = relationship("User", back_populates="contracts")
    
    # Informations financières
    total_amount = Column(Float, nullable=False)
    remaining_amount = Column(Float, nullable=False)
    
    # Dates et statut
    creation_date = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    is_signed = Column(Boolean, default=False, nullable=False)
    
    # Relation avec les événements
    events = relationship("Event", back_populates="contract")



    def __repr__(self):
        return f"<Contract(client_id={self.client_id}, total_amount={self.total_amount}, is_signed={self.is_signed})>"