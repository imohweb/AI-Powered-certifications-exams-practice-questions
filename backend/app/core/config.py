"""
Core configuration settings for the FastAPI application.
"""

from typing import List, Optional
from pydantic import validator
from pydantic_settings import BaseSettings
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Azure Speech Service (Optional for development)
    azure_speech_key: Optional[str] = None
    azure_speech_region: Optional[str] = None
    azure_speech_endpoint: Optional[str] = None
    
    # Azure OpenAI (Optional)
    azure_openai_endpoint: Optional[str] = None
    azure_openai_key: Optional[str] = None
    azure_openai_deployment: Optional[str] = None
    azure_openai_api_version: str = "2024-02-15-preview"
    
    # Azure Translator Service (Optional)
    azure_translator_key: Optional[str] = None
    azure_translator_endpoint: Optional[str] = None
    azure_translator_region: Optional[str] = None
    
    # Database
    database_url: str = "sqlite:///./ms_cert_practice.db"
    
    # Redis Cache
    redis_url: Optional[str] = None
    
    # Application
    debug: bool = False
    log_level: str = "INFO"
    secret_key: str = "your-secret-key-change-in-production"
    
    # CORS - Updated for Azure Static Web App deployment
    # Updated: 2025-10-12 - Azure Static Web App URL for frontend
    cors_origins: List[str] = [
        "https://lively-dune-0486f060f.2.azurestaticapps.net",
        "http://localhost:3000",  # For local development
        "http://127.0.0.1:3000",  # Alternative localhost
    ]
    
    # Rate Limiting
    max_requests_per_minute: int = 60
    
    # Audio Settings
    audio_cache_dir: str = "./audio_cache"
    max_audio_cache_size_mb: int = 500
    
    # Speech Settings - Dual Voice Configuration
    # Primary voice for reading questions (multilingual capable)
    speech_voice_name_primary: str = "en-US-JennyMultilingualNeural"
    speech_rate_primary: str = "-10%"  # Slightly slower for better comprehension
    speech_pitch_primary: str = "0%"
    
    # Secondary voice for feedback/results (different voice for variety)
    speech_voice_name_secondary: str = "en-US-AriaNeural"
    speech_rate_secondary: str = "-5%"  # Slightly faster for feedback
    speech_pitch_secondary: str = "+5%"  # Higher pitch for differentiation
    
    # Legacy settings (kept for compatibility)
    speech_voice_name: str = "en-US-JennyMultilingualNeural"
    speech_rate: str = "-10%"
    speech_pitch: str = "0%"
    
    # Supported Languages for Multilingual Reading (as comma-separated string)
    supported_languages_str: str = "en,es,fr,de,it,pt,ja,ko,zh,ar,hi,ru"
    
    @property
    def supported_languages(self) -> List[str]:
        """Parse supported languages from comma-separated string."""
        return [lang.strip() for lang in self.supported_languages_str.split(",")]
    
    @validator('cors_origins', pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @validator('audio_cache_dir')
    def create_audio_cache_dir(cls, v):
        """Ensure audio cache directory exists."""
        cache_path = Path(v)
        cache_path.mkdir(parents=True, exist_ok=True)
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Microsoft Learn URLs and endpoints
MICROSOFT_LEARN_BASE_URL = "https://learn.microsoft.com"
PRACTICE_ASSESSMENTS_BASE_URL = f"{MICROSOFT_LEARN_BASE_URL}/en-us/credentials/certifications/practice-assessments-for-microsoft-certifications"

# Certification exam mappings - Complete list from Microsoft Learn (50 available practice assessments)
CERTIFICATION_EXAMS = {
    # Azure AI
    "AI-102": "Designing and Implementing a Microsoft Azure AI Solution",
    "AI-900": "Microsoft Azure AI Fundamentals",
    
    # Azure Core
    "AZ-104": "Microsoft Azure Administrator",
    "AZ-140": "Configuring and Operating Microsoft Azure Virtual Desktop",
    "AZ-204": "Developing Solutions for Microsoft Azure",
    "AZ-305": "Designing Microsoft Azure Infrastructure Solutions",
    "AZ-400": "Designing and Implementing Microsoft DevOps Solutions",
    "AZ-500": "Microsoft Azure Security Technologies",
    "AZ-700": "Designing and Implementing Microsoft Azure Networking Solutions",
    "AZ-800": "Administering Windows Server Hybrid Core Infrastructure",
    "AZ-801": "Configuring Windows Server Hybrid Advanced Services",
    "AZ-900": "Microsoft Azure Fundamentals",
    
    # Data & Analytics
    "DP-100": "Designing and Implementing a Data Science Solution on Azure",
    "DP-300": "Administering Microsoft Azure SQL Solutions",
    "DP-420": "Azure Cosmos DB Developer Specialty",
    "DP-600": "Implementing Analytics Solutions Using Microsoft Fabric",
    "DP-700": "Microsoft Certified: Fabric Data Engineer Associate",
    "DP-900": "Microsoft Azure Data Fundamentals",
    
    # GitHub
    "GH-100": "GitHub Administration",
    "GH-200": "GitHub Actions",
    "GH-300": "GitHub Copilot",
    "GH-500": "GitHub Advanced Security",
    "GH-900": "GitHub Foundations",
    
    # Dynamics 365
    "MB-230": "Microsoft Dynamics 365 Customer Service Functional Consultant",
    "MB-240": "Microsoft Dynamics 365 Field Service Functional Consultant",
    "MB-280": "Dynamics 365 Customer Experience Analyst Associate",
    "MB-310": "Microsoft Dynamics 365 Finance Functional Consultant",
    "MB-330": "Microsoft Dynamics 365 Supply Chain Management Functional Consultant Associate",
    "MB-335": "Microsoft Dynamics 365 Supply Chain Management Functional Consultant Expert",
    "MB-500": "Dynamics 365: Finance and Operations Apps Developer Associate",
    "MB-800": "Microsoft Dynamics 365 Business Central Functional Consultant Associate",
    "MB-820": "Microsoft Dynamics 365 Business Central Developer Associate",
    "MB-910": "Microsoft Dynamics 365 Fundamentals (CRM)",
    "MB-920": "Microsoft Dynamics 365 Fundamentals (ERP)",
    
    # Microsoft 365
    "MD-102": "Endpoint Administrator",
    "MS-102": "Microsoft 365 Administrator",
    "MS-700": "Managing Microsoft Teams",
    "MS-721": "Collaboration Communications Systems Engineer",
    "MS-900": "Microsoft 365 Fundamentals",
    
    # Power Platform
    "PL-200": "Microsoft Power Platform Functional Consultant",
    "PL-300": "Microsoft Power BI Data Analyst",
    "PL-400": "Microsoft Power Platform Developer",
    "PL-500": "Microsoft Power Automate RPA Developer",
    "PL-600": "Microsoft Power Platform Solution Architect",
    "PL-900": "Microsoft Power Platform Fundamentals",
    
    # Security, Compliance & Identity
    "SC-100": "Microsoft Cybersecurity Architect",
    "SC-200": "Microsoft Security Operations Analyst",
    "SC-300": "Microsoft Identity and Access Administrator",
    "SC-401": "Microsoft Certified: Information Security Administrator Associate",
    "SC-900": "Microsoft Security, Compliance, and Identity Fundamentals"
}