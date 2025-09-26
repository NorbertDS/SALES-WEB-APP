#!/usr/bin/env python3
"""
Railway Complete Server - Serves both frontend and backend
"""
import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json

# Create main app
app = FastAPI(title="Sales Analytics Complete Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add explicit OPTIONS handler for preflight requests
@app.options("/{path:path}")
async def options_handler(path: str, request: Request):
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true"
        }
    )

# Serve static files (frontend)
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def serve_frontend():
    """Serve the main dashboard"""
    return FileResponse("enhanced_dashboard.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"message": "Sales Analytics Complete Server - Railway Deployment", "status": "running", "version": "2.0.0"}

# API Endpoints - Direct implementation
@app.get("/api/test")
async def test():
    return {"message": "API is working", "status": "success"}

@app.get("/api/analytics/kpis")
async def get_kpis():
    """Get KPI data"""
    return {
        "total_revenue": 50000,
        "total_sales": 150,
        "total_cogs": 30000,
        "gross_profit": 20000,
        "operating_expenses": 5000,
        "net_profit": 15000,
        "profit_margin": 30.0,
        "average_order_value": 333.33
    }

@app.get("/api/sales")
async def get_sales():
    """Get sales data"""
    return [
        {
            "id": 1,
            "product_id": 1,
            "quantity": 2,
            "total_amount": 100.0,
            "date": "2024-01-15"
        },
        {
            "id": 2,
            "product_id": 2,
            "quantity": 1,
            "total_amount": 75.0,
            "date": "2024-01-16"
        }
    ]

@app.get("/api/products")
async def get_products():
    """Get products data"""
    return [
        {
            "id": 1,
            "name": "Product A",
            "unit_price": 50.0,
            "cost_price": 30.0,
            "stock": 100
        },
        {
            "id": 2,
            "name": "Product B",
            "unit_price": 75.0,
            "cost_price": 45.0,
            "stock": 50
        }
    ]

@app.post("/api/auth/login")
async def login(request: Request):
    """Login endpoint"""
    try:
        body = await request.json()
        email = body.get("email", "")
        password = body.get("password", "")
        
        # Simple authentication logic
        if email and password:
            return {
                "access_token": "demo_token_123",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "email": email,
                    "name": "Admin User",
                    "role": "admin"
                }
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/users/")
async def get_users():
    """Get users"""
    return [
        {
            "id": 1,
            "email": "admin@example.com",
            "name": "Admin User",
            "role": "admin",
            "is_active": True
        }
    ]

@app.post("/api/users/")
async def create_user(request: Request):
    """Create user"""
    try:
        body = await request.json()
        return {
            "id": 2,
            "email": body.get("email", ""),
            "name": body.get("name", ""),
            "role": body.get("role", "viewer"),
            "is_active": True
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/users/{user_id}")
async def update_user(user_id: int, request: Request):
    """Update user"""
    try:
        body = await request.json()
        return {
            "id": user_id,
            "email": body.get("email", ""),
            "name": body.get("name", ""),
            "role": body.get("role", "viewer"),
            "is_active": body.get("is_active", True)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int):
    """Delete user"""
    return {"message": f"User {user_id} deleted successfully"}

@app.post("/api/sales")
async def create_sale(request: Request):
    """Create sale"""
    try:
        body = await request.json()
        return {
            "id": 3,
            "product_id": body.get("product_id", 1),
            "quantity": body.get("quantity", 1),
            "total_amount": body.get("total_amount", 0),
            "date": "2024-01-17"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/products")
async def create_product(request: Request):
    """Create product"""
    try:
        body = await request.json()
        return {
            "id": 3,
            "name": body.get("name", ""),
            "unit_price": body.get("unit_price", 0),
            "cost_price": body.get("cost_price", 0),
            "stock": body.get("stock", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)