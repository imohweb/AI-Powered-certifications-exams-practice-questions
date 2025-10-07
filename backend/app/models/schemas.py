"""
Pydantic models for the Microsoft Certification Practice Assessment application.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class QuestionType(str, Enum):
    """Enumeration of question types in practice assessments."""
    MULTIPLE_CHOICE = "multiple_choice"
    MULTIPLE_SELECT = "multiple_select"
    TRUE_FALSE = "true_false"
    DRAG_DROP = "drag_drop"
    CASE_STUDY = "case_study"
    HOTSPOT = "hotspot"


class DifficultyLevel(str, Enum):
    """Question difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Answer(BaseModel):
    """Individual answer option for a question."""
    id: str = Field(..., description="Unique identifier for the answer")
    text: str = Field(..., description="Answer text content")
    is_correct: bool = Field(default=False, description="Whether this answer is correct")
    explanation: Optional[str] = Field(None, description="Explanation for this answer choice")


class Question(BaseModel):
    """Practice assessment question model."""
    id: str = Field(..., description="Unique identifier for the question")
    text: str = Field(..., description="Question text content")
    question_type: QuestionType = Field(..., description="Type of question")
    answers: List[Answer] = Field(..., description="Available answer options")
    correct_answer_ids: List[str] = Field(..., description="IDs of correct answers")
    explanation: Optional[str] = Field(None, description="Detailed explanation of the correct answer")
    difficulty: Optional[DifficultyLevel] = Field(None, description="Question difficulty level")
    topics: List[str] = Field(default_factory=list, description="Topics/skills covered by this question")
    reference_links: List[str] = Field(default_factory=list, description="Links to relevant documentation")
    
    @validator('correct_answer_ids')
    def validate_correct_answers(cls, v, values):
        """Ensure correct answer IDs exist in the answers list."""
        if 'answers' in values:
            answer_ids = {answer.id for answer in values['answers']}
            for correct_id in v:
                if correct_id not in answer_ids:
                    raise ValueError(f"Correct answer ID {correct_id} not found in answers")
        return v


class PracticeAssessment(BaseModel):
    """Practice assessment model containing multiple questions."""
    id: str = Field(..., description="Unique identifier for the assessment")
    certification_code: str = Field(..., description="Microsoft certification exam code (e.g., AZ-900)")
    title: str = Field(..., description="Full certification title")
    description: Optional[str] = Field(None, description="Assessment description")
    questions: List[Question] = Field(..., description="List of questions in the assessment")
    total_questions: int = Field(..., description="Total number of questions")
    estimated_duration_minutes: Optional[int] = Field(None, description="Estimated completion time")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('total_questions')
    def validate_total_questions(cls, v, values):
        """Ensure total_questions matches the actual number of questions."""
        if 'questions' in values:
            actual_count = len(values['questions'])
            if v != actual_count:
                raise ValueError(f"total_questions ({v}) doesn't match actual questions count ({actual_count})")
        return v


class UserSession(BaseModel):
    """User practice session tracking."""
    session_id: str = Field(..., description="Unique session identifier")
    assessment_id: str = Field(..., description="Assessment being attempted")
    current_question_index: int = Field(default=0, description="Current question position")
    answered_questions: List[str] = Field(default_factory=list, description="IDs of answered questions")
    score: int = Field(default=0, description="Current score")
    start_time: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    is_completed: bool = Field(default=False, description="Whether session is completed")
    auto_progression_enabled: bool = Field(default=True, description="Auto-advance to next question")


class UserAnswer(BaseModel):
    """User's answer to a specific question."""
    session_id: str = Field(..., description="Session identifier")
    question_id: str = Field(..., description="Question identifier")
    selected_answer_ids: List[str] = Field(..., description="IDs of selected answers")
    is_correct: bool = Field(..., description="Whether the answer is correct")
    time_spent_seconds: Optional[int] = Field(None, description="Time spent on this question")
    answered_at: datetime = Field(default_factory=datetime.utcnow)


class AudioRequest(BaseModel):
    """Request for text-to-speech conversion."""
    text: str = Field(..., description="Text to convert to speech")
    voice_name: Optional[str] = Field(None, description="Azure Speech Service voice name")
    speech_rate: Optional[str] = Field(None, description="Speech rate adjustment")
    speech_pitch: Optional[str] = Field(None, description="Speech pitch adjustment")
    output_format: str = Field(default="audio-16khz-32kbitrate-mono-mp3", description="Audio output format")


class AudioResponse(BaseModel):
    """Response containing audio data."""
    audio_url: str = Field(..., description="URL to access the generated audio")
    duration_seconds: Optional[float] = Field(None, description="Audio duration in seconds")
    cache_key: Optional[str] = Field(None, description="Cache key for the audio file")
    translated_text: Optional[str] = Field(None, description="The translated text that is being spoken (for progressive display)")
    translated_question: Optional[str] = Field(None, description="The translated question text only")
    translated_answers: Optional[list[str]] = Field(None, description="List of translated answer options")


class SessionProgress(BaseModel):
    """Progress information for a user session."""
    session_id: str = Field(..., description="Session identifier")
    total_questions: int = Field(..., description="Total number of questions")
    answered_questions: int = Field(..., description="Number of answered questions")
    correct_answers: int = Field(..., description="Number of correct answers")
    current_question_index: int = Field(..., description="Current question position")
    percentage_complete: float = Field(..., description="Completion percentage")
    score_percentage: float = Field(..., description="Score as percentage")
    estimated_time_remaining_minutes: Optional[int] = Field(None, description="Estimated time to complete")


class ApiResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if success is False")


class CertificationInfo(BaseModel):
    """Information about available certifications."""
    code: str = Field(..., description="Certification exam code")
    title: str = Field(..., description="Full certification title")
    category: Optional[str] = Field(None, description="Certification category")
    level: Optional[str] = Field(None, description="Certification level")
    url: Optional[str] = Field(None, description="URL to the certification page")


class ScrapingStatus(BaseModel):
    """Status of web scraping operation."""
    status: str = Field(..., description="Current status of scraping operation")
    progress_percentage: float = Field(..., description="Progress as percentage")
    questions_scraped: int = Field(..., description="Number of questions successfully scraped")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")
    estimated_completion_time: Optional[datetime] = Field(None, description="Estimated completion time")