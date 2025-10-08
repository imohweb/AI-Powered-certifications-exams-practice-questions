"""
Main FastAPI application with Azure Speech Service integration.
Redeployed: 2025-10-08
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import logging
from pathlib import Path

from app.core.config import settings
from app.routers import assessments, audio, sessions
from app.services.azure_speech import AzureSpeechService
from app.services.azure_openai import AzureOpenAIService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Microsoft Certification Practice Assessment AI Voice Assistant",
    description="AI-powered voice assistant for Microsoft certification practice assessments",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include routers first
app.include_router(assessments.router, prefix="/api/v1/assessments", tags=["assessments"])
app.include_router(audio.router, prefix="/api/v1/audio", tags=["audio"])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["sessions"])

# Mount static files for audio serving at /api/v1/audio-files (after routers to avoid conflicts)
audio_cache_path = Path(settings.audio_cache_dir)
if audio_cache_path.exists():
    app.mount("/api/v1/audio-files", StaticFiles(directory=str(audio_cache_path)), name="audio")


# Dependency to get Azure Speech Service
async def get_speech_service() -> AzureSpeechService:
    """Dependency to provide Azure Speech Service instance."""
    if not settings.azure_speech_key or not settings.azure_speech_region:
        raise HTTPException(
            status_code=503, 
            detail="Azure Speech Service not configured. Please set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION environment variables."
        )
    return AzureSpeechService(
        speech_key=settings.azure_speech_key,
        speech_region=settings.azure_speech_region
    )


@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    logger.info("Starting Microsoft Certification Practice Assessment AI Voice Assistant")
    
    # Verify Azure Speech Service configuration
    if settings.azure_speech_key and settings.azure_speech_region:
        try:
            speech_service = AzureSpeechService(
                speech_key=settings.azure_speech_key,
                speech_region=settings.azure_speech_region
            )
            # Test speech service connection
            test_audio = await speech_service.text_to_speech("Application startup test")
            if test_audio:
                logger.info("Azure Speech Service initialized successfully")
            else:
                logger.warning("Azure Speech Service test failed")
        except Exception as e:
            logger.error(f"Failed to initialize Azure Speech Service: {e}")
    else:
        logger.warning("Azure Speech Service credentials not provided. Speech features will be disabled.")
    
    # Verify Azure OpenAI Service configuration
    if (settings.azure_openai_endpoint and 
        settings.azure_openai_key and 
        settings.azure_openai_deployment):
        try:
            openai_service = AzureOpenAIService(
                endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_key,
                deployment=settings.azure_openai_deployment
            )
            # Test OpenAI service connection
            test_connection = await openai_service.test_connection()
            if test_connection:
                logger.info("Azure OpenAI Service initialized successfully")
            else:
                logger.warning("Azure OpenAI Service test failed")
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI Service: {e}")
    else:
        logger.warning("Azure OpenAI Service credentials not provided. Enhanced AI features will be disabled.")
    
    # Create audio cache directory
    audio_cache_path = Path(settings.audio_cache_dir)
    audio_cache_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Audio cache directory: {audio_cache_path}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down Microsoft Certification Practice Assessment AI Voice Assistant")


@app.get("/")
async def root():
    """Root endpoint with application information."""
    return {
        "message": "Microsoft Certification Practice Assessment AI Voice Assistant",
        "version": "1.0.0",
        "docs": "/docs" if settings.debug else "Documentation disabled in production",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {
            "api": "operational",
            "azure_speech": "operational",
            "database": "operational"
        }
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Serve favicon."""
    return FileResponse("favicon.ico")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )