"""
Ultra-simple Railway server for immediate deployment
"""

import os
from fastapi import FastAPI
import uvicorn

# Create FastAPI app
app = FastAPI(title="Sales Analytics API")

@app.get("/")
async def root():
    return {
        "message": "Sales Analytics API - Railway Deployment",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/api/test")
async def test():
    return {"message": "API is working!"}

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting simple server on port {PORT}")
    
    uvicorn.run(
        "simple_server:app",
        host="0.0.0.0",
        port=PORT,
        reload=False
    )
