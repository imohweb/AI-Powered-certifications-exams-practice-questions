"""
Azure Speech Service integration for text-to-speech functionality.
Provides secure, scalable voice synthesis with caching and optimization.
"""

import asyncio
import hashlib
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any
import azure.cognitiveservices.speech as speechsdk
import aiofiles

from app.core.config import settings
from app.models.schemas import AudioRequest, AudioResponse

logger = logging.getLogger(__name__)


class AzureSpeechService:
    """Azure Speech Service wrapper with caching, multilingual support, and dual voice functionality."""
    
    # Multilingual voice mappings for different languages
    MULTILINGUAL_VOICES = {
        "en": "en-US-JennyMultilingualNeural",  # English
        "es": "es-ES-ElviraNeural",             # Spanish
        "fr": "fr-FR-DeniseNeural",             # French
        "de": "de-DE-KatjaNeural",              # German
        "it": "it-IT-ElsaNeural",               # Italian
        "pt": "pt-PT-FernandaNeural",           # Portuguese
        "ja": "ja-JP-NanamiNeural",             # Japanese
        "ko": "ko-KR-SunHiNeural",              # Korean
        "zh": "zh-CN-XiaoxiaoNeural",           # Chinese
        "ar": "ar-SA-ZariyahNeural",            # Arabic
        "hi": "hi-IN-SwaraNeural",              # Hindi
        "ru": "ru-RU-SvetlanaNeural",           # Russian
    }
    
    # Voice types for different purposes
    class VoiceType:
        PRIMARY = "primary"      # For reading questions
        SECONDARY = "secondary"  # For feedback and results
    
    def __init__(self, speech_key: str, speech_region: str):
        """
        Initialize Azure Speech Service with multilingual and dual voice support.
        
        Args:
            speech_key: Azure Speech Service key
            speech_region: Azure Speech Service region
        """
        self.speech_key = speech_key
        self.speech_region = speech_region
        self.audio_cache_dir = Path(settings.audio_cache_dir)
        self.audio_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize speech config
        self.speech_config = speechsdk.SpeechConfig(
            subscription=speech_key,
            region=speech_region
        )
        
        # Set default voice and audio format
        self.speech_config.speech_synthesis_voice_name = settings.speech_voice_name_primary
        self.speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
        )
        
        logger.info(f"Azure Speech Service initialized for region: {speech_region}")
        logger.info(f"Primary voice: {settings.speech_voice_name_primary}")
        logger.info(f"Secondary voice: {settings.speech_voice_name_secondary}")
    
    def get_voice_for_language(self, language_code: str) -> str:
        """
        Get the appropriate voice for a given language.
        
        Args:
            language_code: Two-letter language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            Azure voice name for the language
        """
        # Fix language code mapping for Chinese
        if language_code == 'zh':
            language_code = 'zh'  # Keep as 'zh' for internal mapping
            
        voice_name = self.MULTILINGUAL_VOICES.get(language_code.lower(), 
                                                 settings.speech_voice_name_primary)
        logger.info(f"🌐 Language code '{language_code}' mapped to voice: {voice_name}")
        return voice_name
    
    def get_voice_settings(self, voice_type: str = VoiceType.PRIMARY) -> dict:
        """
        Get voice settings based on voice type.
        
        Args:
            voice_type: Type of voice (PRIMARY or SECONDARY)
            
        Returns:
            Dictionary with voice settings
        """
        if voice_type == self.VoiceType.SECONDARY:
            return {
                "voice_name": settings.speech_voice_name_secondary,
                "speech_rate": settings.speech_rate_secondary,
                "speech_pitch": settings.speech_pitch_secondary
            }
        else:
            return {
                "voice_name": settings.speech_voice_name_primary,
                "speech_rate": settings.speech_rate_primary,
                "speech_pitch": settings.speech_pitch_primary
            }
    
    async def text_to_speech(
        self,
        text: str,
        voice_name: Optional[str] = None,
        speech_rate: Optional[str] = None,
        speech_pitch: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Convert text to speech using Azure Speech Service.
        
        Args:
            text: Text to convert to speech
            voice_name: Azure voice name (optional)
            speech_rate: Speech rate adjustment (optional)
            speech_pitch: Speech pitch adjustment (optional)
            
        Returns:
            Audio data as bytes or None if conversion failed
        """
        try:
            # Create cache key
            cache_key = self._generate_cache_key(text, voice_name, speech_rate, speech_pitch)
            cached_audio = await self._get_cached_audio(cache_key)
            
            if cached_audio:
                logger.info(f"Using cached audio for key: {cache_key}")
                return cached_audio
            
            # Create SSML with voice settings
            ssml = self._create_ssml(text, voice_name, speech_rate, speech_pitch)
            
            # Configure speech synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=None  # Use in-memory audio
            )
            
            # Perform synthesis
            logger.info("Starting speech synthesis...")
            result = synthesizer.speak_ssml_async(ssml).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                audio_data = result.audio_data
                
                # Cache the audio
                await self._cache_audio(cache_key, audio_data)
                
                logger.info(f"Speech synthesis completed. Audio size: {len(audio_data)} bytes")
                return audio_data
                
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = speechsdk.CancellationDetails(result)
                logger.error(f"Speech synthesis canceled: {cancellation_details.reason}")
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    logger.error(f"Error details: {cancellation_details.error_details}")
                return None
            else:
                logger.error(f"Speech synthesis failed with reason: {result.reason}")
                return None
                
        except Exception as e:
            logger.error(f"Error in text-to-speech conversion: {e}")
            return None
    
    async def generate_audio_response(self, request: AudioRequest) -> Optional[AudioResponse]:
        """
        Generate audio response from AudioRequest.
        
        Args:
            request: AudioRequest with text and voice settings
            
        Returns:
            AudioResponse with audio URL and metadata
        """
        try:
            # Convert text to speech
            audio_data = await self.text_to_speech(
                text=request.text,
                voice_name=request.voice_name,
                speech_rate=request.speech_rate,
                speech_pitch=request.speech_pitch
            )
            
            if not audio_data:
                return None
            
            # Generate cache key and file path
            cache_key = self._generate_cache_key(
                request.text,
                request.voice_name,
                request.speech_rate,
                request.speech_pitch
            )
            
            audio_filename = f"{cache_key}.mp3"
            audio_url = f"/api/v1/audio-files/{audio_filename}"
            
            # Estimate duration (rough calculation)
            # Average speaking rate is about 150-200 words per minute
            word_count = len(request.text.split())
            estimated_duration = (word_count / 175) * 60  # seconds
            
            return AudioResponse(
                audio_url=audio_url,
                duration_seconds=estimated_duration,
                cache_key=cache_key
            )
            
        except Exception as e:
            logger.error(f"Error generating audio response: {e}")
            return None
    
    async def generate_question_audio(
        self,
        question_text: str,
        answers: list,
        language_code: str = "en"
    ) -> Optional[AudioResponse]:
        """
        Generate audio for a complete question using the primary voice in the specified language.
        
        Args:
            question_text: The question text
            answers: List of answer options
            language_code: Two-letter language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            AudioResponse with question audio
        """
        try:
            # Translate text if not in English
            translated_question = question_text
            translated_answers = answers
            
            if language_code != "en":
                from app.services.azure_translator import get_translator_service
                translator = get_translator_service()
                if translator:
                    logger.info(f"🌐 Translating question from English to {language_code}")
                    
                    # Translate question text
                    translated_result = await translator.translate_text(
                        text=question_text,
                        target_language=language_code,
                        source_language="en"
                    )
                    if translated_result:
                        translated_question = translated_result
                        logger.info(f"✅ Question translation successful")
                    
                    # Translate answers
                    translated_answers = []
                    for answer in answers:
                        answer_result = await translator.translate_text(
                            text=answer,
                            target_language=language_code,
                            source_language="en"
                        )
                        if answer_result:
                            translated_answers.append(answer_result)
                        else:
                            translated_answers.append(answer)  # Fallback to original
                    
                    logger.info(f"✅ Answers translation completed")
                else:
                    logger.warning(f"⚠️ Azure Translator not configured, using original English text")
            
            # Get appropriate voice for the language
            voice_name = self.get_voice_for_language(language_code)
            voice_settings = self.get_voice_settings(self.VoiceType.PRIMARY)
            
            # Build complete question text with translated content
            full_text = f"{translated_question}\n\n"
            
            # Add answer options
            option_labels = ["A", "B", "C", "D", "E", "F"]
            for i, answer in enumerate(translated_answers[:6]):  # Support up to 6 options
                if i < len(option_labels):
                    full_text += f"Option {option_labels[i]}: {answer}\n"
            
            # Create audio request
            request = AudioRequest(
                text=full_text,
                voice_name=voice_name,
                speech_rate=voice_settings["speech_rate"],
                speech_pitch=voice_settings["speech_pitch"]
            )
            
            audio_response = await self.generate_audio_response(request)
            if audio_response:
                # Include translated text for progressive display on frontend
                audio_response.translated_text = full_text
                # Include translated question and answers separately for UI display
                audio_response.translated_question = translated_question
                audio_response.translated_answers = translated_answers
            return audio_response
            
        except Exception as e:
            logger.error(f"Error generating question audio: {e}")
            return None
    
    async def generate_feedback_audio(
        self,
        feedback_text: str,
        is_correct: bool = True,
        language_code: str = "en",
        skip_prefix: bool = False
    ) -> Optional[AudioResponse]:
        """
        Generate audio for feedback/results using the secondary voice.
        
        Args:
            feedback_text: The feedback text
            is_correct: Whether the answer was correct (used for voice style)
            language_code: Two-letter language code
            skip_prefix: If True, skip adding "Correct!" or "Incorrect." prefix
            
        Returns:
            AudioResponse with feedback audio
        """
        try:
            # Determine voice settings
            voice_settings = self.get_voice_settings(self.VoiceType.SECONDARY)

            # Add emotional context prefix to feedback (unless skip_prefix is True)
            if skip_prefix:
                base_text = feedback_text
            else:
                if is_correct:
                    base_text = f"Correct! {feedback_text}"
                else:
                    base_text = f"Incorrect. {feedback_text}"

            # Translate if needed
            final_text = base_text
            chosen_voice = voice_settings["voice_name"]
            if language_code != "en":
                try:
                    from app.services.azure_translator import get_translator_service
                    translator = get_translator_service()
                    if translator:
                        translated = await translator.translate_text(
                            text=base_text,
                            target_language=language_code,
                            source_language="en"
                        )
                        if translated:
                            final_text = translated
                        else:
                            logger.warning("⚠️ Feedback translation failed; using English text")
                    else:
                        logger.warning("⚠️ Azure Translator not configured; using English text for feedback")
                except Exception as te:
                    logger.warning(f"⚠️ Feedback translation error: {te}")

                # For non-English, use a language-appropriate voice
                chosen_voice = self.get_voice_for_language(language_code)

            # Create audio request
            request = AudioRequest(
                text=final_text,
                voice_name=chosen_voice,
                speech_rate=voice_settings["speech_rate"],
                speech_pitch=voice_settings["speech_pitch"]
            )

            audio_response = await self.generate_audio_response(request)
            if audio_response:
                # Include translated feedback text for progressive display on frontend
                audio_response.translated_text = final_text
            return audio_response
            
        except Exception as e:
            logger.error(f"Error generating feedback audio: {e}")
            return None
    
    async def generate_multilingual_audio(
        self,
        text: str,
        language_code: str = "en",
        voice_type: str = VoiceType.PRIMARY
    ) -> Optional[AudioResponse]:
        """
        Generate audio in a specific language with appropriate voice and translation.
        
        Args:
            text: Text to convert to speech
            language_code: Two-letter language code
            voice_type: PRIMARY or SECONDARY voice type
            
        Returns:
            AudioResponse with audio in specified language
        """
        try:
            logger.info(f"🎤 Generating multilingual audio: language={language_code}, voice_type={voice_type}")
            
            # Translate text if not in English
            translated_text = text
            if language_code != "en":
                from app.services.azure_translator import get_translator_service
                translator = get_translator_service()
                if translator:
                    logger.info(f"🌐 Translating text from English to {language_code}")
                    logger.info(f"🔤 Original text (first 100 chars): {text[:100]}...")
                    translated_result = await translator.translate_text(
                        text=text,
                        target_language=language_code,
                        source_language="en"
                    )
                    if translated_result:
                        translated_text = translated_result
                        logger.info(f"✅ Translation successful: {text[:50]}... → {translated_text[:50]}...")
                    else:
                        logger.warning(f"⚠️ Translation failed, using original English text")
                else:
                    logger.warning(f"⚠️ Azure Translator not configured, using original English text")
            else:
                logger.info(f"🔤 Using original English text for language code: {language_code}")
            
            # Validate text length (Azure Speech Service has limits)
            max_length = 10000  # Azure Speech Service limit
            if len(translated_text) > max_length:
                logger.warning(f"⚠️ Text too long ({len(translated_text)} chars), truncating to {max_length}")
                translated_text = translated_text[:max_length] + "..."
            
            # Select appropriate voice
            if voice_type == self.VoiceType.SECONDARY:
                voice_settings = self.get_voice_settings(self.VoiceType.SECONDARY)
                # If non-English, prefer a language-appropriate secondary by reusing mapping
                if language_code != "en":
                    voice_name = self.get_voice_for_language(language_code)
                    logger.info(f"🔊 Using language-appropriate secondary voice for {language_code}: {voice_name}")
                else:
                    voice_name = voice_settings["voice_name"]
                    logger.info(f"🔊 Using default secondary voice: {voice_name}")
            else:
                voice_name = self.get_voice_for_language(language_code)
                voice_settings = self.get_voice_settings(self.VoiceType.PRIMARY)
                logger.info(f"🔊 Using primary voice for {language_code}: {voice_name}")
            
            # Create audio request with translated text
            request = AudioRequest(
                text=translated_text,
                voice_name=voice_name,
                speech_rate=voice_settings["speech_rate"],
                speech_pitch=voice_settings["speech_pitch"]
            )
            
            logger.info(f"🔊 Final audio request: voice={request.voice_name}, rate={request.speech_rate}, pitch={request.speech_pitch}")
            logger.info(f"🔊 Text length: {len(translated_text)} characters")
            
            return await self.generate_audio_response(request)
            
        except Exception as e:
            logger.error(f"Error generating multilingual audio: {e}")
            return None
    
    def _create_ssml(
        self,
        text: str,
        voice_name: Optional[str] = None,
        speech_rate: Optional[str] = None,
        speech_pitch: Optional[str] = None
    ) -> str:
        """
        Create simple, reliable SSML from text and voice settings.
        """
        # Use provided voice or default
        voice = voice_name or settings.speech_voice_name
        rate = speech_rate or settings.speech_rate
        pitch = speech_pitch or settings.speech_pitch
        
        # Determine language from voice name for proper SSML language tagging
        xml_lang = self._get_xml_lang_from_voice(voice)
        logger.info(f"🗣️ Creating simple SSML: voice={voice}, xml:lang={xml_lang}, rate={rate}, pitch={pitch}")
        
        # Clean text - just remove HTML and escape XML characters
        clean_text = self._clean_text_for_speech(text)
        
        # Create simple SSML without complex enhancements
        ssml = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{xml_lang}"><voice name="{voice}"><prosody rate="{rate}" pitch="{pitch}">{clean_text}</prosody></voice></speak>'
        
        return ssml
    
    def _get_xml_lang_from_voice(self, voice_name: str) -> str:
        """
        Get the appropriate xml:lang value from the voice name.
        
        Args:
            voice_name: Azure voice name (e.g., 'es-ES-ElviraNeural')
            
        Returns:
            Language tag for SSML (e.g., 'es-ES')
        """
        # Voice names typically follow format: language-region-VoiceNameNeural
        # Extract the language-region part
        parts = voice_name.split('-')
        if len(parts) >= 2:
            return f"{parts[0]}-{parts[1]}"
        
        # Fallback to English if we can't parse the voice name
        return "en-US"
    
    def _clean_text_for_speech(self, text: str) -> str:
        """
        Clean and prepare text for speech synthesis.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text suitable for speech synthesis
        """
        import html
        import re
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Escape XML characters for SSML safety
        text = html.escape(text, quote=False)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _generate_cache_key(
        self,
        text: str,
        voice_name: Optional[str] = None,
        speech_rate: Optional[str] = None,
        speech_pitch: Optional[str] = None
    ) -> str:
        """
        Generate cache key for audio file.
        
        Args:
            text: Text content
            voice_name: Voice name
            speech_rate: Speech rate
            speech_pitch: Speech pitch
            
        Returns:
            Cache key string
        """
        # Create hash from all parameters
        content = f"{text}_{voice_name}_{speech_rate}_{speech_pitch}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def _get_cached_audio(self, cache_key: str) -> Optional[bytes]:
        """
        Retrieve cached audio file.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached audio data or None
        """
        try:
            cache_file = self.audio_cache_dir / f"{cache_key}.mp3"
            if cache_file.exists():
                async with aiofiles.open(cache_file, 'rb') as f:
                    return await f.read()
        except Exception as e:
            logger.error(f"Error reading cached audio: {e}")
        return None
    
    async def _cache_audio(self, cache_key: str, audio_data: bytes):
        """
        Cache audio data to file.
        
        Args:
            cache_key: Cache key
            audio_data: Audio data to cache
        """
        try:
            cache_file = self.audio_cache_dir / f"{cache_key}.mp3"
            async with aiofiles.open(cache_file, 'wb') as f:
                await f.write(audio_data)
            
            # Check cache size and cleanup if needed
            await self._cleanup_cache_if_needed()
            
        except Exception as e:
            logger.error(f"Error caching audio: {e}")
    
    async def _cleanup_cache_if_needed(self):
        """Clean up cache if it exceeds the maximum size."""
        try:
            # Calculate total cache size
            total_size = sum(
                f.stat().st_size for f in self.audio_cache_dir.glob('*.mp3')
                if f.is_file()
            )
            
            max_size_bytes = settings.max_audio_cache_size_mb * 1024 * 1024
            
            if total_size > max_size_bytes:
                logger.info(f"Cache size ({total_size} bytes) exceeds limit. Cleaning up...")
                
                # Get all cache files sorted by modification time (oldest first)
                cache_files = [
                    f for f in self.audio_cache_dir.glob('*.mp3')
                    if f.is_file()
                ]
                cache_files.sort(key=lambda f: f.stat().st_mtime)
                
                # Delete oldest files until we're under the limit
                for cache_file in cache_files:
                    if total_size <= max_size_bytes * 0.8:  # Leave some buffer
                        break
                    
                    file_size = cache_file.stat().st_size
                    cache_file.unlink()
                    total_size -= file_size
                    logger.info(f"Deleted cached audio file: {cache_file.name}")
                
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
    
    async def get_available_voices(self) -> Dict[str, Any]:
        """
        Get list of available voices from Azure Speech Service.
        
        Returns:
            Dictionary of available voices with metadata
        """
        try:
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=None
            )
            
            # Get voice list
            result = synthesizer.get_voices_async().get()
            
            voices = {}
            if result.reason == speechsdk.ResultReason.VoicesListRetrieved:
                for voice in result.voices:
                    voices[voice.short_name] = {
                        "name": voice.name,
                        "gender": voice.gender.name,
                        "locale": voice.locale,
                        "neural": "Neural" in voice.name
                    }
            
            return voices
            
        except Exception as e:
            logger.error(f"Error getting available voices: {e}")
            return {}
    
    async def test_connection(self) -> bool:
        """
        Test connection to Azure Speech Service.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Try a simple synthesis
            test_audio = await self.text_to_speech("Connection test")
            return test_audio is not None
        except Exception as e:
            logger.error(f"Azure Speech Service connection test failed: {e}")
            return False