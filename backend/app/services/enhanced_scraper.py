"""
Enhanced scraper for Microsoft Learn practice assessments.
Uses Azure OpenAI to intelligently extract and process questions from practice assessment pages.
"""

import asyncio
import logging
import re
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin
import aiohttp
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from app.models.schemas import PracticeAssessment, Question, Answer, QuestionType, DifficultyLevel
from app.core.config import settings, CERTIFICATION_EXAMS
from app.services.azure_openai import AzureOpenAIService

logger = logging.getLogger(__name__)


class EnhancedMicrosoftLearnScraper:
    """AI-powered web scraper for Microsoft Learn practice assessments."""
    
    def __init__(self):
        self.base_url = "https://learn.microsoft.com/en-us/credentials/certifications/practice-assessments-for-microsoft-certifications"
        self.session = None
        self.driver = None
        
        # Initialize Azure OpenAI if available
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
                logger.info("Azure OpenAI integration enabled for enhanced scraping")
            except Exception as e:
                logger.warning(f"Failed to initialize Azure OpenAI for scraping: {e}")
                self.openai_service = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
        if self.driver:
            self.driver.quit()
    
    def _setup_selenium_driver(self) -> webdriver.Chrome:
        """Set up Selenium Chrome driver with appropriate options."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        try:
            # Install and use ChromeDriver with Service
            driver_path = ChromeDriverManager().install()
            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            raise
    
    async def scrape_practice_assessment(self, certification_code: str) -> Optional[PracticeAssessment]:
        """
        Scrape practice assessment for a given certification using AI enhancement.
        
        Args:
            certification_code: Microsoft certification exam code (e.g., 'AZ-900')
            
        Returns:
            PracticeAssessment object with AI-enhanced questions
        """
        try:
            logger.info(f"Starting AI-enhanced scraping for {certification_code}")
            
            # First, try to find the practice assessment URL
            practice_url = await self._find_practice_assessment_url(certification_code)
            
            if not practice_url:
                logger.warning(f"Could not find practice assessment URL for {certification_code}")
                return await self._generate_ai_sample_assessment(certification_code)
            
            # Navigate to practice assessment and extract content
            questions = await self._extract_questions_with_ai(practice_url, certification_code)
            
            if not questions:
                logger.warning(f"No questions extracted for {certification_code}, generating AI sample")
                return await self._generate_ai_sample_assessment(certification_code)
            
            # Create assessment object
            assessment = PracticeAssessment(
                id=f"assessment_{certification_code.lower()}",
                certification_code=certification_code,
                title=CERTIFICATION_EXAMS.get(certification_code, certification_code),
                description=f"AI-enhanced practice assessment for {CERTIFICATION_EXAMS.get(certification_code, certification_code)}",
                questions=questions,
                total_questions=len(questions),
                estimated_duration_minutes=len(questions) * 2
            )
            
            logger.info(f"Successfully created AI-enhanced assessment with {len(questions)} questions for {certification_code}")
            return assessment
            
        except Exception as e:
            logger.error(f"Error in AI-enhanced scraping for {certification_code}: {e}")
            return await self._generate_ai_sample_assessment(certification_code)
    
    async def _find_practice_assessment_url(self, certification_code: str) -> Optional[str]:
        """Find the practice assessment URL for a specific certification."""
        try:
            # Set up driver
            self.driver = self._setup_selenium_driver()
            
            # Navigate to the main practice assessments page
            logger.info(f"Navigating to practice assessments page for {certification_code}")
            self.driver.get(self.base_url)
            
            # Wait for page to load
            await asyncio.sleep(3)
            
            # Search for the certification code on the page
            try:
                # Look for links or text containing the certification code
                search_patterns = [
                    f"//a[contains(text(), '{certification_code}')]",
                    f"//a[contains(@href, '{certification_code.lower()}')]",
                    f"//*[contains(text(), '{certification_code}')]//ancestor::a",
                    f"//a[contains(text(), '{CERTIFICATION_EXAMS.get(certification_code, '')}')]"
                ]
                
                practice_link = None
                for pattern in search_patterns:
                    try:
                        elements = self.driver.find_elements(By.XPATH, pattern)
                        for element in elements:
                            href = element.get_attribute('href')
                            if href and ('practice' in href.lower() or 'assessment' in href.lower()):
                                practice_link = href
                                break
                        if practice_link:
                            break
                    except:
                        continue
                
                if practice_link:
                    logger.info(f"Found practice assessment URL: {practice_link}")
                    return practice_link
                
            except Exception as e:
                logger.warning(f"Error searching for practice assessment link: {e}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding practice assessment URL: {e}")
            return None
        finally:
            if self.driver:
                self.driver.quit()
    
    async def _extract_questions_with_ai(self, practice_url: str, certification_code: str) -> List[Question]:
        """Extract questions from practice assessment using AI enhancement."""
        try:
            # Set up driver
            self.driver = self._setup_selenium_driver()
            
            # Navigate to practice assessment
            logger.info(f"Extracting questions from: {practice_url}")
            self.driver.get(practice_url)
            
            # Wait for content to load
            await asyncio.sleep(5)
            
            # Get page content
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract raw content
            raw_content = soup.get_text()
            
            # Use AI to process and extract questions if available
            if self.openai_service:
                questions = await self._ai_process_content(raw_content, certification_code)
                if questions:
                    return questions
            
            # Fallback to basic extraction
            return await self._basic_question_extraction(soup, certification_code)
            
        except Exception as e:
            logger.error(f"Error extracting questions with AI: {e}")
            return []
        finally:
            if self.driver:
                self.driver.quit()
    
    async def _ai_process_content(self, content: str, certification_code: str) -> List[Question]:
        """Use Azure OpenAI to intelligently extract questions from content."""
        try:
            if not self.openai_service:
                return []
            
            # Prepare prompt for AI processing
            prompt = f"""
            You are an expert at extracting Microsoft certification practice questions from web content.
            
            Extract practice questions for {certification_code} ({CERTIFICATION_EXAMS.get(certification_code, certification_code)}) from this content:
            
            {content[:8000]}  # Limit content to stay within token limits
            
            Please extract and format questions as JSON with this structure:
            {{
                "questions": [
                    {{
                        "text": "Question text here",
                        "options": [
                            "Option A text",
                            "Option B text", 
                            "Option C text",
                            "Option D text"
                        ],
                        "correct_answer_index": 0,
                        "explanation": "Explanation of why this answer is correct",
                        "difficulty": "beginner|intermediate|advanced",
                        "topics": ["topic1", "topic2"]
                    }}
                ]
            }}
            
            Focus on:
            1. Clear, well-formed questions
            2. Multiple choice options (A, B, C, D)
            3. Correct answer identification
            4. Relevant explanations
            5. Appropriate difficulty level
            6. Relevant topics for {certification_code}
            
            Return valid JSON only.
            """
            
            response = await self.openai_service.client.chat.completions.create(
                model=self.openai_service.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Microsoft certification question extractor. Return only valid JSON."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=4000,
                temperature=0.1
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content
            
            # Try to extract JSON from response
            import json
            try:
                # Find JSON in response
                json_start = ai_response.find('{')
                json_end = ai_response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_content = ai_response[json_start:json_end]
                    parsed_data = json.loads(json_content)
                    
                    # Convert to Question objects
                    questions = []
                    for i, q_data in enumerate(parsed_data.get('questions', [])):
                        question = await self._convert_ai_question_to_object(q_data, i, certification_code)
                        if question:
                            questions.append(question)
                    
                    logger.info(f"AI extracted {len(questions)} questions for {certification_code}")
                    return questions
                    
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse AI response as JSON: {e}")
            
            return []
            
        except Exception as e:
            logger.error(f"Error in AI content processing: {e}")
            return []
    
    async def _convert_ai_question_to_object(self, q_data: Dict, index: int, certification_code: str) -> Optional[Question]:
        """Convert AI-extracted question data to Question object."""
        try:
            # Create answers
            answers = []
            options = q_data.get('options', [])
            correct_index = q_data.get('correct_answer_index', 0)
            
            for i, option_text in enumerate(options):
                answers.append(Answer(
                    id=f"answer_{certification_code}_{index}_{i}",
                    text=option_text,
                    is_correct=(i == correct_index)
                ))
            
            # Determine difficulty
            difficulty_map = {
                'beginner': DifficultyLevel.BEGINNER,
                'intermediate': DifficultyLevel.INTERMEDIATE,
                'advanced': DifficultyLevel.ADVANCED
            }
            difficulty = difficulty_map.get(q_data.get('difficulty', 'intermediate'), DifficultyLevel.INTERMEDIATE)
            
            # Create question
            question = Question(
                id=f"question_{certification_code}_{index}",
                text=q_data.get('text', ''),
                question_type=QuestionType.MULTIPLE_CHOICE,
                answers=answers,
                correct_answer_ids=[f"answer_{certification_code}_{index}_{correct_index}"],
                explanation=q_data.get('explanation', ''),
                difficulty=difficulty,
                topics=q_data.get('topics', []),
                reference_links=[]
            )
            
            return question
            
        except Exception as e:
            logger.error(f"Error converting AI question to object: {e}")
            return None
    
    async def _basic_question_extraction(self, soup: BeautifulSoup, certification_code: str) -> List[Question]:
        """Fallback basic question extraction."""
        # This is a simplified fallback - in practice, you'd implement more sophisticated parsing
        questions = []
        
        # Look for common question patterns
        question_elements = soup.find_all(['div', 'section'], class_=re.compile(r'question|quiz|assessment'))
        
        for i, element in enumerate(question_elements[:5]):  # Limit to 5 questions for demo
            question_text = element.get_text(strip=True)
            if len(question_text) > 50:  # Basic validation
                # Create a basic question
                answers = [
                    Answer(id=f"basic_a_{i}_0", text="Option A", is_correct=True),
                    Answer(id=f"basic_a_{i}_1", text="Option B", is_correct=False),
                    Answer(id=f"basic_a_{i}_2", text="Option C", is_correct=False),
                    Answer(id=f"basic_a_{i}_3", text="Option D", is_correct=False)
                ]
                
                question = Question(
                    id=f"basic_q_{certification_code}_{i}",
                    text=question_text[:200],  # Truncate for demo
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    answers=answers,
                    correct_answer_ids=[f"basic_a_{i}_0"],
                    difficulty=DifficultyLevel.INTERMEDIATE,
                    topics=[certification_code],
                    reference_links=[]
                )
                questions.append(question)
        
        return questions
    
    async def _generate_ai_sample_assessment(self, certification_code: str) -> PracticeAssessment:
        """Generate AI-powered sample assessment when scraping fails."""
        try:
            if self.openai_service:
                # Use AI to generate practice questions
                questions = await self._ai_generate_questions(certification_code)
                if questions:
                    return PracticeAssessment(
                        id=f"ai_generated_{certification_code.lower()}",
                        certification_code=certification_code,
                        title=f"AI-Generated Practice Assessment - {CERTIFICATION_EXAMS.get(certification_code, certification_code)}",
                        description=f"AI-generated practice questions for {certification_code}",
                        questions=questions,
                        total_questions=len(questions),
                        estimated_duration_minutes=len(questions) * 2
                    )
            
            # Fallback to static sample
            return await self.get_sample_assessment(certification_code)
            
        except Exception as e:
            logger.error(f"Error generating AI sample assessment: {e}")
            return await self.get_sample_assessment(certification_code)
    
    async def _ai_generate_questions(self, certification_code: str) -> List[Question]:
        """Generate practice questions using Azure OpenAI."""
        try:
            if not self.openai_service:
                return []
            
            cert_title = CERTIFICATION_EXAMS.get(certification_code, certification_code)
            
            prompt = f"""
            Generate 5 realistic Microsoft certification practice questions for {certification_code} - {cert_title}.
            
            Make questions that test real knowledge needed for this certification.
            Include proper multiple choice options and explanations.
            
            Return as JSON:
            {{
                "questions": [
                    {{
                        "text": "Realistic question about {cert_title}",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer_index": 0,
                        "explanation": "Clear explanation of correct answer",
                        "difficulty": "beginner|intermediate|advanced", 
                        "topics": ["relevant", "topics"]
                    }}
                ]
            }}
            """
            
            response = await self.openai_service.client.chat.completions.create(
                model=self.openai_service.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert Microsoft certification instructor for {certification_code}. Generate realistic practice questions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=3000,
                temperature=0.3
            )
            
            # Process response similar to _ai_process_content
            ai_response = response.choices[0].message.content
            
            import json
            try:
                json_start = ai_response.find('{')
                json_end = ai_response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_content = ai_response[json_start:json_end]
                    parsed_data = json.loads(json_content)
                    
                    questions = []
                    for i, q_data in enumerate(parsed_data.get('questions', [])):
                        question = await self._convert_ai_question_to_object(q_data, i, certification_code)
                        if question:
                            questions.append(question)
                    
                    logger.info(f"AI generated {len(questions)} questions for {certification_code}")
                    return questions
                    
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse AI generated questions: {e}")
            
            return []
            
        except Exception as e:
            logger.error(f"Error generating AI questions: {e}")
            return []
    
    async def get_sample_assessment(self, certification_code: str) -> PracticeAssessment:
        """Generate a basic sample assessment (fallback)."""
        # Basic sample questions as fallback
        sample_questions = [
            Question(
                id=f"sample_{certification_code}_1",
                text=f"What is the primary purpose of {CERTIFICATION_EXAMS.get(certification_code, certification_code)}?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                answers=[
                    Answer(id="sa1", text="To demonstrate expertise in Microsoft technologies", is_correct=True),
                    Answer(id="sa2", text="To learn programming basics", is_correct=False), 
                    Answer(id="sa3", text="To get a job at Microsoft", is_correct=False),
                    Answer(id="sa4", text="To use Microsoft Office", is_correct=False)
                ],
                correct_answer_ids=["sa1"],
                explanation=f"{certification_code} certification demonstrates expertise in Microsoft technologies and cloud services.",
                difficulty=DifficultyLevel.BEGINNER,
                topics=["Certification Basics"],
                reference_links=[]
            )
        ]
        
        return PracticeAssessment(
            id=f"sample_{certification_code.lower()}",
            certification_code=certification_code,
            title=f"Sample Assessment - {CERTIFICATION_EXAMS.get(certification_code, certification_code)}",
            description=f"Sample practice assessment for {certification_code}",
            questions=sample_questions,
            total_questions=len(sample_questions),
            estimated_duration_minutes=len(sample_questions) * 2
        )