"""
Health check endpoints
"""

from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.models.schemas import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(lambda: None)):
    """Health check endpoint"""
    
    # Check database connection
    database_status = "connected"
    if db:
        try:
            await db.execute(text("SELECT 1"))
        except Exception:
            database_status = "disconnected"
    else:
        database_status = "not_configured"
    
    return HealthResponse(
        status="healthy",
        service="payment-service",
        timestamp=datetime.utcnow(),
        database=database_status
    )
