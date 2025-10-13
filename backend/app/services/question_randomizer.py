"""
Question randomization service to simulate Microsoft's official practice test behavior.
Provides question pool management, randomization, and session-based question selection.
"""

import random
import logging
from typing import List, Optional, Set
from datetime import datetime, timedelta

from app.models.schemas import Question, Answer, PracticeAssessment

logger = logging.getLogger(__name__)


class QuestionRandomizer:
    """
    Manages question randomization to match Microsoft's official practice test behavior.
    Features:
    - Question pool rotation (different questions on retakes)
    - Answer option shuffling
    - Session-based question tracking
    - Configurable question set size
    """
    
    def __init__(self):
        """Initialize the question randomizer."""
        self.session_questions: dict[str, Set[str]] = {}  # Track used questions per session
        self.session_timestamps: dict[str, datetime] = {}  # Track session creation times
        
    def randomize_assessment_for_session(
        self, 
        assessment: PracticeAssessment, 
        session_id: str,
        questions_per_session: int = 50,
        shuffle_answers: bool = True
    ) -> PracticeAssessment:
        """
        Create a randomized version of an assessment for a specific session.
        
        Args:
            assessment: Original assessment with full question pool
            session_id: Unique session identifier
            questions_per_session: Number of questions to select for this session
            shuffle_answers: Whether to randomize answer order
            
        Returns:
            Randomized assessment with selected questions
        """
        try:
            # Clean up old sessions (older than 24 hours)
            self._cleanup_old_sessions()
            
            # Get available questions (avoid recently used ones for this session type)
            available_questions = self._get_available_questions(
                assessment.questions, 
                assessment.certification_code,
                session_id
            )
            
            # Select random questions for this session
            selected_questions = self._select_random_questions(
                available_questions, 
                questions_per_session
            )
            
            # Shuffle answer options if requested
            if shuffle_answers:
                selected_questions = self._shuffle_answer_options(selected_questions)
            
            # Track questions used in this session
            if session_id not in self.session_questions:
                self.session_questions[session_id] = set()
                self.session_timestamps[session_id] = datetime.utcnow()
            
            for question in selected_questions:
                self.session_questions[session_id].add(question.id)
            
            # Create randomized assessment
            randomized_assessment = PracticeAssessment(
                id=f"{assessment.id}_session_{session_id}",
                certification_code=assessment.certification_code,
                title=assessment.title,
                description=f"Randomized practice session - {assessment.description}",
                questions=selected_questions,
                total_questions=len(selected_questions),
                estimated_duration_minutes=assessment.estimated_duration_minutes,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            logger.info(f"Created randomized assessment for session {session_id} with {len(selected_questions)} questions")
            return randomized_assessment
            
        except Exception as e:
            logger.error(f"Error randomizing assessment for session {session_id}: {e}")
            return assessment  # Return original as fallback
    
    def _get_available_questions(
        self, 
        all_questions: List[Question], 
        certification_code: str,
        session_id: str
    ) -> List[Question]:
        """Get questions available for selection (excluding recently used ones)."""
        
        # If this is a new session or we have enough unused questions, return all
        used_questions = self.session_questions.get(session_id, set())
        
        # If less than 20% of questions have been used, return all questions
        usage_percentage = len(used_questions) / len(all_questions) if all_questions else 0
        
        if usage_percentage < 0.2:
            return all_questions
        
        # Filter out recently used questions to provide variety
        available_questions = [
            q for q in all_questions 
            if q.id not in used_questions
        ]
        
        # If we don't have enough unused questions, reset and use all
        if len(available_questions) < 30:  # Minimum threshold
            logger.info(f"Resetting question pool for certification {certification_code}")
            if session_id in self.session_questions:
                self.session_questions[session_id].clear()
            available_questions = all_questions
        
        return available_questions
    
    def _select_random_questions(
        self, 
        available_questions: List[Question], 
        count: int
    ) -> List[Question]:
        """Randomly select questions from available pool."""
        
        if len(available_questions) <= count:
            return available_questions.copy()
        
        # Use weighted selection to prefer different difficulty levels
        selected = []
        remaining_questions = available_questions.copy()
        
        # Try to maintain difficulty distribution
        difficulty_targets = {
            "easy": int(count * 0.3),      # 30% easy
            "medium": int(count * 0.5),    # 50% medium  
            "hard": int(count * 0.2)       # 20% hard
        }
        
        # Select questions by difficulty
        for difficulty, target_count in difficulty_targets.items():
            difficulty_questions = [
                q for q in remaining_questions 
                if q.difficulty_level.value.lower() == difficulty
            ]
            
            if difficulty_questions:
                selection_count = min(target_count, len(difficulty_questions))
                selected_difficulty = random.sample(difficulty_questions, selection_count)
                selected.extend(selected_difficulty)
                
                # Remove selected questions from remaining pool
                remaining_questions = [
                    q for q in remaining_questions 
                    if q not in selected_difficulty
                ]
        
        # Fill remaining slots with random questions
        remaining_needed = count - len(selected)
        if remaining_needed > 0 and remaining_questions:
            additional = random.sample(
                remaining_questions, 
                min(remaining_needed, len(remaining_questions))
            )
            selected.extend(additional)
        
        # Shuffle the final order
        random.shuffle(selected)
        
        return selected
    
    def _shuffle_answer_options(self, questions: List[Question]) -> List[Question]:
        """Shuffle answer options for each question."""
        
        shuffled_questions = []
        
        for question in questions:
            # Create a copy of the question
            shuffled_answers = question.answers.copy()
            random.shuffle(shuffled_answers)
            
            # Create new question with shuffled answers
            shuffled_question = Question(
                id=question.id,
                text=question.text,
                answers=shuffled_answers,
                correct_answer_ids=question.correct_answer_ids,
                question_type=question.question_type,
                difficulty_level=question.difficulty_level,
                explanation=question.explanation,
                category=question.category,
                tags=question.tags
            )
            
            shuffled_questions.append(shuffled_question)
        
        return shuffled_questions
    
    def _cleanup_old_sessions(self):
        """Remove session data older than 24 hours to prevent memory leaks."""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        sessions_to_remove = [
            session_id for session_id, timestamp in self.session_timestamps.items()
            if timestamp < cutoff_time
        ]
        
        for session_id in sessions_to_remove:
            self.session_questions.pop(session_id, None)
            self.session_timestamps.pop(session_id, None)
        
        if sessions_to_remove:
            logger.info(f"Cleaned up {len(sessions_to_remove)} old sessions")
    
    def get_session_stats(self, session_id: str) -> dict:
        """Get statistics about question usage for a session."""
        
        used_questions = len(self.session_questions.get(session_id, set()))
        session_time = self.session_timestamps.get(session_id)
        
        return {
            "session_id": session_id,
            "questions_used": used_questions,
            "session_created": session_time.isoformat() if session_time else None,
            "total_sessions_tracked": len(self.session_questions)
        }


# Global instance
question_randomizer = QuestionRandomizer()