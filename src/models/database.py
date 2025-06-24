"""
Database models for Payment Service
"""

import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, Boolean, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class PaymentMethod(Base):
    """Payment method model - simplified card storage"""
    __tablename__ = "payment_methods"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    card_last_four = Column(String(4), nullable=False)
    card_brand = Column(String(20), nullable=True)  # visa, mastercard, etc.
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    transactions = relationship("Transaction", back_populates="payment_method")

class Transaction(Base):
    """Transaction model - simplified payment records"""
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ride_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String(20), default="completed")  # completed, failed
    payment_method_id = Column(UUID(as_uuid=True), ForeignKey("payment_methods.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    payment_method = relationship("PaymentMethod", back_populates="transactions")
