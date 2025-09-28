"""
API router for user session management and progress tracking.
Handles session creation, question progression, answer submission, and analytics.
"""

import logging
import uuid
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.models.schemas import (
    UserSession, UserAnswer, SessionProgress, ApiResponse,
    Question, PracticeAssessment
)
from app.services.ai_agent import QuestionFlowAgent
from app.routers.assessments import assessment_cache

logger = logging.getLogger(__name__)
router = APIRouter()

# Global AI agent instance
ai_agent = QuestionFlowAgent()


@router.post("/start", response_model=UserSession)
async def start_session(
    certification_code: str,
    auto_progression: bool = True
):
    """
    Start a new practice session for a certification.
    
    Args:
        certification_code: Microsoft certification exam code
        auto_progression: Whether to automatically advance questions
        
    Returns:
        UserSession object with session details
    """
    try:
        certification_code = certification_code.upper()
        
        # Check if assessment is available
        if certification_code not in assessment_cache:
            raise HTTPException(
                status_code=404,
                detail=f"Practice assessment for {certification_code} not found. Please load the assessment first."
            )
        
        # Get assessment
        assessment = assessment_cache[certification_code]
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Start session with AI agent
        session = await ai_agent.start_session(
            session_id=session_id,
            assessment=assessment,
            auto_progression=auto_progression
        )
        
        logger.info(f"Started session {session_id} for {certification_code}")
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting session for {certification_code}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start session: {str(e)}"
        )


@router.get("/{session_id}/current-question", response_model=Question)
async def get_current_question(session_id: str):
    """
    Get the current question for a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Current question or 404 if session complete
    """
    try:
        question = await ai_agent.get_current_question(session_id)
        
        if not question:
            # Check if session exists and is complete
            session = ai_agent.sessions.get(session_id)
            if session and session.is_completed:
                raise HTTPException(
                    status_code=200,  # Use 200 but with completion message
                    detail="Assessment completed"
                )
            else:
                raise HTTPException(
                    status_code=404,
                    detail="Session not found or no current question available"
                )
        
        return question
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current question for session {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get current question: {str(e)}"
        )


@router.post("/{session_id}/submit-answer")
async def submit_answer(
    session_id: str,
    question_id: str,
    selected_answer_ids: List[str],
    time_spent_seconds: Optional[int] = None
):
    """
    Submit an answer for the current question.
    
    Args:
        session_id: Session identifier
        question_id: Question identifier
        selected_answer_ids: List of selected answer IDs
        time_spent_seconds: Time spent on the question
        
    Returns:
        Answer result with correctness, explanation, and next action
    """
    try:
        if not selected_answer_ids:
            raise HTTPException(
                status_code=400,
                detail="At least one answer must be selected"
            )
        
        # Submit answer to AI agent
        result = await ai_agent.submit_answer(
            session_id=session_id,
            question_id=question_id,
            selected_answer_ids=selected_answer_ids,
            time_spent_seconds=time_spent_seconds
        )
        
        logger.info(f"Answer submitted for session {session_id}, question {question_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting answer for session {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit answer: {str(e)}"
        )


@router.post("/{session_id}/next-question", response_model=Question)
async def advance_to_next_question(session_id: str):
    """
    Manually advance to the next question in the assessment.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Next question or completion message
    """
    try:
        next_question = await ai_agent.advance_to_next_question(session_id)
        
        if not next_question:
            # Assessment completed
            return JSONResponse(
                content={
                    "message": "Assessment completed!",
                    "completed": True,
                    "session_id": session_id
                }
            )
        
        return next_question
        
    except Exception as e:
        logger.error(f"Error advancing to next question for session {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to advance to next question: {str(e)}"
        )


@router.get("/{session_id}/progress", response_model=SessionProgress)
async def get_session_progress(session_id: str):
    """
    Get progress information for a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        SessionProgress with completion and performance metrics
    """
    try:
        progress = await ai_agent.get_session_progress(session_id)
        
        if not progress:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        return progress
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting progress for session {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session progress: {str(e)}"
        )


@router.get("/{session_id}/summary")
async def get_session_summary(session_id: str):
    """
    Get comprehensive session summary with analytics and recommendations.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Detailed session summary with performance analysis
    """
    try:
        summary = await ai_agent.get_session_summary(session_id)
        
        if "error" in summary:
            raise HTTPException(
                status_code=404,
                detail=summary["error"]
            )
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting summary for session {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session summary: {str(e)}"
        )


@router.get("/{session_id}/answers", response_model=List[UserAnswer])
async def get_session_answers(session_id: str):
    """
    Get all answers submitted in a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        List of UserAnswer objects
    """
    try:
        answers = ai_agent.user_answers.get(session_id, [])
        
        if not answers:
            # Check if session exists
            if session_id not in ai_agent.sessions:
                raise HTTPException(
                    status_code=404,
                    detail="Session not found"
                )
        
        return answers
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting answers for session {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session answers: {str(e)}"
        )


@router.put("/{session_id}/settings")
async def update_session_settings(
    session_id: str,
    auto_progression: Optional[bool] = None
):
    """
    Update session settings.
    
    Args:
        session_id: Session identifier
        auto_progression: Whether to enable auto-progression
        
    Returns:
        Updated session information
    """
    try:
        session = ai_agent.sessions.get(session_id)
        
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        # Update settings
        if auto_progression is not None:
            session.auto_progression_enabled = auto_progression
        
        return {
            "message": "Session settings updated successfully",
            "session_id": session_id,
            "auto_progression": session.auto_progression_enabled
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating settings for session {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update session settings: {str(e)}"
        )


@router.delete("/{session_id}")
async def end_session(session_id: str):
    """
    End a practice session and clean up resources.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Session termination confirmation
    """
    try:
        # Check if session exists
        if session_id not in ai_agent.sessions:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        # Get final summary before cleanup
        final_summary = await ai_agent.get_session_summary(session_id)
        
        # Clean up session data
        if session_id in ai_agent.sessions:
            del ai_agent.sessions[session_id]
        if session_id in ai_agent.user_answers:
            del ai_agent.user_answers[session_id]
        
        logger.info(f"Session {session_id} ended and cleaned up")
        
        return {
            "message": "Session ended successfully",
            "session_id": session_id,
            "final_summary": final_summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending session {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to end session: {str(e)}"
        )


@router.get("/active")
async def get_active_sessions():
    """
    Get list of currently active sessions.
    
    Returns:
        List of active session information
    """
    try:
        active_sessions = []
        
        for session_id, session in ai_agent.sessions.items():
            # Get progress for each session
            progress = await ai_agent.get_session_progress(session_id)
            
            active_sessions.append({
                "session_id": session_id,
                "assessment_id": session.assessment_id,
                "start_time": session.start_time,
                "last_activity": session.last_activity,
                "is_completed": session.is_completed,
                "progress": progress.dict() if progress else None
            })
        
        return {
            "total_sessions": len(active_sessions),
            "sessions": active_sessions
        }
        
    except Exception as e:
        logger.error(f"Error getting active sessions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get active sessions: {str(e)}"
        )