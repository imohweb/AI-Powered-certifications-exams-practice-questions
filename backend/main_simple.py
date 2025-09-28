"""
Simplified FastAPI application for testing.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Microsoft Certification Practice Assessment AI Voice Assistant",
    description="AI-powered voice assistant for Microsoft certification practice assessments",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001", 
        "http://127.0.0.1:3001",
        "http://localhost:3000", 
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    logger.info("Starting Microsoft Certification Practice Assessment AI Voice Assistant")

@app.get("/")
async def root():
    """Root endpoint with application information."""
    return {
        "message": "Microsoft Certification Practice Assessment AI Voice Assistant",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "services": {
            "api": "operational"
        }
    }

@app.get("/api/v1/assessments/certifications")
async def get_certifications():
    """Get available certifications - mock data for now."""
    return {
        "certifications": [
            {"code": "AZ-900", "title": "Microsoft Azure Fundamentals", "category": "Azure", "level": "Fundamentals"},
            {"code": "AZ-104", "title": "Microsoft Azure Administrator", "category": "Azure", "level": "Associate"},
            {"code": "AI-900", "title": "Microsoft Azure AI Fundamentals", "category": "Azure AI", "level": "Fundamentals"},
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )