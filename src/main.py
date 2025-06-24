"""
Payment Service - FastAPI Application (Fixed version)
Simplified payment processing for RideShare Pro
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.models.database import Base
from src.routes import payment_methods, transactions, health

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres:password@localhost:5432/rideshare_payments"
)

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting Payment Service...")
    
    # Create tables
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created/verified")
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
    
    yield
    
    logger.info("🛑 Shutting down Payment Service...")

# Create FastAPI app
app = FastAPI(
    title="Payment Service",
    description="Simplified payment processing for RideShare Pro",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Override the placeholder database dependency in routes
def override_get_db():
    return get_db

# Apply the database dependency override to all route modules
payment_methods.get_db = get_db
transactions.get_db = get_db

# For health route, we'll handle it differently since it needs to be optional
async def get_db_for_health():
    try:
        async with AsyncSessionLocal() as session:
            yield session
    except Exception as e:
        logger.warning(f"Database not available for health check: {e}")
        yield None

# Include routers
app.include_router(health.router, prefix="/api/payments", tags=["health"])
app.include_router(payment_methods.router, prefix="/api/payments", tags=["payment-methods"])
app.include_router(transactions.router, prefix="/api/payments", tags=["transactions"])

# Override health route's database dependency
@app.get("/api/payments/health")
async def health_check_override(db: AsyncSession = Depends(get_db_for_health)):
    """Health check endpoint with proper database handling"""
    from datetime import datetime
    from sqlalchemy import text
    
    # Check database connection
    database_status = "connected"
    if db:
        try:
            await db.execute(text("SELECT 1"))
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            database_status = "disconnected"
    else:
        database_status = "not_available"
    
    return {
        "status": "healthy",
        "service": "payment-service",
        "timestamp": datetime.utcnow(),
        "database": database_status
    }

@app.get("/")
async def root():
    return {
        "service": "Payment Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/api/payments/health",
            "docs": "/docs",
            "payment_methods": "/api/payments/payment-methods",
            "transactions": "/api/payments/transactions"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )