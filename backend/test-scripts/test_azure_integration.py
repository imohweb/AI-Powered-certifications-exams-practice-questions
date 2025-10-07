"""
Test script to verify Azure Speech Service and Azure OpenAI integration.
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.config import settings
from app.services.azure_speech import AzureSpeechService
from app.services.azure_openai import AzureOpenAIService
from app.models.schemas import Question, Answer, QuestionType, DifficultyLevel


async def test_azure_services():
    """Test both Azure Speech Service and Azure OpenAI Service."""
    
    print("🚀 Testing Azure Services Integration")
    print("=" * 50)
    
    # Test Azure Speech Service
    print("\n1. Testing Azure Speech Service...")
    try:
        if settings.azure_speech_key and settings.azure_speech_region:
            speech_service = AzureSpeechService(
                speech_key=settings.azure_speech_key,
                speech_region=settings.azure_speech_region
            )
            
            # Test speech generation
            test_text = "Hello, this is a test of the Azure Speech Service integration."
            audio_data = await speech_service.text_to_speech(test_text)
            
            if audio_data:
                print(f"✅ Azure Speech Service working! Generated {len(audio_data)} bytes of audio")
            else:
                print("❌ Azure Speech Service failed to generate audio")
        else:
            print("❌ Azure Speech Service credentials not configured")
    except Exception as e:
        print(f"❌ Azure Speech Service error: {e}")
    
    # Test Azure OpenAI Service
    print("\n2. Testing Azure OpenAI Service...")
    try:
        if (settings.azure_openai_endpoint and 
            settings.azure_openai_key and 
            settings.azure_openai_deployment):
            
            openai_service = AzureOpenAIService(
                endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_key,
                deployment=settings.azure_openai_deployment
            )
            
            # Test connection
            is_connected = await openai_service.test_connection()
            
            if is_connected:
                print("✅ Azure OpenAI Service connected successfully!")
                
                # Test question enhancement
                sample_question = Question(
                    id="test_q1",
                    text="What is Microsoft Azure?",
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    answers=[
                        Answer(id="a1", text="A cloud computing platform", is_correct=True),
                        Answer(id="a2", text="A database system", is_correct=False),
                        Answer(id="a3", text="An operating system", is_correct=False)
                    ],
                    correct_answer_ids=["a1"],
                    difficulty=DifficultyLevel.BEGINNER,
                    topics=["Azure Basics"],
                    reference_links=[]
                )
                
                print("\n  Testing enhanced explanation generation...")
                enhanced_explanation = await openai_service.enhance_question_explanation(sample_question)
                print(f"✅ Generated enhanced explanation ({len(enhanced_explanation)} characters)")
                print(f"Preview: {enhanced_explanation[:200]}...")
                
            else:
                print("❌ Azure OpenAI Service connection failed")
        else:
            print("❌ Azure OpenAI Service credentials not configured")
    except Exception as e:
        print(f"❌ Azure OpenAI Service error: {e}")
    
    # Test combined functionality
    print("\n3. Testing Combined AI Features...")
    try:
        if (settings.azure_speech_key and settings.azure_openai_endpoint):
            from app.services.ai_agent import QuestionFlowAgent
            
            ai_agent = QuestionFlowAgent()
            
            # Test enhanced audio script generation
            sample_question = Question(
                id="test_q2",
                text="Which Azure service provides virtual machines?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                answers=[
                    Answer(id="b1", text="Azure App Service", is_correct=False),
                    Answer(id="b2", text="Azure Virtual Machines", is_correct=True),
                    Answer(id="b3", text="Azure Functions", is_correct=False)
                ],
                correct_answer_ids=["b2"],
                difficulty=DifficultyLevel.INTERMEDIATE,
                topics=["Azure Compute"],
                reference_links=[]
            )
            
            enhanced_script = await ai_agent.get_enhanced_question_audio_script(sample_question)
            print(f"✅ Generated enhanced audio script ({len(enhanced_script)} characters)")
            print(f"Preview: {enhanced_script[:200]}...")
            
    except Exception as e:
        print(f"❌ Combined AI features error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Azure Services Integration Test Complete!")


if __name__ == "__main__":
    asyncio.run(test_azure_services())