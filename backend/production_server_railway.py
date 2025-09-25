"""
Railway-optimized Sales Analytics API Server
Handles missing database gracefully for initial deployment
"""

import os
import logging
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt
from passlib.context import CryptContext
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()

# FastAPI app
app = FastAPI(
    title="Sales Analytics API",
    description="Railway-optimized Sales Analytics System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory data storage (for Railway without database)
users_db = {
    "admin@example.com": {
        "id": 1,
        "email": "admin@example.com",
        "name": "Admin User",
        "role": "admin",
        "hashed_password": pwd_context.hash("admin123"),
        "is_active": True,
        "permissions": ["financial", "analytics", "users", "sales", "products"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    "analyst@example.com": {
        "id": 2,
        "email": "analyst@example.com", 
        "name": "Analyst User",
        "role": "analyst",
        "hashed_password": pwd_context.hash("analyst123"),
        "is_active": True,
        "permissions": ["analytics", "sales", "products"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
}

# Sample data
sales_data = [
    {
        "id": 1,
        "product_name": "Laptop Pro",
        "quantity": 2,
        "unit_price": 1200.00,
        "sale_date": "2024-01-15",
        "customer_name": "John Doe",
        "region": "North America",
        "salesperson": "Alice Smith",
        "total_amount": 2400.00,
        "profit_margin": 25.0
    },
    {
        "id": 2,
        "product_name": "Wireless Mouse",
        "quantity": 5,
        "unit_price": 25.00,
        "sale_date": "2024-01-16",
        "customer_name": "Jane Wilson",
        "region": "Europe",
        "salesperson": "Bob Johnson",
        "total_amount": 125.00,
        "profit_margin": 30.0
    }
]

products_data = [
    {
        "id": 1,
        "name": "Laptop Pro",
        "category": "Electronics",
        "unit_price": 1200.00,
        "cost_price": 900.00,
        "stock_quantity": 50,
        "description": "High-performance laptop",
        "profit_margin": 25.0
    },
    {
        "id": 2,
        "name": "Wireless Mouse",
        "category": "Accessories",
        "unit_price": 25.00,
        "cost_price": 17.50,
        "stock_quantity": 200,
        "description": "Ergonomic wireless mouse",
        "profit_margin": 30.0
    }
]

# Pydantic models
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "viewer"
    permissions: List[str] = []
    is_active: bool = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    permissions: List[str]
    created_at: datetime
    updated_at: datetime

class LoginRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class SaleCreate(BaseModel):
    product_name: str
    quantity: int
    unit_price: float
    sale_date: str
    customer_name: str
    region: str
    salesperson: str

class ProductCreate(BaseModel):
    name: str
    category: str
    unit_price: float
    cost_price: float
    stock_quantity: int
    description: str

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = users_db.get(email)
    if user is None:
        raise credentials_exception
    return user

def has_financial_access(user: dict) -> bool:
    """Check if user has financial data access"""
    if user["role"] == "admin":
        return True
    return "financial" in user.get("permissions", [])

# Routes
@app.get("/")
async def root():
    return {
        "message": "Sales Analytics API - Railway Deployment",
        "status": "running",
        "version": "1.0.0",
        "database": "in-memory (add PostgreSQL for production)"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "in-memory"
    }

@app.post("/api/auth/login", response_model=Token)
async def login(login_data: LoginRequest):
    user = users_db.get(login_data.email)
    if not user or not verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/analytics/kpis")
async def get_kpis(current_user: dict = Depends(get_current_user)):
    """Get key performance indicators"""
    try:
        # Calculate KPIs from sample data
        total_revenue = sum(sale["total_amount"] for sale in sales_data)
        total_sales = len(sales_data)
        total_products = len(products_data)
        
        # Calculate profit metrics
        total_cogs = sum(sale["total_amount"] * (1 - sale["profit_margin"]/100) for sale in sales_data)
        gross_profit = total_revenue - total_cogs
        operating_expenses = total_revenue * 0.15  # Assume 15% operating expenses
        net_profit = gross_profit - operating_expenses
        
        # Calculate margins
        gross_profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
        net_profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        kpis = {
            "total_revenue": total_revenue,
            "total_sales": total_sales,
            "total_products": total_products,
            "total_cogs": total_cogs,
            "gross_profit": gross_profit,
            "operating_expenses": operating_expenses,
            "net_profit": net_profit,
            "gross_profit_margin": round(gross_profit_margin, 2),
            "net_profit_margin": round(net_profit_margin, 2)
        }
        
        # Hide financial details if user doesn't have access
        if not has_financial_access(current_user):
            kpis = {k: v for k, v in kpis.items() if k not in ["total_cogs", "gross_profit", "operating_expenses", "net_profit", "gross_profit_margin", "net_profit_margin"]}
        
        return kpis
    except Exception as e:
        logger.error(f"Error calculating KPIs: {e}")
        raise HTTPException(status_code=500, detail="Error calculating KPIs")

@app.get("/api/sales")
async def get_sales(current_user: dict = Depends(get_current_user)):
    """Get all sales data"""
    return sales_data

@app.post("/api/sales")
async def create_sale(sale: SaleCreate, current_user: dict = Depends(get_current_user)):
    """Create a new sale"""
    new_sale = {
        "id": len(sales_data) + 1,
        "product_name": sale.product_name,
        "quantity": sale.quantity,
        "unit_price": sale.unit_price,
        "sale_date": sale.sale_date,
        "customer_name": sale.customer_name,
        "region": sale.region,
        "salesperson": sale.salesperson,
        "total_amount": sale.quantity * sale.unit_price,
        "profit_margin": 25.0  # Default profit margin
    }
    sales_data.append(new_sale)
    return new_sale

@app.get("/api/products")
async def get_products(current_user: dict = Depends(get_current_user)):
    """Get all products"""
    # Hide cost and profit data if user doesn't have financial access
    if has_financial_access(current_user):
        return products_data
    else:
        return [
            {k: v for k, v in product.items() if k not in ["cost_price", "profit_margin"]}
            for product in products_data
        ]

@app.post("/api/products")
async def create_product(product: ProductCreate, current_user: dict = Depends(get_current_user)):
    """Create a new product"""
    if current_user["role"] not in ["admin", "analyst"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    new_product = {
        "id": len(products_data) + 1,
        "name": product.name,
        "category": product.category,
        "unit_price": product.unit_price,
        "cost_price": product.cost_price,
        "stock_quantity": product.stock_quantity,
        "description": product.description,
        "profit_margin": ((product.unit_price - product.cost_price) / product.unit_price * 100) if product.unit_price > 0 else 0
    }
    products_data.append(new_product)
    return new_product

@app.get("/api/users")
async def get_users(current_user: dict = Depends(get_current_user)):
    """Get all users (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return [
        UserResponse(
            id=user["id"],
            name=user["name"],
            email=user["email"],
            role=user["role"],
            is_active=user["is_active"],
            permissions=user["permissions"],
            created_at=user["created_at"],
            updated_at=user["updated_at"]
        )
        for user in users_db.values()
    ]

@app.post("/api/users", response_model=UserResponse)
async def create_user(user: UserCreate, current_user: dict = Depends(get_current_user)):
    """Create a new user (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = {
        "id": max([u["id"] for u in users_db.values()]) + 1,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "hashed_password": get_password_hash(user.password),
        "is_active": user.is_active,
        "permissions": user.permissions,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    users_db[user.email] = new_user
    
    return UserResponse(
        id=new_user["id"],
        name=new_user["name"],
        email=new_user["email"],
        role=new_user["role"],
        is_active=new_user["is_active"],
        permissions=new_user["permissions"],
        created_at=new_user["created_at"],
        updated_at=new_user["updated_at"]
    )

@app.put("/api/users/{user_id}")
async def update_user(user_id: int, user_update: UserUpdate, current_user: dict = Depends(get_current_user)):
    """Update a user (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Find user by ID
    user_to_update = None
    user_email = None
    for email, user in users_db.items():
        if user["id"] == user_id:
            user_to_update = user
            user_email = email
            break
    
    if not user_to_update:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    if user_update.name is not None:
        user_to_update["name"] = user_update.name
    if user_update.email is not None:
        # Remove old email entry and add new one
        if user_update.email != user_email:
            users_db[user_update.email] = user_to_update
            del users_db[user_email]
    if user_update.role is not None:
        user_to_update["role"] = user_update.role
    if user_update.permissions is not None:
        user_to_update["permissions"] = user_update.permissions
    if user_update.is_active is not None:
        user_to_update["is_active"] = user_update.is_active
    
    user_to_update["updated_at"] = datetime.utcnow()
    
    return {"message": "User updated successfully"}

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int, current_user: dict = Depends(get_current_user)):
    """Delete a user (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Find and remove user
    user_to_delete = None
    user_email = None
    for email, user in users_db.items():
        if user["id"] == user_id:
            user_to_delete = user
            user_email = email
            break
    
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")
    
    del users_db[user_email]
    return {"message": "User deleted successfully"}

if __name__ == "__main__":
    # Get port from Railway environment variable
    PORT = int(os.getenv("PORT", 8000))
    
    print(f"🚀 Starting Sales Analytics API on port {PORT}")
    print(f"🌍 Host: 0.0.0.0")
    print(f"📊 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"💾 Database: In-memory (add PostgreSQL for production)")
    
    try:
        uvicorn.run(
            "production_server_railway:app",
            host="0.0.0.0",
            port=PORT,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        raise
