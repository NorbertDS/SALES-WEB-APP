"""
Ultra-simple Railway server for immediate deployment
"""

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Create FastAPI app
app = FastAPI(title="Sales Analytics API")

# Add CORS middleware with explicit configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "https://localhost:3000",
        "*"  # Allow all origins for development
    ],
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

@app.get("/")
async def root():
    return {
        "message": "Sales Analytics API - Railway Deployment",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return JSONResponse(
        content={
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z"
        },
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        }
    )

@app.get("/api/test")
async def test():
    return {"message": "API is working!"}

# Add basic endpoints that the frontend expects
@app.get("/api/analytics/kpis")
async def get_kpis():
    return {
        "total_revenue": 50000,
        "total_sales": 150,
        "total_cogs": 30000,
        "gross_profit": 20000,
        "operating_expenses": 5000,
        "net_profit": 15000,
        "gross_profit_margin": 40.0,
        "net_profit_margin": 30.0
    }

@app.get("/api/sales")
async def get_sales():
    return [
        {
            "id": 1,
            "product_name": "Sample Product",
            "quantity": 10,
            "unit_price": 100.0,
            "total_amount": 1000.0,
            "sale_date": "2024-01-01",
            "customer_name": "Sample Customer",
            "region": "North",
            "salesperson": "John Doe"
        }
    ]

@app.get("/api/products")
async def get_products():
    return [
        {
            "id": 1,
            "name": "Sample Product",
            "category": "Electronics",
            "unit_price": 100.0,
            "cost_price": 60.0,
            "stock_quantity": 50,
            "description": "Sample product description"
        }
    ]

@app.post("/api/auth/login")
async def login():
    return {
        "access_token": "demo_token_123",
        "token_type": "bearer",
        "user": {
            "id": 1,
            "email": "admin@example.com",
            "name": "Admin User",
            "role": "admin"
        }
    }

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting simple server on port {PORT}")
    
    uvicorn.run(
        "simple_server:app",
        host="0.0.0.0",
        port=PORT,
        reload=False
    )
