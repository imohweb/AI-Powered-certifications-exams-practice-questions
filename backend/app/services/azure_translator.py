"""
Azure Translator Service integration for multilingual text translation.
Provides secure, scalable translation with caching and error handling.
"""

import logging
import hashlib
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
import aiofiles
import aiohttp
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)


class AzureTranslatorService:
    """Azure Translator Service wrapper with caching and multilingual support."""
    
    # Supported languages with their codes and display names
    SUPPORTED_LANGUAGES = {
        "en": {"name": "English", "code": "en"},
        "es": {"name": "Spanish", "code": "es"},
        "fr": {"name": "French", "code": "fr"},
        "de": {"name": "German", "code": "de"},
        "it": {"name": "Italian", "code": "it"},
        "pt": {"name": "Portuguese", "code": "pt"},
        "ja": {"name": "Japanese", "code": "ja"},
        "ko": {"name": "Korean", "code": "ko"},
        "zh": {"name": "Chinese (Simplified)", "code": "zh-Hans"},
        "ar": {"name": "Arabic", "code": "ar"},
        "hi": {"name": "Hindi", "code": "hi"},
        "ru": {"name": "Russian", "code": "ru"},
        "mt": {"name": "Maltese", "code": "mt"},
        "pcm": {"name": "Nigerian Pidgin", "code": "pcm"}
    }
    
    def __init__(self, translator_key: str, translator_endpoint: str, translator_region: str):
        """
        Initialize Azure Translator Service.
        
        Args:
            translator_key: Azure Translator Service key
            translator_endpoint: Azure Translator Service endpoint
            translator_region: Azure Translator Service region
        """
        self.translator_key = translator_key
        self.translator_endpoint = translator_endpoint
        self.translator_region = translator_region
        self.translation_cache_dir = Path(settings.audio_cache_dir).parent / "translation_cache"
        self.translation_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # API headers
        self.headers = {
            'Ocp-Apim-Subscription-Key': translator_key,
            'Ocp-Apim-Subscription-Region': translator_region,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4().hex)
        }
        
        logger.info(f"Azure Translator Service initialized for region: {translator_region}")
    
    def _get_cache_key(self, text: str, target_language: str, source_language: str = "en") -> str:
        """Generate cache key for translation."""
        content = f"{text}|{source_language}|{target_language}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    async def _get_cached_translation(self, cache_key: str) -> Optional[str]:
        """Get cached translation if available."""
        cache_file = self.translation_cache_dir / f"{cache_key}.json"
        try:
            if cache_file.exists():
                async with aiofiles.open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.loads(await f.read())
                    return cached_data.get('translation')
        except Exception as e:
            logger.warning(f"Failed to read translation cache: {e}")
        return None
    
    async def _save_translation_cache(self, cache_key: str, translation: str, text: str, target_language: str):
        """Save translation to cache."""
        cache_file = self.translation_cache_dir / f"{cache_key}.json"
        try:
            cache_data = {
                'translation': translation,
                'original_text': text,
                'target_language': target_language,
                'timestamp': str(datetime.utcnow())
            }
            async with aiofiles.open(cache_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(cache_data, ensure_ascii=False, indent=2))
        except Exception as e:
            logger.warning(f"Failed to save translation cache: {e}")
    
    async def translate_text(
        self, 
        text: str, 
        target_language: str, 
        source_language: str = "en"
    ) -> Optional[str]:
        """
        Translate text from source language to target language.
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code (default: "en")
            
        Returns:
            Translated text or None if translation fails
        """
        # Return original text if target is the same as source
        if target_language == source_language:
            return text
        
        # Check cache first
        cache_key = self._get_cache_key(text, target_language, source_language)
        cached_translation = await self._get_cached_translation(cache_key)
        if cached_translation:
            logger.info(f"🔄 Using cached translation for {source_language} → {target_language}")
            return cached_translation
        
        try:
            # Map language codes to Azure Translator codes
            azure_target_code = self.SUPPORTED_LANGUAGES.get(target_language, {}).get('code', target_language)
            
            # Prepare API request
            url = f"{self.translator_endpoint}/translate?api-version=3.0&from={source_language}&to={azure_target_code}"
            
            body = [{
                'text': text
            }]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=body) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result and len(result) > 0 and 'translations' in result[0]:
                            translated_text = result[0]['translations'][0]['text']
                            
                            # Save to cache
                            await self._save_translation_cache(
                                cache_key, translated_text, text, target_language
                            )
                            
                            logger.info(f"✅ Successfully translated text to {target_language}")
                            return translated_text
                    else:
                        error_text = await response.text()
                        logger.error(f"Translation API error {response.status}: {error_text}")
                        
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            
        return None
    
    async def get_supported_languages(self) -> Dict[str, Any]:
        """Get list of supported languages with their display names."""
        return self.SUPPORTED_LANGUAGES
    
    def get_language_code_for_speech(self, language_key: str) -> str:
        """
        Get the appropriate language code for Azure Speech Service.
        
        Args:
            language_key: Language key (e.g., 'zh' for Chinese)
            
        Returns:
            Language code compatible with Speech Service
        """
        # Map special cases for Speech Service compatibility
        speech_mappings = {
            'zh': 'zh-CN',  # Chinese Simplified
            'pt': 'pt-PT',  # Portuguese
            'ar': 'ar-SA',  # Arabic (Saudi Arabia)
            'hi': 'hi-IN',  # Hindi (India)
            'ru': 'ru-RU',  # Russian
        }
        
        return speech_mappings.get(language_key, language_key)


# Global translator instance
_translator_service: Optional[AzureTranslatorService] = None


def get_translator_service() -> Optional[AzureTranslatorService]:
    """Get the global translator service instance."""
    global _translator_service
    
    if _translator_service is None:
        if (settings.azure_translator_key and 
            settings.azure_translator_endpoint and 
            settings.azure_translator_region):
            
            _translator_service = AzureTranslatorService(
                translator_key=settings.azure_translator_key,
                translator_endpoint=settings.azure_translator_endpoint,
                translator_region=settings.azure_translator_region
            )
            logger.info("✅ Azure Translator Service initialized")
        else:
            logger.warning("⚠️ Azure Translator Service credentials not configured")
    
    return _translator_service