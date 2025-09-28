"""
AI Agent for intelligent question management and automatic progression.
Handles session flow, progress tracking, and adaptive learning features.
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from app.models.schemas import (
    UserSession, Question, UserAnswer, SessionProgress, 
    PracticeAssessment, QuestionType
)
from app.core.config import settings
from app.services.azure_openai import AzureOpenAIService

logger = logging.getLogger(__name__)


class QuestionFlowAgent:
    """AI Agent for managing question flow and user progression."""
    
    def __init__(self):
        self.sessions: Dict[str, UserSession] = {}
        self.assessments: Dict[str, PracticeAssessment] = {}
        self.user_answers: Dict[str, List[UserAnswer]] = {}
        
        # Initialize Azure OpenAI if configured
        self.openai_service = None
        if (settings.azure_openai_endpoint and 
            settings.azure_openai_key and 
            settings.azure_openai_deployment):
            try:
                self.openai_service = AzureOpenAIService(
                    endpoint=settings.azure_openai_endpoint,
                    api_key=settings.azure_openai_key,
                    deployment=settings.azure_openai_deployment
                )
                logger.info("Azure OpenAI integration enabled for AI Agent")
            except Exception as e:
                logger.warning(f"Failed to initialize Azure OpenAI: {e}")
                self.openai_service = None
        
    async def start_session(
        self, 
        session_id: str, 
        assessment: PracticeAssessment,
        auto_progression: bool = True
    ) -> UserSession:
        """
        Start a new practice session.
        
        Args:
            session_id: Unique session identifier
            assessment: Practice assessment to work with
            auto_progression: Whether to automatically advance questions
            
        Returns:
            UserSession object
        """
        try:
            # Store assessment
            self.assessments[assessment.id] = assessment
            
            # Create session
            session = UserSession(
                session_id=session_id,
                assessment_id=assessment.id,
                current_question_index=0,
                answered_questions=[],
                score=0,
                auto_progression_enabled=auto_progression
            )
            
            self.sessions[session_id] = session
            self.user_answers[session_id] = []
            
            logger.info(f"Started session {session_id} for assessment {assessment.id}")
            return session
            
        except Exception as e:
            logger.error(f"Error starting session {session_id}: {e}")
            raise
    
    async def get_current_question(self, session_id: str) -> Optional[Question]:
        """
        Get the current question for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Current question or None if session complete
        """
        try:
            session = self.sessions.get(session_id)
            if not session:
                logger.warning(f"Session {session_id} not found")
                return None
            
            assessment = self.assessments.get(session.assessment_id)
            if not assessment:
                logger.warning(f"Assessment {session.assessment_id} not found")
                return None
            
            # Check if session is complete
            if session.current_question_index >= len(assessment.questions):
                session.is_completed = True
                return None
            
            current_question = assessment.questions[session.current_question_index]
            
            # Update last activity
            session.last_activity = datetime.utcnow()
            
            return current_question
            
        except Exception as e:
            logger.error(f"Error getting current question for session {session_id}: {e}")
            return None
    
    async def submit_answer(
        self, 
        session_id: str, 
        question_id: str, 
        selected_answer_ids: List[str],
        time_spent_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Submit an answer and determine next action.
        
        Args:
            session_id: Session identifier
            question_id: Question identifier
            selected_answer_ids: List of selected answer IDs
            time_spent_seconds: Time spent on question
            
        Returns:
            Result with correctness, explanation, and next action
        """
        try:
            session = self.sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            assessment = self.assessments.get(session.assessment_id)
            if not assessment:
                raise ValueError(f"Assessment {session.assessment_id} not found")
            
            # Find the question
            question = next((q for q in assessment.questions if q.id == question_id), None)
            if not question:
                raise ValueError(f"Question {question_id} not found")
            
            # Check correctness
            is_correct = self._check_answer_correctness(question, selected_answer_ids)
            
            # Get enhanced explanation if Azure OpenAI is available
            explanation = question.explanation
            if self.openai_service and not is_correct:
                try:
                    enhanced_explanation = await self.openai_service.enhance_question_explanation(question)
                    explanation = enhanced_explanation
                except Exception as e:
                    logger.warning(f"Failed to get enhanced explanation: {e}")
                    explanation = question.explanation or "No explanation available."
            
            # Create user answer record
            user_answer = UserAnswer(
                session_id=session_id,
                question_id=question_id,
                selected_answer_ids=selected_answer_ids,
                is_correct=is_correct,
                time_spent_seconds=time_spent_seconds
            )
            
            # Store answer
            self.user_answers[session_id].append(user_answer)
            
            # Update session
            if question_id not in session.answered_questions:
                session.answered_questions.append(question_id)
                if is_correct:
                    session.score += 1
            
            # Determine next action
            next_action = await self._determine_next_action(session, question, is_correct)
            
            # Prepare response
            result = {
                "is_correct": is_correct,
                "correct_answer_ids": question.correct_answer_ids,
                "explanation": explanation,
                "reference_links": question.reference_links,
                "next_action": next_action,
                "progress": await self.get_session_progress(session_id)
            }
            
            logger.info(f"Answer submitted for session {session_id}, question {question_id}: {'correct' if is_correct else 'incorrect'}")
            return result
            
        except Exception as e:
            logger.error(f"Error submitting answer for session {session_id}: {e}")
            raise
    
    async def advance_to_next_question(self, session_id: str) -> Optional[Question]:
        """
        Advance to the next question in the assessment.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Next question or None if assessment complete
        """
        try:
            session = self.sessions.get(session_id)
            if not session:
                logger.warning(f"Session {session_id} not found")
                return None
            
            assessment = self.assessments.get(session.assessment_id)
            if not assessment:
                logger.warning(f"Assessment {session.assessment_id} not found")
                return None
            
            # Move to next question
            session.current_question_index += 1
            session.last_activity = datetime.utcnow()
            
            # Check if assessment is complete
            if session.current_question_index >= len(assessment.questions):
                session.is_completed = True
                logger.info(f"Session {session_id} completed")
                return None
            
            # Get next question
            next_question = assessment.questions[session.current_question_index]
            logger.info(f"Advanced to question {session.current_question_index + 1} for session {session_id}")
            
            return next_question
            
        except Exception as e:
            logger.error(f"Error advancing to next question for session {session_id}: {e}")
            return None
    
    async def get_session_progress(self, session_id: str) -> Optional[SessionProgress]:
        """
        Get progress information for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionProgress object
        """
        try:
            session = self.sessions.get(session_id)
            if not session:
                return None
            
            assessment = self.assessments.get(session.assessment_id)
            if not assessment:
                return None
            
            # Calculate progress metrics
            total_questions = len(assessment.questions)
            answered_questions = len(session.answered_questions)
            correct_answers = session.score
            
            percentage_complete = (answered_questions / total_questions) * 100
            score_percentage = (correct_answers / answered_questions) * 100 if answered_questions > 0 else 0
            
            # Estimate remaining time
            avg_time_per_question = 120  # 2 minutes default
            if answered_questions > 0:
                total_time_spent = sum(
                    answer.time_spent_seconds or 120 
                    for answer in self.user_answers.get(session_id, [])
                )
                avg_time_per_question = total_time_spent / answered_questions
            
            remaining_questions = total_questions - answered_questions
            estimated_time_remaining = int((remaining_questions * avg_time_per_question) / 60)  # minutes
            
            return SessionProgress(
                session_id=session_id,
                total_questions=total_questions,
                answered_questions=answered_questions,
                correct_answers=correct_answers,
                current_question_index=session.current_question_index,
                percentage_complete=percentage_complete,
                score_percentage=score_percentage,
                estimated_time_remaining_minutes=estimated_time_remaining
            )
            
        except Exception as e:
            logger.error(f"Error getting session progress for {session_id}: {e}")
            return None
    
    async def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get comprehensive session summary and recommendations.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session summary with statistics and recommendations
        """
        try:
            session = self.sessions.get(session_id)
            if not session:
                return {"error": "Session not found"}
            
            assessment = self.assessments.get(session.assessment_id)
            if not assessment:
                return {"error": "Assessment not found"}
            
            progress = await self.get_session_progress(session_id)
            user_answers = self.user_answers.get(session_id, [])
            
            # Calculate detailed statistics
            total_time_spent = sum(answer.time_spent_seconds or 0 for answer in user_answers)
            
            # Topic performance analysis
            topic_performance = await self._analyze_topic_performance(session_id, assessment)
            
            # Difficulty analysis
            difficulty_performance = await self._analyze_difficulty_performance(session_id, assessment)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                session, assessment, topic_performance, difficulty_performance
            )
            
            # Generate AI-powered study tips if OpenAI is available
            ai_study_tips = None
            if self.openai_service and len(user_answers) > 3:  # Only if enough data
                try:
                    ai_study_tips = await self.openai_service.generate_study_tips(assessment.questions)
                except Exception as e:
                    logger.warning(f"Failed to generate AI study tips: {e}")
            
            summary = {
                "session_id": session_id,
                "assessment_title": assessment.title,
                "completion_status": "completed" if session.is_completed else "in_progress",
                "total_time_spent_minutes": total_time_spent / 60 if total_time_spent > 0 else 0,
                "progress": progress.dict() if progress else None,
                "topic_performance": topic_performance,
                "difficulty_performance": difficulty_performance,
                "recommendations": recommendations,
                "ai_study_tips": ai_study_tips,
                "detailed_answers": [answer.dict() for answer in user_answers]
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting session summary for {session_id}: {e}")
            return {"error": str(e)}
    
    def _check_answer_correctness(self, question: Question, selected_answer_ids: List[str]) -> bool:
        """Check if the selected answers are correct."""
        # Sort both lists for comparison
        selected_sorted = sorted(selected_answer_ids)
        correct_sorted = sorted(question.correct_answer_ids)
        
        return selected_sorted == correct_sorted
    
    async def _determine_next_action(
        self, 
        session: UserSession, 
        question: Question, 
        is_correct: bool
    ) -> Dict[str, Any]:
        """
        Determine the next action based on session settings and answer correctness.
        
        Args:
            session: Current session
            question: Question that was answered
            is_correct: Whether the answer was correct
            
        Returns:
            Next action information
        """
        try:
            assessment = self.assessments.get(session.assessment_id)
            if not assessment:
                return {"action": "error", "message": "Assessment not found"}
            
            # Check if this was the last question
            is_last_question = session.current_question_index >= len(assessment.questions) - 1
            
            if is_last_question:
                return {
                    "action": "complete_assessment",
                    "message": "Assessment completed!",
                    "auto_advance": False
                }
            
            # Determine advancement timing
            if session.auto_progression_enabled:
                # Calculate delay based on question type and correctness
                delay_seconds = self._calculate_auto_advance_delay(question, is_correct)
                
                return {
                    "action": "auto_advance",
                    "delay_seconds": delay_seconds,
                    "message": f"Automatically advancing to next question in {delay_seconds} seconds..."
                }
            else:
                return {
                    "action": "manual_advance",
                    "message": "Click 'Next Question' to continue."
                }
            
        except Exception as e:
            logger.error(f"Error determining next action: {e}")
            return {"action": "error", "message": str(e)}
    
    def _calculate_auto_advance_delay(self, question: Question, is_correct: bool) -> int:
        """
        Calculate delay before automatically advancing to next question.
        
        Args:
            question: Current question
            is_correct: Whether answer was correct
            
        Returns:
            Delay in seconds
        """
        base_delay = 3  # Base delay in seconds
        
        # Add time for explanation reading
        if question.explanation:
            explanation_length = len(question.explanation)
            # Assume 200 words per minute reading speed
            reading_time = max(3, explanation_length / (200 * 5))  # Rough approximation
            base_delay += int(reading_time)
        
        # Adjust based on correctness
        if not is_correct:
            base_delay += 2  # Extra time to review incorrect answers
        
        # Adjust based on question type
        if question.question_type in [QuestionType.CASE_STUDY, QuestionType.DRAG_DROP]:
            base_delay += 3  # More complex questions need more time
        
        return min(base_delay, 15)  # Cap at 15 seconds
    
    async def _analyze_topic_performance(
        self, 
        session_id: str, 
        assessment: PracticeAssessment
    ) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by topic."""
        try:
            user_answers = self.user_answers.get(session_id, [])
            topic_stats = {}
            
            for answer in user_answers:
                # Find the question
                question = next((q for q in assessment.questions if q.id == answer.question_id), None)
                if not question:
                    continue
                
                # Process each topic
                for topic in question.topics:
                    if topic not in topic_stats:
                        topic_stats[topic] = {"total": 0, "correct": 0}
                    
                    topic_stats[topic]["total"] += 1
                    if answer.is_correct:
                        topic_stats[topic]["correct"] += 1
            
            # Calculate percentages
            for topic, stats in topic_stats.items():
                stats["percentage"] = (stats["correct"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            
            return topic_stats
            
        except Exception as e:
            logger.error(f"Error analyzing topic performance: {e}")
            return {}
    
    async def _analyze_difficulty_performance(
        self, 
        session_id: str, 
        assessment: PracticeAssessment
    ) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by difficulty level."""
        try:
            user_answers = self.user_answers.get(session_id, [])
            difficulty_stats = {}
            
            for answer in user_answers:
                # Find the question
                question = next((q for q in assessment.questions if q.id == answer.question_id), None)
                if not question or not question.difficulty:
                    continue
                
                difficulty = question.difficulty.value
                if difficulty not in difficulty_stats:
                    difficulty_stats[difficulty] = {"total": 0, "correct": 0}
                
                difficulty_stats[difficulty]["total"] += 1
                if answer.is_correct:
                    difficulty_stats[difficulty]["correct"] += 1
            
            # Calculate percentages
            for difficulty, stats in difficulty_stats.items():
                stats["percentage"] = (stats["correct"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            
            return difficulty_stats
            
        except Exception as e:
            logger.error(f"Error analyzing difficulty performance: {e}")
            return {}
    
    async def _generate_recommendations(
        self,
        session: UserSession,
        assessment: PracticeAssessment,
        topic_performance: Dict[str, Dict[str, Any]],
        difficulty_performance: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Generate personalized recommendations based on performance."""
        recommendations = []
        
        try:
            # Overall score recommendations
            if session.score > 0 and len(session.answered_questions) > 0:
                score_percentage = (session.score / len(session.answered_questions)) * 100
                
                if score_percentage >= 80:
                    recommendations.append("Excellent work! You're well-prepared for this certification exam.")
                elif score_percentage >= 60:
                    recommendations.append("Good progress! Review the topics where you had incorrect answers.")
                else:
                    recommendations.append("Consider additional study before taking the actual exam.")
            
            # Topic-specific recommendations
            weak_topics = [
                topic for topic, stats in topic_performance.items()
                if stats["percentage"] < 60 and stats["total"] >= 2
            ]
            
            if weak_topics:
                recommendations.append(f"Focus on these topics: {', '.join(weak_topics[:3])}")
            
            # Difficulty-specific recommendations
            if "advanced" in difficulty_performance:
                advanced_perf = difficulty_performance["advanced"]["percentage"]
                if advanced_perf < 50:
                    recommendations.append("Practice more advanced-level questions to improve your expertise.")
            
            # Study resource recommendations
            recommendations.append("Review the reference links provided with incorrect answers.")
            recommendations.append("Take the practice assessment multiple times to reinforce learning.")
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    async def get_enhanced_question_audio_script(self, question: Question) -> str:
        """
        Get enhanced audio script for a question using Azure OpenAI.
        
        Args:
            question: Question to convert to audio script
            
        Returns:
            Enhanced audio script or fallback basic script
        """
        try:
            if self.openai_service:
                return await self.openai_service.generate_question_audio_script(question)
            else:
                # Fallback to basic script
                answers_text = ""
                for i, answer in enumerate(question.answers):
                    answers_text += f"Option {chr(65 + i)}: {answer.text}. "
                
                return f"Question: {question.text}. The answer options are: {answers_text}"
                
        except Exception as e:
            logger.error(f"Error generating enhanced audio script: {e}")
            # Fallback to basic script
            answers_text = ""
            for i, answer in enumerate(question.answers):
                answers_text += f"Option {chr(65 + i)}: {answer.text}. "
            
            return f"Question: {question.text}. The answer options are: {answers_text}"