"""
Web scraping service for Microsoft Learn practice assessments.
This service crawls practice assessment pages and extracts questions, answers, and metadata.
"""

import asyncio
import logging
import re
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin, urlparse
import aiohttp
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from app.models.schemas import PracticeAssessment, Question, Answer, QuestionType, DifficultyLevel
from app.core.config import settings, CERTIFICATION_EXAMS, PRACTICE_ASSESSMENTS_BASE_URL

logger = logging.getLogger(__name__)


class MicrosoftLearnScraper:
    """Web scraper for Microsoft Learn practice assessments."""
    
    def __init__(self):
        self.base_url = PRACTICE_ASSESSMENTS_BASE_URL
        self.session = None
        self.driver = None
    
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
        
        # Install and use ChromeDriver
        driver_path = ChromeDriverManager().install()
        driver = webdriver.Chrome(driver_path, options=chrome_options)
        return driver
    
    async def get_available_certifications(self) -> List[Dict[str, str]]:
        """Get list of available certification practice assessments."""
        try:
            certifications = []
            for code, title in CERTIFICATION_EXAMS.items():
                certifications.append({
                    "code": code,
                    "title": title,
                    "url": f"{self.base_url}/{code.lower()}"
                })
            return certifications
        except Exception as e:
            logger.error(f"Error getting available certifications: {e}")
            return []
    
    async def scrape_practice_assessment(self, certification_code: str) -> Optional[PracticeAssessment]:
        """
        Scrape a complete practice assessment for a given certification.
        
        Args:
            certification_code: Microsoft certification exam code (e.g., 'AZ-900')
            
        Returns:
            PracticeAssessment object with questions and metadata
        """
        try:
            logger.info(f"Starting to scrape practice assessment for {certification_code}")
            
            # Construct the practice assessment URL
            assessment_url = self._build_assessment_url(certification_code)
            logger.info(f"Assessment URL: {assessment_url}")
            
            # Use Selenium for dynamic content
            self.driver = self._setup_selenium_driver()
            self.driver.get(assessment_url)
            
            # Wait for the page to load and check if practice assessment is available
            try:
                # Look for practice assessment link or button
                practice_link = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Practice Assessment') or contains(@href, 'practice')]"))
                )
                
                # Click on practice assessment link
                practice_url = practice_link.get_attribute('href')
                logger.info(f"Found practice assessment URL: {practice_url}")
                
                # Navigate to practice assessment
                self.driver.get(practice_url)
                
            except TimeoutException:
                logger.warning(f"No practice assessment found for {certification_code}")
                return None
            
            # Wait for questions to load
            await asyncio.sleep(3)
            
            # Extract questions
            questions = await self._extract_questions_from_page()
            
            if not questions:
                logger.warning(f"No questions found for {certification_code}")
                return None
            
            # Create assessment object
            assessment = PracticeAssessment(
                id=f"assessment_{certification_code.lower()}",
                certification_code=certification_code,
                title=CERTIFICATION_EXAMS.get(certification_code, certification_code),
                description=f"Practice assessment for {CERTIFICATION_EXAMS.get(certification_code, certification_code)}",
                questions=questions,
                total_questions=len(questions),
                estimated_duration_minutes=len(questions) * 2  # Estimate 2 minutes per question
            )
            
            logger.info(f"Successfully scraped {len(questions)} questions for {certification_code}")
            return assessment
            
        except Exception as e:
            logger.error(f"Error scraping practice assessment for {certification_code}: {e}")
            return None
        finally:
            if self.driver:
                self.driver.quit()
    
    def _build_assessment_url(self, certification_code: str) -> str:
        """Build the URL for a specific certification assessment."""
        # Microsoft Learn certification URLs follow a pattern
        code_lower = certification_code.lower()
        return f"https://learn.microsoft.com/en-us/credentials/certifications/exams/{code_lower}/"
    
    async def _extract_questions_from_page(self) -> List[Question]:
        """Extract questions from the current practice assessment page."""
        questions = []
        
        try:
            # Wait for questions to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "question"))
            )
            
            # Get page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract questions using various selectors
            question_elements = soup.find_all(['div', 'section'], class_=re.compile(r'question|quiz|assessment'))
            
            for idx, element in enumerate(question_elements):
                question = await self._parse_question_element(element, idx)
                if question:
                    questions.append(question)
            
            # If no questions found with standard selectors, try alternative approaches
            if not questions:
                questions = await self._extract_questions_alternative_method()
            
        except Exception as e:
            logger.error(f"Error extracting questions from page: {e}")
        
        return questions
    
    async def _parse_question_element(self, element, question_index: int) -> Optional[Question]:
        """Parse a single question element."""
        try:
            # Extract question text
            question_text_elem = element.find(['h2', 'h3', 'p'], class_=re.compile(r'question|text'))
            if not question_text_elem:
                return None
            
            question_text = question_text_elem.get_text(strip=True)
            if not question_text or len(question_text) < 10:
                return None
            
            # Extract answers
            answers = []
            answer_elements = element.find_all(['li', 'div'], class_=re.compile(r'answer|option|choice'))
            
            for idx, answer_elem in enumerate(answer_elements):
                answer_text = answer_elem.get_text(strip=True)
                if answer_text and len(answer_text) > 2:
                    answers.append(Answer(
                        id=f"answer_{question_index}_{idx}",
                        text=answer_text,
                        is_correct=False  # Will be determined later
                    ))
            
            # Determine question type
            question_type = self._determine_question_type(element, answers)
            
            # For now, assume the first answer is correct (this would need enhancement)
            correct_answer_ids = [answers[0].id] if answers else []
            if answers:
                answers[0].is_correct = True
            
            question = Question(
                id=f"question_{question_index}",
                text=question_text,
                question_type=question_type,
                answers=answers,
                correct_answer_ids=correct_answer_ids,
                difficulty=DifficultyLevel.INTERMEDIATE,
                topics=[],
                reference_links=[]
            )
            
            return question
            
        except Exception as e:
            logger.error(f"Error parsing question element: {e}")
            return None
    
    def _determine_question_type(self, element, answers: List[Answer]) -> QuestionType:
        """Determine the type of question based on element structure."""
        # Check for checkboxes (multiple select)
        if element.find_all('input', type='checkbox'):
            return QuestionType.MULTIPLE_SELECT
        
        # Check for radio buttons (multiple choice)
        if element.find_all('input', type='radio'):
            return QuestionType.MULTIPLE_CHOICE
        
        # Check for true/false
        if len(answers) == 2 and any('true' in answer.text.lower() or 'false' in answer.text.lower() for answer in answers):
            return QuestionType.TRUE_FALSE
        
        # Default to multiple choice
        return QuestionType.MULTIPLE_CHOICE
    
    async def _extract_questions_alternative_method(self) -> List[Question]:
        """Alternative method to extract questions when standard selectors don't work."""
        questions = []
        
        try:
            # Use JavaScript to extract dynamic content
            script = '''
            var questions = [];
            var questionElements = document.querySelectorAll('[data-question], .question-container, .quiz-question');
            questionElements.forEach(function(elem, index) {
                var questionText = elem.querySelector('.question-text, h2, h3, p');
                var answers = elem.querySelectorAll('.answer, .option, li');
                
                if (questionText && answers.length > 0) {
                    var questionData = {
                        index: index,
                        text: questionText.textContent.trim(),
                        answers: Array.from(answers).map(function(answer, ansIdx) {
                            return {
                                index: ansIdx,
                                text: answer.textContent.trim()
                            };
                        })
                    };
                    questions.push(questionData);
                }
            });
            return questions;
            '''
            
            question_data = self.driver.execute_script(script)
            
            for data in question_data:
                answers = []
                for answer_data in data['answers']:
                    if answer_data['text'] and len(answer_data['text']) > 2:
                        answers.append(Answer(
                            id=f"answer_{data['index']}_{answer_data['index']}",
                            text=answer_data['text'],
                            is_correct=answer_data['index'] == 0  # Assume first is correct
                        ))
                
                if answers:
                    question = Question(
                        id=f"question_{data['index']}",
                        text=data['text'],
                        question_type=QuestionType.MULTIPLE_CHOICE,
                        answers=answers,
                        correct_answer_ids=[answers[0].id],
                        difficulty=DifficultyLevel.INTERMEDIATE,
                        topics=[],
                        reference_links=[]
                    )
                    questions.append(question)
            
        except Exception as e:
            logger.error(f"Error in alternative question extraction: {e}")
        
        return questions
    
    async def get_sample_assessment(self, certification_code: str) -> PracticeAssessment:
        """
        Generate a sample assessment for testing purposes.
        This can be used when live scraping is not available.
        """
        sample_questions = []
        
        # Create sample questions based on certification type
        if certification_code.startswith('AZ'):
            # Azure-related questions
            sample_questions = [
                Question(
                    id="sample_q1",
                    text="What is Microsoft Azure?",
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    answers=[
                        Answer(id="a1", text="A cloud computing platform", is_correct=True),
                        Answer(id="a2", text="A database system", is_correct=False),
                        Answer(id="a3", text="An operating system", is_correct=False),
                        Answer(id="a4", text="A programming language", is_correct=False)
                    ],
                    correct_answer_ids=["a1"],
                    explanation="Microsoft Azure is a cloud computing platform and service provided by Microsoft.",
                    difficulty=DifficultyLevel.BEGINNER,
                    topics=["Cloud Computing", "Azure Basics"],
                    reference_links=["https://docs.microsoft.com/en-us/azure/"]
                ),
                Question(
                    id="sample_q2",
                    text="Which Azure service provides virtual machines?",
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    answers=[
                        Answer(id="b1", text="Azure App Service", is_correct=False),
                        Answer(id="b2", text="Azure Virtual Machines", is_correct=True),
                        Answer(id="b3", text="Azure Functions", is_correct=False),
                        Answer(id="b4", text="Azure Storage", is_correct=False)
                    ],
                    correct_answer_ids=["b2"],
                    explanation="Azure Virtual Machines (VMs) provide on-demand, scalable computing resources.",
                    difficulty=DifficultyLevel.BEGINNER,
                    topics=["Azure Compute", "Virtual Machines"],
                    reference_links=["https://docs.microsoft.com/en-us/azure/virtual-machines/"]
                )
            ]
        
        return PracticeAssessment(
            id=f"sample_{certification_code.lower()}",
            certification_code=certification_code,
            title=CERTIFICATION_EXAMS.get(certification_code, certification_code),
            description=f"Sample practice assessment for {certification_code}",
            questions=sample_questions,
            total_questions=len(sample_questions),
            estimated_duration_minutes=len(sample_questions) * 2
        )