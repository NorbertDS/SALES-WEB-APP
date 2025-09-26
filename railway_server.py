#!/usr/bin/env python3
"""
Railway Complete Server - Serves both frontend and backend
"""
import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import json

# Import the backend API
from backend.simple_server import app as api_app

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

# Mount the API routes
app.mount("/api", api_app)

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

@app.get("/config")
async def get_config():
    """Serve configuration"""
    try:
        with open("config.js", "r") as f:
            config_content = f.read()
        return {"config": config_content}
    except:
        return {"config": "// Default config"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)