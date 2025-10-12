"""
API router for audio generation and text-to-speech functionality.
Handles audio requests, voice configuration, and audio streaming.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.background import BackgroundTasks
import io

from app.models.schemas import AudioRequest, AudioResponse, ApiResponse, Question
from app.services.azure_speech import AzureSpeechService
from app.services.ai_agent import QuestionFlowAgent
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


# Global AI agent instance
ai_agent = QuestionFlowAgent()


@router.get("/")
async def audio_health_check():
    """Health check endpoint for audio service."""
    return {
        "service": "audio",
        "status": "healthy",
        "azure_speech_configured": bool(settings.azure_speech_key and settings.azure_speech_region),
        "endpoints": {
            "generate": "POST /api/v1/audio/generate",
            "voices": "GET /api/v1/audio/voices",
            "play": "GET /api/v1/audio/play/{filename}",
            "transcribe": "POST /api/v1/audio/transcribe"
        }
    }


# Dependency to get Azure Speech Service
async def get_speech_service() -> AzureSpeechService:
    """Dependency to provide Azure Speech Service instance."""
    if not settings.azure_speech_key or not settings.azure_speech_region:
        raise HTTPException(
            status_code=503, 
            detail="Azure Speech Service not configured. Please set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION in your .env file."
        )
    return AzureSpeechService(
        speech_key=settings.azure_speech_key,
        speech_region=settings.azure_speech_region
    )


@router.post("/generate", response_model=AudioResponse)
async def generate_audio(
    request: AudioRequest,
    speech_service: AzureSpeechService = Depends(get_speech_service)
):
    """
    Generate audio from text using Azure Speech Service.
    
    Args:
        request: AudioRequest with text and voice settings
        speech_service: Azure Speech Service instance
        
    Returns:
        AudioResponse with audio URL and metadata
    """
    try:
        # Validate text length
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(request.text) > 10000:  # Azure Speech Service limit
            raise HTTPException(status_code=400, detail="Text too long (max 10,000 characters)")
        
        # Generate audio
        audio_response = await speech_service.generate_audio_response(request)
        
        if not audio_response:
            raise HTTPException(
                status_code=500, 
                detail="Failed to generate audio. Please check Azure Speech Service configuration."
            )
        
        logger.info(f"Generated audio for text length: {len(request.text)} characters")
        return audio_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        raise HTTPException(status_code=500, detail=f"Audio generation failed: {str(e)}")


@router.post("/generate/question/enhanced")
async def generate_enhanced_question_audio(
    question: Question,
    voice_name: Optional[str] = None,
    speech_service: AzureSpeechService = Depends(get_speech_service)
):
    """
    Generate enhanced audio for a question using AI-optimized script.
    
    Args:
        question: Question object with full details
        voice_name: Optional voice name
        speech_service: Azure Speech Service instance
        
    Returns:
        AudioResponse with AI-enhanced question audio
    """
    try:
        # Get AI-enhanced audio script
        enhanced_script = await ai_agent.get_enhanced_question_audio_script(question)
        
        # Generate audio request
        audio_request = AudioRequest(
            text=enhanced_script,
            voice_name=voice_name
        )
        
        # Generate audio
        audio_response = await speech_service.generate_audio_response(audio_request)
        
        if not audio_response:
            raise HTTPException(status_code=500, detail="Failed to generate enhanced question audio")
        
        logger.info(f"Generated enhanced question audio for question: {question.id}")
        return audio_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating enhanced question audio: {e}")
        raise HTTPException(status_code=500, detail=f"Enhanced question audio generation failed: {str(e)}")


@router.post("/generate/question")
async def generate_question_audio(
    question_text: str,
    answers: list[str],
    explanation: Optional[str] = None,
    voice_name: Optional[str] = None,
    speech_service: AzureSpeechService = Depends(get_speech_service)
):
    """
    Generate audio for a complete question including answers and explanation.
    
    Args:
        question_text: The question text
        answers: List of answer options
        explanation: Optional explanation text
        voice_name: Optional voice name
        speech_service: Azure Speech Service instance
        
    Returns:
        AudioResponse with complete question audio
    """
    try:
        # Construct complete text for the question
        full_text = f"Question: {question_text}\n\n"
        
        # Add answer options
        for i, answer in enumerate(answers, 1):
            full_text += f"Option {i}: {answer}\n"
        
        # Add explanation if provided
        if explanation:
            full_text += f"\nExplanation: {explanation}"
        
        # Generate audio request
        audio_request = AudioRequest(
            text=full_text,
            voice_name=voice_name
        )
        
        # Generate audio
        audio_response = await speech_service.generate_audio_response(audio_request)
        
        if not audio_response:
            raise HTTPException(status_code=500, detail="Failed to generate question audio")
        
        logger.info(f"Generated question audio with {len(answers)} answers")
        return audio_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating question audio: {e}")
        raise HTTPException(status_code=500, detail=f"Question audio generation failed: {str(e)}")


@router.get("/voices")
async def get_available_voices(
    speech_service: AzureSpeechService = Depends(get_speech_service)
):
    """
    Get list of available voices from Azure Speech Service.
    
    Returns:
        Dictionary of available voices with metadata
    """
    try:
        voices = await speech_service.get_available_voices()
        
        if not voices:
            # Return a default set if API call fails
            voices = {
                "en-US-JennyNeural": {
                    "name": "Jenny (Neural)",
                    "gender": "Female",
                    "locale": "en-US",
                    "neural": True
                },
                "en-US-GuyNeural": {
                    "name": "Guy (Neural)",
                    "gender": "Male", 
                    "locale": "en-US",
                    "neural": True
                },
                "en-US-AriaNeural": {
                    "name": "Aria (Neural)",
                    "gender": "Female",
                    "locale": "en-US",
                    "neural": True
                }
            }
        
        return {
            "voices": voices,
            "default_voice": settings.speech_voice_name,
            "total_count": len(voices)
        }
        
    except Exception as e:
        logger.error(f"Error getting available voices: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve available voices")


@router.get("/test")
async def test_speech_service(
    speech_service: AzureSpeechService = Depends(get_speech_service)
):
    """
    Test Azure Speech Service connectivity and configuration.
    
    Returns:
        Test result with connection status
    """
    try:
        # Test connection
        is_connected = await speech_service.test_connection()
        
        if is_connected:
            return {
                "status": "success",
                "message": "Azure Speech Service is working correctly",
                "region": settings.azure_speech_region,
                "voice": settings.speech_voice_name
            }
        else:
            return {
                "status": "error",
                "message": "Azure Speech Service connection failed",
                "region": settings.azure_speech_region
            }
            
    except Exception as e:
        logger.error(f"Error testing speech service: {e}")
        raise HTTPException(status_code=500, detail=f"Speech service test failed: {str(e)}")


@router.post("/stream")
async def stream_audio_generation(
    request: AudioRequest,
    speech_service: AzureSpeechService = Depends(get_speech_service)
):
    """
    Stream audio generation for real-time playback.
    
    Args:
        request: AudioRequest with text and voice settings
        speech_service: Azure Speech Service instance
        
    Returns:
        Streaming audio response
    """
    try:
        # Generate audio
        audio_data = await speech_service.text_to_speech(
            text=request.text,
            voice_name=request.voice_name,
            speech_rate=request.speech_rate,
            speech_pitch=request.speech_pitch
        )
        
        if not audio_data:
            raise HTTPException(status_code=500, detail="Failed to generate audio stream")
        
        # Create streaming response
        audio_stream = io.BytesIO(audio_data)
        
        def generate_audio_chunks():
            chunk_size = 8192
            while True:
                chunk = audio_stream.read(chunk_size)
                if not chunk:
                    break
                yield chunk
        
        return StreamingResponse(
            generate_audio_chunks(),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=generated_audio.mp3",
                "Content-Length": str(len(audio_data))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error streaming audio: {e}")
        raise HTTPException(status_code=500, detail=f"Audio streaming failed: {str(e)}")


@router.delete("/cache")
async def clear_audio_cache(
    speech_service: AzureSpeechService = Depends(get_speech_service)
):
    """
    Clear the audio cache to free up storage space.
    
    Returns:
        Cache clearing result
    """
    try:
        # Clear cache by triggering cleanup
        await speech_service._cleanup_cache_if_needed()
        
        return {
            "status": "success",
            "message": "Audio cache cleared successfully",
            "cache_directory": settings.audio_cache_dir
        }
        
    except Exception as e:
        logger.error(f"Error clearing audio cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear audio cache: {str(e)}")


@router.get("/cache/stats")
async def get_cache_stats():
    """
    Get statistics about the audio cache.
    
    Returns:
        Cache statistics including size and file count
    """
    try:
        from pathlib import Path
        
        cache_dir = Path(settings.audio_cache_dir)
        
        if not cache_dir.exists():
            return {
                "total_files": 0,
                "total_size_mb": 0,
                "cache_directory": str(cache_dir)
            }
        
        # Calculate cache statistics
        cache_files = list(cache_dir.glob("*.mp3"))
        total_files = len(cache_files)
        total_size = sum(f.stat().st_size for f in cache_files if f.is_file())
        total_size_mb = total_size / (1024 * 1024)
        
        return {
            "total_files": total_files,
            "total_size_mb": round(total_size_mb, 2),
            "max_size_mb": settings.max_audio_cache_size_mb,
            "cache_directory": str(cache_dir),
            "usage_percentage": round((total_size_mb / settings.max_audio_cache_size_mb) * 100, 1)
        }
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cache statistics: {str(e)}")


@router.post("/generate/multilingual", response_model=AudioResponse)
async def generate_multilingual_audio(
    text: str,
    language_code: str = "en",
    voice_type: str = "primary",
    speech_service: AzureSpeechService = Depends(get_speech_service)
):
    """
    Generate audio in a specific language with appropriate voice.
    
    Args:
        text: Text to convert to speech
        language_code: Two-letter language code (en, es, fr, de, it, pt, ja, ko, zh, ar, hi, ru)
        voice_type: Voice type - "primary" for questions, "secondary" for feedback
        speech_service: Azure Speech Service instance
        
    Returns:
        AudioResponse with audio in specified language
    """
    try:
        # Validate language code
        if language_code not in settings.supported_languages:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported language code: {language_code}. Supported languages: {', '.join(settings.supported_languages)}"
            )
        
        # Validate voice type
        valid_voice_types = ["primary", "secondary"]
        if voice_type not in valid_voice_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid voice type: {voice_type}. Must be one of: {', '.join(valid_voice_types)}"
            )
        
        # Generate multilingual audio
        audio_response = await speech_service.generate_multilingual_audio(
            text=text,
            language_code=language_code,
            voice_type=voice_type
        )
        
        if not audio_response:
            raise HTTPException(status_code=500, detail="Failed to generate multilingual audio")
        
        logger.info(f"Generated multilingual audio in {language_code} using {voice_type} voice")
        return audio_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating multilingual audio: {e}")
        raise HTTPException(status_code=500, detail=f"Multilingual audio generation failed: {str(e)}")


@router.post("/generate/question/multilingual", response_model=AudioResponse)
async def generate_multilingual_question_audio(
    question_text: str,
    answers: str,  # Comma-separated answers
    language_code: str = "en",
    speech_service: AzureSpeechService = Depends(get_speech_service)
):
    """
    Generate audio for a complete question in the specified language using primary voice.
    
    Args:
        question_text: The question text
        answers: Comma-separated list of answer options
        language_code: Two-letter language code
        speech_service: Azure Speech Service instance
        
    Returns:
        AudioResponse with complete question audio in specified language
    """
    try:
        # Validate language code
        if language_code not in settings.supported_languages:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language code: {language_code}. Supported languages: {', '.join(settings.supported_languages)}"
            )
        
        # Parse answers
        answer_list = [answer.strip() for answer in answers.split(',') if answer.strip()]
        
        # Generate multilingual question audio
        audio_response = await speech_service.generate_question_audio(
            question_text=question_text,
            answers=answer_list,
            language_code=language_code
        )
        
        if not audio_response:
            raise HTTPException(status_code=500, detail="Failed to generate multilingual question audio")
        
        logger.info(f"Generated multilingual question audio in {language_code}")
        return audio_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating multilingual question audio: {e}")
        raise HTTPException(status_code=500, detail=f"Multilingual question audio generation failed: {str(e)}")


@router.post("/generate/feedback", response_model=AudioResponse)
async def generate_feedback_audio(
    feedback_text: str,
    is_correct: bool = True,
    language_code: str = "en",
    skip_prefix: bool = False,
    speech_service: AzureSpeechService = Depends(get_speech_service)
):
    """
    Generate audio for feedback/results using secondary voice with emotional context.
    
    Args:
        feedback_text: The feedback text
        is_correct: Whether the answer was correct (affects voice style)
        language_code: Two-letter language code
        skip_prefix: If True, skip adding "Correct!" or "Incorrect." prefix
        speech_service: Azure Speech Service instance
        
    Returns:
        AudioResponse with feedback audio using secondary voice
    """
    try:
        # Validate language code
        if language_code not in settings.supported_languages:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language code: {language_code}. Supported languages: {', '.join(settings.supported_languages)}"
            )
        
        # Generate feedback audio with secondary voice
        audio_response = await speech_service.generate_feedback_audio(
            feedback_text=feedback_text,
            is_correct=is_correct,
            language_code=language_code,
            skip_prefix=skip_prefix
        )
        
        if not audio_response:
            raise HTTPException(status_code=500, detail="Failed to generate feedback audio")
        
        logger.info(f"Generated feedback audio ({'correct' if is_correct else 'incorrect'}) in {language_code}")
        return audio_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating feedback audio: {e}")
        raise HTTPException(status_code=500, detail=f"Feedback audio generation failed: {str(e)}")


@router.get("/voices/multilingual")
async def get_multilingual_voices():
    """
    Get available multilingual voices and supported languages.
    
    Returns:
        Dictionary with supported languages and their corresponding voices
    """
    try:
        from app.services.azure_speech import AzureSpeechService
        
        return {
            "supported_languages": settings.supported_languages,
            "multilingual_voices": AzureSpeechService.MULTILINGUAL_VOICES,
            "primary_voice_settings": {
                "voice_name": settings.speech_voice_name_primary,
                "speech_rate": settings.speech_rate_primary,
                "speech_pitch": settings.speech_pitch_primary
            },
            "secondary_voice_settings": {
                "voice_name": settings.speech_voice_name_secondary,
                "speech_rate": settings.speech_rate_secondary,
                "speech_pitch": settings.speech_pitch_secondary
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting multilingual voices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get multilingual voices: {str(e)}")


@router.post("/test/translation")
async def test_translation(
    text: str = "What is Azure?",
    language_code: str = "es"
):
    """
    Test translation functionality.
    
    Args:
        text: Text to translate
        language_code: Target language code
        
    Returns:
        Translation result
    """
    try:
        from app.services.azure_translator import get_translator_service
        
        translator = get_translator_service()
        if not translator:
            return {
                "status": "error",
                "message": "Azure Translator not configured",
                "original_text": text,
                "target_language": language_code,
                "translated_text": None
            }
        
        translated_text = await translator.translate_text(
            text=text,
            target_language=language_code,
            source_language="en"
        )
        
        return {
            "status": "success" if translated_text else "failed",
            "message": "Translation completed" if translated_text else "Translation failed",
            "original_text": text,
            "target_language": language_code,
            "translated_text": translated_text
        }
        
    except Exception as e:
        logger.error(f"Error testing translation: {e}")
        return {
            "status": "error",
            "message": f"Translation test failed: {str(e)}",
            "original_text": text,
            "target_language": language_code,
            "translated_text": None
        }