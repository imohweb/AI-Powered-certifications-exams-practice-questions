"""
Simplified AI-powered question generator for Microsoft certification practice assessments.
Uses only Azure OpenAI to generate realistic practice questions without browser dependencies.
"""

import asyncio
import logging
from typing import List, Optional
import uuid
from datetime import datetime

from app.models.schemas import (
    PracticeAssessment, Question, Answer, QuestionType, DifficultyLevel
)
from app.core.config import settings
from app.services.azure_openai import AzureOpenAIService

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Microsoft certification information
CERTIFICATION_EXAMS = {
    # Azure Fundamentals
    "AZ-900": "Microsoft Azure Fundamentals",
    
    # Azure Role-based
    "AZ-104": "Microsoft Azure Administrator",
    "AZ-204": "Developing Solutions for Microsoft Azure",
    "AZ-305": "Designing Microsoft Azure Infrastructure Solutions",
    "AZ-400": "Designing and Implementing Microsoft DevOps Solutions",
    "AZ-500": "Microsoft Azure Security Technologies",
    "AZ-700": "Designing and Implementing Microsoft Azure Networking Solutions",
    "AZ-800": "Administering Windows Server Hybrid Core Infrastructure",
    "AZ-801": "Configuring Windows Server Hybrid Advanced Services",
    
    # Microsoft 365
    "MS-900": "Microsoft 365 Fundamentals",
    "MS-102": "Microsoft 365 Administrator",
    "MS-203": "Microsoft 365 Messaging",
    "MS-700": "Managing Microsoft Teams",
    
    # Power Platform
    "PL-900": "Microsoft Power Platform Fundamentals",
    "PL-100": "Microsoft Power Platform App Maker",
    "PL-200": "Microsoft Power Platform Functional Consultant",
    "PL-300": "Microsoft Power BI Data Analyst",
    "PL-400": "Microsoft Power Platform Developer",
    "PL-500": "Microsoft Power Automate RPA Developer",
    "PL-600": "Microsoft Power Platform Solution Architect",
    
    # Dynamics 365
    "MB-910": "Microsoft Dynamics 365 Fundamentals (CRM)",
    "MB-920": "Microsoft Dynamics 365 Fundamentals (ERP)",
    "MB-200": "Microsoft Power Platform + Dynamics 365 Core",
    "MB-220": "Microsoft Dynamics 365 Marketing",
    "MB-230": "Microsoft Dynamics 365 Customer Service",
    "MB-240": "Microsoft Dynamics 365 Field Service",
    "MB-300": "Microsoft Dynamics 365: Core Finance and Operations",
    "MB-330": "Microsoft Dynamics 365 Supply Chain Management",
    
    # Security, Compliance, and Identity
    "SC-900": "Microsoft Security, Compliance, and Identity Fundamentals",
    "SC-200": "Microsoft Security Operations Analyst",
    "SC-300": "Microsoft Identity and Access Administrator",
    "SC-400": "Microsoft Information Protection Administrator",
    
    # Data & AI
    "DP-900": "Microsoft Azure Data Fundamentals",
    "DP-100": "Designing and Implementing a Data Science Solution on Azure",
    "DP-203": "Data Engineering on Microsoft Azure",
    "DP-300": "Administering Microsoft Azure SQL Solutions",
    "DP-420": "Designing and Implementing Cloud-Native Applications Using Microsoft Azure Cosmos DB",
    "AI-900": "Microsoft Azure AI Fundamentals",
    "AI-102": "Designing and Implementing a Microsoft Azure AI Solution",
    
    # Modern Work
    "MD-100": "Windows Client",
    "MD-101": "Managing Modern Desktops",
    "MD-102": "Endpoint Administrator",
    
    # Mixed Reality
    "AZ-220": "Microsoft Azure IoT Developer",
    
    # Developer
    "AZ-120": "Planning and Administering Microsoft Azure for SAP Workloads",
    "AZ-140": "Configuring and Operating Microsoft Azure Virtual Desktop",
    
    # Database
    "DP-080": "Querying Data with Microsoft Transact-SQL"
}


class SimplifiedAIQuestionGenerator:
    """Simplified AI-powered question generator without browser dependencies."""
    
    def __init__(self):
        """Initialize the AI question generator."""
        self.azure_openai = AzureOpenAIService(
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key,
            deployment=settings.azure_openai_deployment
        )
        logger.info("Initialized Simplified AI Question Generator")
    
    async def generate_practice_assessment(self, certification_code: str) -> Optional[PracticeAssessment]:
        """
        Generate a practice assessment for a given certification using AI.
        
        Args:
            certification_code: Microsoft certification exam code (e.g., 'AZ-900')
            
        Returns:
            PracticeAssessment object with AI-generated questions
        """
        try:
            logger.info(f"Generating AI practice assessment for {certification_code}")
            
            # Get certification details
            certification_title = CERTIFICATION_EXAMS.get(certification_code, certification_code)
            
            # Generate questions using AI
            questions = await self._generate_ai_questions(certification_code, certification_title)
            
            if not questions:
                logger.error(f"Failed to generate questions for {certification_code}")
                return None
            
            # Create assessment object
            assessment = PracticeAssessment(
                id=f"assessment_{certification_code.lower()}_{uuid.uuid4().hex[:8]}",
                certification_code=certification_code,
                title=f"Practice Assessment - {certification_title}",
                description=f"AI-generated practice questions for {certification_title}",
                questions=questions,
                total_questions=len(questions),
                estimated_duration_minutes=len(questions) * 2  # 2 minutes per question for 50 questions = 100 minutes
            )
            
            logger.info(f"Successfully generated assessment with {len(questions)} questions for {certification_code}")
            return assessment
            
        except Exception as e:
            logger.error(f"Error generating assessment for {certification_code}: {e}")
            return None
    
    async def _generate_ai_questions(self, certification_code: str, certification_title: str) -> List[Question]:
        """Generate AI-powered questions for a specific certification."""
        try:
            # Create a detailed prompt for question generation
            prompt = self._create_question_generation_prompt(certification_code, certification_title)
            
            # Get AI response using the correct method
            response = await self._generate_text_with_openai(prompt)
            
            if not response:
                logger.error(f"No AI response received for {certification_code}")
                return []
            
            # Parse the AI response into Question objects
            questions = self._parse_ai_response_to_questions(response)
            
            logger.info(f"Generated {len(questions)} AI questions for {certification_code}")
            return questions
            
        except Exception as e:
            logger.error(f"Error generating AI questions for {certification_code}: {e}")
            return []
    
    async def _generate_text_with_openai(self, prompt: str) -> str:
        """Generate text using Azure OpenAI."""
        try:
            response = await self.azure_openai.client.chat.completions.create(
                model=self.azure_openai.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Microsoft certification trainer who creates realistic practice exam questions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=8000,  # Increased for 50 questions
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating text with OpenAI: {e}")
            return ""
    
    def _create_question_generation_prompt(self, certification_code: str, certification_title: str) -> str:
        """Create a detailed prompt for AI question generation."""
        
        # Get certification-specific context
        context = self._get_certification_context(certification_code)
        
        prompt = f"""
Generate 50 realistic practice exam questions for the Microsoft certification: {certification_title} ({certification_code}).

These questions should be based on the official Microsoft Learn practice assessments available at:
https://learn.microsoft.com/en-us/credentials/certifications/practice-assessments-for-microsoft-certifications

{context}

Requirements:
- Generate exactly 50 questions covering all exam domains
- Questions should match the style and difficulty of official Microsoft practice assessments
- Include a variety of difficulty levels: 15 beginner, 25 intermediate, 10 advanced
- Cover all major domains and skills measured in the {certification_code} exam
- Use realistic scenarios that professionals encounter
- Include technical details and specific Microsoft product knowledge

For each question, provide:
1. A clear, technical question text (similar to official Microsoft exams)
2. 4 multiple-choice answers (A, B, C, D)
3. Indicate which answer is correct
4. Brief technical explanation of the correct answer
5. Difficulty level (beginner, intermediate, advanced)
6. 2-3 relevant exam domains/skills

Format each question as:
QUESTION 1:
Text: [question text - make it detailed and scenario-based like Microsoft exams]
A) [answer option A]
B) [answer option B]
C) [answer option C]
D) [answer option D]
Correct: [A/B/C/D]
Explanation: [technical explanation with reasoning]
Difficulty: [beginner/intermediate/advanced]
Topics: [domain1, domain2, skill area]

Continue for all 50 questions. Ensure questions cover:
- All major exam domains proportionally
- Real-world scenarios
- Microsoft-specific terminology and concepts
- Current technology and best practices
- Hands-on implementation knowledge
"""
        
        return prompt
    
    def _get_certification_context(self, certification_code: str) -> str:
        """Get specific context and focus areas for different certifications."""
        
        context_map = {
            "AZ-900": """
Official Microsoft Azure Fundamentals exam domains:
1. Describe cloud concepts (25–30%)
   - Benefits and considerations of cloud services
   - Differences between Infrastructure-as-a-Service (IaaS), Platform-as-a-Service (PaaS), and Software-as-a-Service (SaaS)
   - Differences between public, private, and hybrid cloud models
2. Describe Azure architecture and services (35–40%)
   - Core Azure architectural components, compute, networking, storage services
   - Azure identity, access, and security services
3. Describe Azure management and governance (30–35%)
   - Cost management, features and tools for governance and compliance
   - Features and tools for managing and deploying Azure resources
Generate questions covering real Azure scenarios, services, and implementation decisions.
""",
            "AZ-104": """
Official Microsoft Azure Administrator exam domains:
1. Manage Azure identities and governance (15–20%)
   - Azure Active Directory, users, groups, administrative units, RBAC
2. Implement and manage storage (15–20%)
   - Storage accounts, blob storage, Azure Files, backup and recovery
3. Deploy and manage Azure compute resources (20–25%)
   - Virtual machines, Azure App Service, containers, Azure Functions
4. Configure and manage virtual networking (20–25%)
   - Virtual networks, name resolution, security groups, load balancing
5. Monitor and maintain Azure resources (10–15%)
   - Azure Monitor, Log Analytics, alerts, backup and recovery
Generate hands-on administrative scenarios and troubleshooting questions.
""",
            "AZ-204": """
Official Azure Developer exam domains:
1. Develop Azure compute solutions (25–30%)
   - Azure Functions, App Service, container solutions
2. Develop for Azure storage (15–20%)
   - Cosmos DB, blob storage, relational databases
3. Implement Azure security (20–25%)
   - Authentication, authorization, Key Vault, Managed Identities
4. Monitor, troubleshoot, and optimize Azure solutions (15–20%)
   - Application Insights, caching, CDN optimization
5. Connect to and consume Azure services (15–20%)
   - API Management, Event-based solutions, message-based solutions
Generate coding scenarios and implementation challenges.
""",
            "MS-900": """
Official Microsoft 365 Fundamentals exam domains:
1. Describe Microsoft 365 core services and concepts (30–35%)
   - Microsoft 365 productivity services, collaboration tools
2. Explain Microsoft 365 security, compliance, privacy, and trust (30–35%)
   - Security features, compliance solutions, privacy in Microsoft 365
3. Describe Microsoft 365 pricing, licensing, and support (20–25%)
   - Licensing options, pricing models, support offerings
4. Describe Microsoft 365 productivity solutions and capabilities (15–20%)
   - Productivity capabilities, Microsoft 365 Apps, SharePoint, Teams
Generate questions about Microsoft 365 administration and business scenarios.
""",
            "PL-900": """
Official Power Platform Fundamentals exam domains:
1. Describe the business value of the Microsoft Power Platform (15–20%)
   - Business value and platform components
2. Identify foundational components of Microsoft Power Platform (15–20%)
   - Connectors, AI Builder, Common Data Service
3. Demonstrate the business value of Power BI (15–20%)
   - Power BI components, dashboards, reports
4. Describe the business value of Power Apps (15–20%)
   - Canvas apps, model-driven apps, portals
5. Demonstrate the business value of Power Automate (15–20%)
   - Flow types, templates, connectors
6. Describe the business value of Power Virtual Agents (10–15%)
   - Chatbots, topics, entities
Generate citizen developer scenarios and business process automation questions.
""",
            "SC-900": """
Official Security, Compliance, and Identity Fundamentals exam domains:
1. Describe security and compliance concepts (10–15%)
   - Shared responsibility model, defense in depth, Zero Trust
2. Describe identity concepts (20–25%)
   - Authentication vs authorization, identity providers, directory services
3. Describe the function and identity types of Microsoft Azure Active Directory (25–30%)
   - Azure AD, identity types, authentication methods
4. Describe the authentication capabilities of Microsoft Azure AD (25–30%)
   - MFA, self-service password reset, password protection
5. Describe access management capabilities of Azure AD (15–20%)
   - Conditional access, Azure AD roles, access reviews
Generate identity and security scenarios with Zero Trust principles.
""",
            "DP-900": """
Official Azure Data Fundamentals exam domains:
1. Describe core data concepts (25–30%)
   - Data types, file formats, databases, analytics workloads
2. Identify considerations for relational data on Azure (20–25%)
   - Azure SQL Database, Azure Database services, SQL queries
3. Describe considerations for working with non-relational data on Azure (15–20%)
   - Azure Cosmos DB, Azure Storage, Azure Data Lake
4. Describe an analytics workload on Azure (30–35%)
   - Azure Synapse Analytics, Azure HDInsight, Power BI, real-time analytics
Generate data engineering and analytics scenarios.
""",
            "AI-900": """
Official Azure AI Fundamentals exam domains:
1. Describe Artificial Intelligence workloads and considerations (15–20%)
   - AI concepts, responsible AI principles
2. Describe fundamental principles of machine learning on Azure (20–25%)
   - Machine learning types, Azure Machine Learning service
3. Describe features of computer vision workloads on Azure (15–20%)
   - Computer Vision API, Custom Vision, Face API
4. Describe features of Natural Language Processing (NLP) workloads on Azure (15–20%)
   - Text Analytics, Language Understanding, Speech services
5. Describe features of generative AI workloads on Azure (15–20%)
   - Azure OpenAI Service, responsible AI for generative AI
Generate AI implementation scenarios and use cases.
"""
        }
        
        return context_map.get(certification_code, f"""
Focus on the core concepts and technologies covered in the {certification_code} certification.
Generate questions that test practical knowledge and understanding of the subject matter.
""")
    
    def _parse_ai_response_to_questions(self, ai_response: str) -> List[Question]:
        """Parse AI response text into Question objects."""
        questions = []
        
        try:
            # Split response into individual questions
            question_blocks = ai_response.split("QUESTION")
            
            for i, block in enumerate(question_blocks[1:], 1):  # Skip the first empty split
                try:
                    question = self._parse_single_question(block, i)
                    if question:
                        questions.append(question)
                except Exception as e:
                    logger.error(f"Error parsing question {i}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
        
        return questions
    
    def _parse_single_question(self, question_block: str, question_num: int) -> Optional[Question]:
        """Parse a single question block into a Question object."""
        try:
            lines = [line.strip() for line in question_block.strip().split('\n') if line.strip()]
            
            # Extract question components
            question_text = ""
            answers = []
            correct_answer = ""
            explanation = ""
            difficulty = DifficultyLevel.INTERMEDIATE
            topics = []
            
            for line in lines:
                if line.startswith("Text:"):
                    question_text = line.replace("Text:", "").strip()
                elif line.startswith(("A)", "B)", "C)", "D)")):
                    answer_letter = line[0]
                    answer_text = line[3:].strip()
                    answers.append(Answer(
                        id=f"answer_{answer_letter.lower()}",
                        text=answer_text,
                        is_correct=False
                    ))
                elif line.startswith("Correct:"):
                    correct_answer = line.replace("Correct:", "").strip().upper()
                elif line.startswith("Explanation:"):
                    explanation = line.replace("Explanation:", "").strip()
                elif line.startswith("Difficulty:"):
                    diff_text = line.replace("Difficulty:", "").strip().lower()
                    if diff_text in ["beginner", "intermediate", "advanced"]:
                        difficulty = DifficultyLevel(diff_text)
                elif line.startswith("Topics:"):
                    topics_text = line.replace("Topics:", "").strip()
                    topics = [topic.strip() for topic in topics_text.split(",")]
            
            # Mark correct answer
            for answer in answers:
                if answer.id == f"answer_{correct_answer.lower()}":
                    answer.is_correct = True
                    break
            
            # Create Question object
            question = Question(
                id=f"question_{uuid.uuid4().hex[:8]}",
                text=question_text,
                question_type=QuestionType.MULTIPLE_CHOICE,
                answers=answers,
                correct_answer_ids=[f"answer_{correct_answer.lower()}"],
                explanation=explanation,
                difficulty=difficulty,
                topics=topics
            )
            
            return question
            
        except Exception as e:
            logger.error(f"Error parsing question {question_num}: {e}")
            return None


# Global instance
ai_question_generator = SimplifiedAIQuestionGenerator()