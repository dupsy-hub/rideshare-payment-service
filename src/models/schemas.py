"""
Pydantic schemas for request/response validation
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID

# Payment Method Schemas
class PaymentMethodCreate(BaseModel):
    card_last_four: str = Field(..., min_length=4, max_length=4, description="Last 4 digits of card")
    card_brand: Optional[str] = Field(None, max_length=20, description="Card brand (visa, mastercard, etc.)")
    is_default: bool = Field(default=False, description="Set as default payment method")

class PaymentMethodResponse(BaseModel):
    id: UUID
    user_id: UUID
    card_last_four: str
    card_brand: Optional[str]
    is_default: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Transaction Schemas
class TransactionCreate(BaseModel):
    ride_id: UUID = Field(..., description="ID of the ride being paid for")
    amount: Decimal = Field(..., gt=0, description="Payment amount")
    payment_method_id: Optional[UUID] = Field(None, description="Payment method to use")

class TransactionResponse(BaseModel):
    id: UUID
    ride_id: UUID
    user_id: UUID
    amount: Decimal
    status: str
    payment_method_id: Optional[UUID]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Generic Response Schemas
class MessageResponse(BaseModel):
    message: str

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime
    database: str
