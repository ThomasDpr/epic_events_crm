import enum
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import relationship

from database.config import Base


class DepartmentType(enum.Enum):
    COMMERCIAL = "commercial"
    SUPPORT = "support"
    GESTION = "gestion"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    employee_number = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    department = Column(Enum(DepartmentType), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    
    # Relation avec les clients
    clients = relationship("Client", back_populates="sales_contact")
    
    # Relation avec les contrats
    contracts = relationship("Contract", back_populates="sales_contact")

    # Relation avec les événements
    supported_events = relationship("Event", back_populates="support_contact")


    def __repr__(self):
        return f"<User(employee_number='{self.employee_number}', name='{self.name}', department='{self.department}')>"