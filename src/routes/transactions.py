"""
Transaction processing endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, desc

from models.database import Transaction, PaymentMethod
from models.schemas import TransactionCreate, TransactionResponse
from utils.auth import get_current_user, TokenData

router = APIRouter()

async def get_db() -> AsyncSession:
    """Placeholder for database dependency"""
    # This will be overridden by the main app
    pass

@router.post("/process", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def process_payment(
    transaction: TransactionCreate,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Process a payment for a ride (mock implementation)"""
    
    payment_method_id = transaction.payment_method_id
    
    # If no payment method specified, use the default one
    if not payment_method_id:
        stmt = select(PaymentMethod).where(
            and_(PaymentMethod.user_id == current_user.user_id, PaymentMethod.is_default == True)
        )
        result = await db.execute(stmt)
        default_method = result.scalar_one_or_none()
        
        if not default_method:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No default payment method found. Please specify a payment method."
            )
        
        payment_method_id = default_method.id
    else:
        # Verify the payment method belongs to the user
        stmt = select(PaymentMethod).where(
            and_(PaymentMethod.id == payment_method_id, PaymentMethod.user_id == current_user.user_id)
        )
        result = await db.execute(stmt)
        payment_method = result.scalar_one_or_none()
        
        if not payment_method:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment method not found"
            )
    
    # Mock payment processing - always succeeds
    # In a real system, this would integrate with Stripe, PayStack, etc.
    db_transaction = Transaction(
        ride_id=transaction.ride_id,
        user_id=current_user.user_id,
        amount=transaction.amount,
        status="completed",  # Mock success
        payment_method_id=payment_method_id
    )
    
    db.add(db_transaction)
    await db.commit()
    await db.refresh(db_transaction)
    
    return db_transaction

@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transaction_history(
    limit: int = 50,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get transaction history for the current user"""
    
    stmt = select(Transaction).where(
        Transaction.user_id == current_user.user_id
    ).order_by(desc(Transaction.created_at)).limit(limit)
    
    result = await db.execute(stmt)
    transactions = result.scalars().all()
    
    return transactions

@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific transaction"""
    
    stmt = select(Transaction).where(
        and_(Transaction.id == transaction_id, Transaction.user_id == current_user.user_id)
    )
    result = await db.execute(stmt)
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return transaction
