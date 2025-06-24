"""
Payment methods management endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_

from src.models.database import PaymentMethod
from src.models.schemas import PaymentMethodCreate, PaymentMethodResponse, MessageResponse
from src.utils.auth import get_current_user, TokenData

router = APIRouter()

async def get_db() -> AsyncSession:
    """Placeholder for database dependency"""
    # This will be overridden by the main app
    pass

@router.post("/payment-methods", response_model=PaymentMethodResponse, status_code=status.HTTP_201_CREATED)
async def add_payment_method(
    payment_method: PaymentMethodCreate,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a new payment method for the user"""
    
    # If this is set as default, unset other defaults
    if payment_method.is_default:
        stmt = select(PaymentMethod).where(
            and_(PaymentMethod.user_id == current_user.user_id, PaymentMethod.is_default == True)
        )
        result = await db.execute(stmt)
        existing_defaults = result.scalars().all()
        
        for default_method in existing_defaults:
            default_method.is_default = False
    
    # Create new payment method
    db_payment_method = PaymentMethod(
        user_id=current_user.user_id,
        card_last_four=payment_method.card_last_four,
        card_brand=payment_method.card_brand,
        is_default=payment_method.is_default
    )
    
    db.add(db_payment_method)
    await db.commit()
    await db.refresh(db_payment_method)
    
    return db_payment_method

@router.get("/payment-methods", response_model=List[PaymentMethodResponse])
async def get_payment_methods(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all payment methods for the current user"""
    
    stmt = select(PaymentMethod).where(PaymentMethod.user_id == current_user.user_id)
    result = await db.execute(stmt)
    payment_methods = result.scalars().all()
    
    return payment_methods

@router.delete("/payment-methods/{method_id}", response_model=MessageResponse)
async def delete_payment_method(
    method_id: str,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a payment method"""
    
    stmt = select(PaymentMethod).where(
        and_(PaymentMethod.id == method_id, PaymentMethod.user_id == current_user.user_id)
    )
    result = await db.execute(stmt)
    payment_method = result.scalar_one_or_none()
    
    if not payment_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )
    
    await db.delete(payment_method)
    await db.commit()
    
    return MessageResponse(message="Payment method deleted successfully")
