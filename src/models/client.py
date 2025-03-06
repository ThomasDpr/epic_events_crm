from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database.config import Base


class Client(Base):
    """Modèle pour les clients d'Epic Events"""
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    
    # Dates
    created_date = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    last_contact_date = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    # Relation avec le commercial
    sales_contact_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    sales_contact = relationship("User", back_populates="clients")

    # Relation avec les contrats
    contracts = relationship("Contract", back_populates="client")


    def __repr__(self):
        return f"<Client(name='{self.full_name}', company='{self.company_name}')>"