"""
Azure OpenAI Service integration for enhanced AI capabilities.
Provides intelligent question analysis, explanations, and enhanced responses.
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from openai import AsyncAzureOpenAI

from app.core.config import settings
from app.models.schemas import Question, Answer

logger = logging.getLogger(__name__)


class AzureOpenAIService:
    """Azure OpenAI Service wrapper for enhanced AI capabilities."""
    
    def __init__(self, endpoint: str, api_key: str, deployment: str):
        """
        Initialize Azure OpenAI Service.
        
        Args:
            endpoint: Azure OpenAI endpoint URL
            api_key: Azure OpenAI API key
            deployment: Azure OpenAI deployment name
        """
        self.endpoint = endpoint
        self.api_key = api_key
        self.deployment = deployment
        
        # Initialize OpenAI client
        self.client = AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=settings.azure_openai_api_version
        )
        
        logger.info(f"Azure OpenAI Service initialized with deployment: {deployment}")
    
    async def enhance_question_explanation(self, question: Question) -> str:
        """
        Generate enhanced explanation for a question using Azure OpenAI.
        
        Args:
            question: Question object to enhance
            
        Returns:
            Enhanced explanation string
        """
        try:
            # Prepare the prompt
            correct_answers = [answer.text for answer in question.answers if answer.is_correct]
            incorrect_answers = [answer.text for answer in question.answers if not answer.is_correct]
            
            prompt = f"""
            You are an expert Microsoft certification instructor. Provide a clear, comprehensive explanation for this practice question.

            Question: {question.text}
            
            Correct Answer(s): {', '.join(correct_answers)}
            Incorrect Options: {', '.join(incorrect_answers)}
            
            Please provide:
            1. Why the correct answer(s) are right
            2. Why the incorrect options are wrong
            3. Key concepts and best practices
            4. Real-world application examples
            
            Keep the explanation educational, clear, and focused on Microsoft certification exam preparation.
            """
            
            # Get response from Azure OpenAI
            response = await self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Microsoft certification instructor who provides clear, accurate explanations for practice questions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            explanation = response.choices[0].message.content
            logger.info(f"Generated enhanced explanation for question: {question.id}")
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating enhanced explanation: {e}")
            return question.explanation or "No explanation available."
    
    async def generate_study_tips(self, questions: List[Question]) -> str:
        """
        Generate personalized study tips based on a set of questions.
        
        Args:
            questions: List of questions to analyze
            
        Returns:
            Study tips and recommendations
        """
        try:
            # Analyze question topics and difficulty
            topics = set()
            difficulty_levels = []
            question_types = []
            
            for question in questions:
                topics.update(question.topics)
                difficulty_levels.append(question.difficulty.value)
                question_types.append(question.question_type.value)
            
            prompt = f"""
            You are a Microsoft certification study advisor. Based on this practice assessment data, provide personalized study recommendations.

            Topics covered: {', '.join(topics) if topics else 'Various Microsoft certification topics'}
            Difficulty levels: {', '.join(set(difficulty_levels))}
            Question types: {', '.join(set(question_types))}
            Total questions: {len(questions)}
            
            Please provide:
            1. Key study areas to focus on
            2. Recommended study resources (Microsoft Learn paths, documentation)
            3. Practice strategies for the exam
            4. Time management tips
            5. Common pitfalls to avoid
            
            Make the advice practical and specific to Microsoft certification preparation.
            """
            
            response = await self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Microsoft certification study advisor who provides practical, actionable study guidance."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1200,
                temperature=0.4
            )
            
            study_tips = response.choices[0].message.content
            logger.info(f"Generated study tips for {len(questions)} questions")
            return study_tips
            
        except Exception as e:
            logger.error(f"Error generating study tips: {e}")
            return "Focus on Microsoft documentation and hands-on practice with Azure services."
    
    async def analyze_answer_patterns(self, user_answers: Dict[str, List[str]]) -> str:
        """
        Analyze user's answer patterns and provide feedback.
        
        Args:
            user_answers: Dictionary mapping question IDs to selected answer IDs
            
        Returns:
            Analysis and feedback on answer patterns
        """
        try:
            prompt = f"""
            You are a Microsoft certification performance analyst. Analyze these user answer patterns and provide insights.

            User has answered {len(user_answers)} questions.
            Answer patterns: {user_answers}
            
            Please provide:
            1. Areas of strength based on correct answers
            2. Knowledge gaps that need improvement
            3. Specific Microsoft services/concepts to review
            4. Recommended next steps for study
            
            Focus on actionable feedback for Microsoft certification success.
            """
            
            response = await self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing Microsoft certification performance and providing targeted improvement recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            analysis = response.choices[0].message.content
            logger.info(f"Analyzed answer patterns for {len(user_answers)} questions")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing answer patterns: {e}")
            return "Continue practicing with more questions to improve your knowledge."
    
    async def generate_question_audio_script(self, question: Question) -> str:
        """
        Generate optimized audio script for text-to-speech conversion.
        
        Args:
            question: Question to convert to audio script
            
        Returns:
            Audio-optimized script
        """
        try:
            answers_text = ""
            for i, answer in enumerate(question.answers):
                answers_text += f"Option {chr(65 + i)}: {answer.text}. "
            
            prompt = f"""
            Convert this Microsoft certification practice question into a clear, natural audio script for text-to-speech.

            Question: {question.text}
            Answers: {answers_text}
            
            Create a script that:
            1. Presents the question clearly
            2. Lists all answer options with proper pacing
            3. Uses natural speech patterns
            4. Includes appropriate pauses
            5. Pronounces technical terms correctly
            
            Format for audio narration, not written text.
            """
            
            response = await self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating natural, clear audio scripts for educational content."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=600,
                temperature=0.2
            )
            
            audio_script = response.choices[0].message.content
            logger.info(f"Generated audio script for question: {question.id}")
            return audio_script
            
        except Exception as e:
            logger.error(f"Error generating audio script: {e}")
            # Fallback to basic script
            answers_text = ""
            for i, answer in enumerate(question.answers):
                answers_text += f"Option {chr(65 + i)}: {answer.text}. "
            
            return f"Question: {question.text}. The answer options are: {answers_text}"
    
    async def suggest_next_question(self, 
                                 current_question: Question, 
                                 user_performance: Dict[str, Any]) -> str:
        """
        Suggest the next question based on user performance and learning path.
        
        Args:
            current_question: Current question being answered
            user_performance: User's performance data
            
        Returns:
            Recommendation for next question type/topic
        """
        try:
            prompt = f"""
            You are an adaptive learning system for Microsoft certification preparation. 
            
            Current question topic: {', '.join(current_question.topics)}
            Current question difficulty: {current_question.difficulty.value}
            User performance data: {user_performance}
            
            Recommend the optimal next question characteristics:
            1. Topic area to focus on
            2. Difficulty level
            3. Question type
            4. Reasoning for this recommendation
            
            Optimize for effective learning progression.
            """
            
            response = await self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an adaptive learning AI that optimizes Microsoft certification study paths."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=400,
                temperature=0.4
            )
            
            recommendation = response.choices[0].message.content
            logger.info(f"Generated next question recommendation")
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generating next question suggestion: {e}")
            return "Continue with the next available question in the assessment."
    
    async def test_connection(self) -> bool:
        """
        Test connection to Azure OpenAI Service.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Test with a simple completion
            response = await self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "user",
                        "content": "Test connection"
                    }
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            return response.choices[0].message.content is not None
            
        except Exception as e:
            logger.error(f"Azure OpenAI Service connection test failed: {e}")
            return False
    
    async def get_deployment_info(self) -> Dict[str, Any]:
        """
        Get information about the Azure OpenAI deployment.
        
        Returns:
            Deployment information dictionary
        """
        try:
            # This would typically require a different API call
            # For now, return configured information
            return {
                "endpoint": self.endpoint,
                "deployment": self.deployment,
                "api_version": settings.azure_openai_api_version,
                "status": "configured"
            }
        except Exception as e:
            logger.error(f"Error getting deployment info: {e}")
            return {"status": "error", "error": str(e)}