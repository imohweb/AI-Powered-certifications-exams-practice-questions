"""
API router for practice assessments management.
Handles assessment listing, retrieval, and scraping operations.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse

from app.models.schemas import (
    PracticeAssessment, CertificationInfo, ApiResponse, ScrapingStatus
)
from app.services.ai_question_generator import ai_question_generator
from app.core.config import CERTIFICATION_EXAMS

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage for assessments (in production, use a database)
assessment_cache: dict[str, PracticeAssessment] = {}
scraping_status: dict[str, ScrapingStatus] = {}


@router.get("/certifications", response_model=List[CertificationInfo])
async def get_available_certifications():
    """Get list of available Microsoft certifications."""
    try:
        certifications = []
        for code, title in CERTIFICATION_EXAMS.items():
            certifications.append(CertificationInfo(
                code=code,
                title=title,
                category=_get_certification_category(code),
                level=_get_certification_level(code),
                url=f"https://learn.microsoft.com/en-us/credentials/certifications/exams/{code.lower()}/"
            ))
        
        return certifications
    except Exception as e:
        logger.error(f"Error getting certifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve certifications")


@router.get("/{certification_code}", response_model=PracticeAssessment)
async def get_practice_assessment(certification_code: str):
    """
    Get practice assessment for a specific certification.
    Returns cached version if available, otherwise scrapes from Microsoft Learn.
    """
    try:
        certification_code = certification_code.upper()
        
        # Check if certification exists
        if certification_code not in CERTIFICATION_EXAMS:
            raise HTTPException(
                status_code=404, 
                detail=f"Certification {certification_code} not found"
            )
        
        # Check cache first
        if certification_code in assessment_cache:
            logger.info(f"Returning cached assessment for {certification_code}")
            return assessment_cache[certification_code]
        
        # Generate assessment using AI (no web scraping)
        assessment = await ai_question_generator.generate_practice_assessment(certification_code)
        
        if not assessment:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to generate practice assessment for {certification_code}"
            )
        
        # Cache the assessment
        assessment_cache[certification_code] = assessment
        
        return assessment
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting practice assessment for {certification_code}: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve practice assessment for {certification_code}"
        )


@router.post("/{certification_code}/generate")
async def generate_practice_assessment(
    certification_code: str, 
    background_tasks: BackgroundTasks
):
    """
    Trigger background generation of a practice assessment using AI.
    Returns immediately with a task ID for status checking.
    """
    try:
        certification_code = certification_code.upper()
        
        # Check if certification exists
        if certification_code not in CERTIFICATION_EXAMS:
            raise HTTPException(
                status_code=404, 
                detail=f"Certification {certification_code} not found"
            )
        
        # Check if already generating
        if certification_code in scraping_status:
            current_status = scraping_status[certification_code]
            if current_status.status == "in_progress":
                return JSONResponse(
                    content={
                        "message": f"Question generation already in progress for {certification_code}",
                        "status": current_status.dict()
                    }
                )
        
        # Initialize generation status
        scraping_status[certification_code] = ScrapingStatus(
            status="in_progress",
            progress_percentage=0.0,
            questions_scraped=0,
            errors=[]
        )
        
        # Start background question generation with AI
        background_tasks.add_task(
            _background_generate_assessment, 
            certification_code
        )
        
        return JSONResponse(
            content={
                "message": f"Started generating practice assessment for {certification_code}",
                "certification_code": certification_code,
                "status_url": f"/api/v1/assessments/{certification_code}/generate/status"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting scrape for {certification_code}: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to start scraping for {certification_code}"
        )


@router.get("/{certification_code}/generate/status", response_model=ScrapingStatus)
async def get_generation_status(certification_code: str):
    """Get the status of a question generation operation."""
    try:
        certification_code = certification_code.upper()
        
        if certification_code not in scraping_status:
            raise HTTPException(
                status_code=404, 
                detail=f"No generation operation found for {certification_code}"
            )
        
        return scraping_status[certification_code]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting generation status for {certification_code}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to retrieve generation status"
        )


@router.delete("/{certification_code}/cache")
async def clear_assessment_cache(certification_code: str):
    """Clear cached assessment data for a specific certification."""
    try:
        certification_code = certification_code.upper()
        
        if certification_code in assessment_cache:
            del assessment_cache[certification_code]
            logger.info(f"Cleared cache for {certification_code}")
            
        if certification_code in scraping_status:
            del scraping_status[certification_code]
            
        return JSONResponse(
            content={
                "message": f"Cache cleared for {certification_code}",
                "certification_code": certification_code
            }
        )
        
    except Exception as e:
        logger.error(f"Error clearing cache for {certification_code}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to clear cache"
        )


@router.get("/{certification_code}/sample", response_model=PracticeAssessment)
async def get_sample_assessment(certification_code: str):
    """Get a sample practice assessment for testing purposes."""
    try:
        certification_code = certification_code.upper()
        
        # Check if certification exists
        if certification_code not in CERTIFICATION_EXAMS:
            raise HTTPException(
                status_code=404, 
                detail=f"Certification {certification_code} not found"
            )
        
        assessment = await ai_question_generator.generate_practice_assessment(certification_code)
        
        if not assessment:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to generate sample assessment for {certification_code}"
            )
            
        return assessment
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sample assessment for {certification_code}: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate sample assessment for {certification_code}"
        )


async def _background_generate_assessment(certification_code: str):
    """Background task to generate practice assessment using AI."""
    try:
        logger.info(f"Starting background AI generation for {certification_code}")
        
        # Update status
        scraping_status[certification_code].progress_percentage = 10.0
        
        # Generate assessment using AI
        scraping_status[certification_code].progress_percentage = 50.0
        assessment = await ai_question_generator.generate_practice_assessment(certification_code)
        
        if assessment:
            # Success
            scraping_status[certification_code].status = "completed"
            scraping_status[certification_code].progress_percentage = 100.0
            scraping_status[certification_code].questions_scraped = len(assessment.questions)
            
            # Cache the assessment
            assessment_cache[certification_code] = assessment
            
            logger.info(f"Successfully generated {len(assessment.questions)} questions for {certification_code}")
        else:
            # Failed
            scraping_status[certification_code].status = "failed"
            scraping_status[certification_code].errors.append("AI question generation failed")
            logger.error(f"Failed to generate questions for {certification_code}")
                
    except Exception as e:
        logger.error(f"Error in background generation for {certification_code}: {e}")
        
        # Update status with error
        if certification_code in scraping_status:
            scraping_status[certification_code].status = "failed"
            scraping_status[certification_code].errors.append(str(e))


def _get_certification_category(code: str) -> str:
    """Determine certification category from exam code."""
    if code.startswith('AZ-'):
        return "Azure"
    elif code.startswith('AI-'):
        return "Azure AI"
    elif code.startswith('DP-'):
        return "Data Platform"
    elif code.startswith('SC-'):
        return "Security"
    elif code.startswith('MS-'):
        return "Microsoft 365"
    elif code.startswith('MD-'):
        return "Modern Desktop"
    elif code.startswith('PL-'):
        return "Power Platform"
    elif code.startswith('MB-'):
        return "Dynamics 365"
    elif code.startswith('GH-'):
        return "GitHub"
    else:
        return "Other"


def _get_certification_level(code: str) -> str:
    """Determine certification level from exam code."""
    fundamentals_codes = ['AZ-900', 'AI-900', 'DP-900', 'PL-900', 'SC-900', 'MS-900', 'MB-910', 'MB-920', 'GH-900']
    
    if code in fundamentals_codes:
        return "Fundamentals"
    elif any(code.endswith(suffix) for suffix in ['00', '01', '02', '03', '04', '05']):
        return "Associate"
    elif any(code.endswith(suffix) for suffix in ['05', '06', '07', '08', '09']):
        return "Expert"
    else:
        return "Specialty"