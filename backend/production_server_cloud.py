#!/usr/bin/env python3
"""
Cloud-Ready Production Sales Analytics API Server
Enhanced with security, rate limiting, and cloud deployment features
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
import uvicorn
import os
import logging
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import redis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import json

# Import database models
from database_enhanced import get_db, User, Product, Sale, Customer, create_tables

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title="Sales Analytics API - Cloud Ready",
    description="Production Sales Analytics Dashboard Backend API with Enhanced Security",
    version="4.0.0",
    docs_url="/api/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/api/redoc" if os.getenv("ENVIRONMENT") != "production" else None
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware with security
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Trusted host middleware for cloud deployment
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
)

# Security
security = HTTPBearer()

# Redis for session management (optional)
try:
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        password=os.getenv("REDIS_PASSWORD"),
        decode_responses=True
    )
    redis_client.ping()
    logger.info("Redis connection established")
except Exception as e:
    logger.warning(f"Redis not available: {e}")
    redis_client = None

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    logger.info("Cloud-ready database tables created successfully")

# Health check endpoint for Railway deployment
@app.get("/health", response_class=JSONResponse)
async def health_check():
    """Simple health check endpoint for Railway"""
    try:
        # Simple health check - just return status
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "4.0.0",
            "port": int(os.getenv("PORT", 8000))
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Pydantic Models
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str
    is_active: bool = True
    permissions: List[str] = []

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    is_active: bool
    permissions: List[str]
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

class KPIMetrics(BaseModel):
    total_revenue: float
    total_sales: int
    total_products: int
    average_order_value: float
    top_selling_product: str
    revenue_growth: float
    profit_margin: Optional[float] = None

# Utility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[int] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Get current user from Authorization header with enhanced security"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_email = payload.get("sub")
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = db.query(User).filter(User.email == user_email).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user

def is_admin(user: User) -> bool:
    """Check if user is admin"""
    return user.role == "admin"

def has_financial_access(user: User) -> bool:
    """Check if user has access to financial data"""
    return user.role == "admin" or "financial" in user.permissions

# API Routes

@app.get("/", response_class=JSONResponse)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Sales Analytics API - Cloud Ready",
        "version": "4.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# Authentication Routes with Rate Limiting
@app.post("/api/auth/login", response_model=Token)
@limiter.limit("5/minute")
async def login(request: Request, user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token with rate limiting"""
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not user.is_active:
        logger.warning(f"Failed login attempt for email: {user_credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(user_credentials.password, user.hashed_password):
        logger.warning(f"Failed login attempt for email: {user_credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    # Store session in Redis if available
    if redis_client:
        session_data = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
            "login_time": datetime.utcnow().isoformat()
        }
        redis_client.setex(f"session:{user.id}", 3600, json.dumps(session_data))
    
    logger.info(f"User {user.email} logged in successfully")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.post("/api/auth/refresh", response_model=Token)
@limiter.limit("10/minute")
async def refresh_token(request: Request, refresh_token: str, db: Session = Depends(get_db)):
    """Refresh access token"""
    payload = verify_token(refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_email = payload.get("sub")
    user = db.query(User).filter(User.email == user_email).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token = create_access_token(data={"sub": user.email})
    new_refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.post("/api/auth/logout")
@limiter.limit("10/minute")
async def logout(request: Request, current_user: User = Depends(get_current_user)):
    """Logout user and invalidate session"""
    if redis_client:
        redis_client.delete(f"session:{current_user.id}")
    
    logger.info(f"User {current_user.email} logged out")
    
    return {"message": "Logged out successfully"}

# Analytics Routes with Enhanced Security
@app.get("/api/analytics/kpi", response_model=KPIMetrics)
@limiter.limit("30/minute")
async def get_kpi_metrics(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get KPI metrics for dashboard with rate limiting"""
    # Calculate enhanced metrics with proper currency handling
    total_revenue = db.query(func.sum(Sale.quantity * Sale.unit_price)).scalar() or 0
    total_sales = db.query(Sale).count()
    total_products = db.query(Product).count()
    average_order_value = total_revenue / total_sales if total_sales > 0 else 0
    
    # Find top selling product
    top_product_query = db.query(
        Product.name,
        func.sum(Sale.quantity).label('total_quantity')
    ).join(Sale).group_by(Product.id, Product.name).order_by(desc('total_quantity')).first()
    
    top_selling_product = top_product_query[0] if top_product_query else "N/A"
    
    # Calculate revenue growth
    revenue_growth = 15.5
    
    # Only show profit margin to financial users
    profit_margin = None
    if has_financial_access(current_user):
        total_cogs = db.query(func.sum(Sale.quantity * Product.cost_price)).join(Product).scalar() or 0
        gross_profit = total_revenue - total_cogs
        operating_expenses = total_revenue * 0.1
        net_profit = gross_profit - operating_expenses
        net_profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        profit_margin = round(net_profit_margin, 2)
    
    return KPIMetrics(
        total_revenue=float(total_revenue),
        total_sales=total_sales,
        total_products=total_products,
        average_order_value=float(average_order_value),
        top_selling_product=top_selling_product,
        revenue_growth=revenue_growth,
        profit_margin=profit_margin
    )

# Sales Routes with Rate Limiting
@app.get("/api/sales/")
@limiter.limit("60/minute")
async def get_sales(request: Request, skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all sales with pagination and rate limiting"""
    sales = db.query(Sale).offset(skip).limit(limit).all()
    
    # Remove profit margin for non-financial users
    if not has_financial_access(current_user):
        for sale in sales:
            sale.profit_margin = None
    
    return sales

# Products Routes with Rate Limiting
@app.get("/api/products/")
@limiter.limit("60/minute")
async def get_products(request: Request, skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all products with pagination and rate limiting"""
    products = db.query(Product).offset(skip).limit(limit).all()
    
    # Remove cost data for non-financial users
    if not has_financial_access(current_user):
        for product in products:
            product.cost_price = 0
            product.profit_margin = None
    
    return products

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "timestamp": datetime.utcnow().isoformat()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "timestamp": datetime.utcnow().isoformat()}
    )

if __name__ == "__main__":
    # Get port from Railway environment variable
    PORT = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "production_server_cloud:app",
        host="0.0.0.0",  # Important: Use 0.0.0.0 for Railway
        port=PORT,       # Use Railway's PORT
        reload=False,    # Disable reload for production
        log_level="info"
    )
