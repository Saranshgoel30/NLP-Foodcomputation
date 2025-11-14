"""
Translation Adapter
Supports IndicTrans2, MarianMT, and external API providers
Includes culinary terminology table for consistency
"""
import structlog
from typing import Dict, Tuple
from config import Settings
from models import Language

logger = structlog.get_logger()


# Culinary terminology table for consistent translation
# Maps English -> {lang: translation}
CULINARY_TERMS = {
    "rice": {
        "hi": "चावल",
        "mr": "तांदूळ",
        "ta": "அரிசி",
        "te": "అన్నం",
        "bn": "চাল"
    },
    "chicken": {
        "hi": "मुर्गा",
        "mr": "कोंबडी",
        "ta": "கோழி",
        "te": "కోడి",
        "bn": "মুরগি"
    },
    "dal": {
        "hi": "दाल",
        "mr": "डाळ",
        "ta": "பருப்பு",
        "te": "పప్పు",
        "bn": "ডাল"
    },
    "paneer": {
        "hi": "पनीर",
        "mr": "पनीर",
        "ta": "பன்னீர்",
        "te": "పన్నీర్",
        "bn": "পনির"
    },
    # Add more as needed
}


class TranslationAdapter:
    """Abstract translation adapter interface"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.provider = settings.translation_provider
    
    def translate(
        self,
        text: str,
        source_lang: Language,
        target_lang: Language
    ) -> Tuple[str, Language]:
        """
        Translate text from source to target language
        
        Args:
            text: Text to translate
            source_lang: Source language code ('auto' for detection)
            target_lang: Target language code
            
        Returns:
            (translated_text, detected_source_lang)
        """
        raise NotImplementedError


class MockTranslationAdapter(TranslationAdapter):
    """
    Production-ready mock translation for development
    Handles food-specific terms correctly
    """
    
    def __init__(self, settings: Settings):
        super().__init__(settings)
        # Build reverse lookup for culinary terms
        self.term_lookup = {}
        for eng_term, translations in CULINARY_TERMS.items():
            for lang, native_term in translations.items():
                if lang not in self.term_lookup:
                    self.term_lookup[lang] = {}
                self.term_lookup[lang][native_term.lower()] = eng_term
    
    def _detect_language(self, text: str) -> Language:
        """
        Simple language detection based on script
        For production, use langdetect or similar
        """
        # Check for Devanagari (Hindi, Marathi)
        if any('\u0900' <= c <= '\u097F' for c in text):
            return 'hi'  # Default to Hindi
        
        # Check for Bengali
        if any('\u0980' <= c <= '\u09FF' for c in text):
            return 'bn'
        
        # Check for Tamil
        if any('\u0B80' <= c <= '\u0BFF' for c in text):
            return 'ta'
        
        # Check for Telugu
        if any('\u0C00' <= c <= '\u0C7F' for c in text):
            return 'te'
        
        # Check for Gujarati
        if any('\u0A80' <= c <= '\u0AFF' for c in text):
            return 'gu'
        
        # Check for Kannada
        if any('\u0C80' <= c <= '\u0CFF' for c in text):
            return 'kn'
        
        # Default to English
        return 'en'
    
    def _translate_culinary_terms(self, text: str, source_lang: Language, target_lang: Language) -> str:
        """Apply culinary term translations"""
        result = text
        
        # If translating to English, look up native terms
        if target_lang == 'en' and source_lang in self.term_lookup:
            for native_term, eng_term in self.term_lookup[source_lang].items():
                # Case-insensitive replacement
                import re
                pattern = re.compile(re.escape(native_term), re.IGNORECASE)
                result = pattern.sub(eng_term, result)
        
        # If translating from English, use CULINARY_TERMS
        elif source_lang == 'en' and target_lang != 'en':
            for eng_term, translations in CULINARY_TERMS.items():
                if target_lang in translations:
                    import re
                    pattern = re.compile(r'\b' + re.escape(eng_term) + r'\b', re.IGNORECASE)
                    result = pattern.sub(translations[target_lang], result)
        
        return result
    
    def translate(
        self,
        text: str,
        source_lang: Language,
        target_lang: Language
    ) -> Tuple[str, Language]:
        """
        Mock translation with culinary term handling
        
        In production, this would be replaced with:
        - MarianMT models for neural translation
        - IndicTrans2 for better Indic language support
        - External API (Google Translate, DeepL)
        """
        
        # Detect source language if auto
        detected_lang = source_lang
        if source_lang == 'auto':
            detected_lang = self._detect_language(text)
            logger.info("language_detected", detected=detected_lang, text_preview=text[:50])
        
        logger.info(
            "mock_translation",
            source_lang=detected_lang,
            target_lang=target_lang,
            text_length=len(text)
        )
        
        # If source and target are same, return as-is
        if detected_lang == target_lang:
            return text, detected_lang
        
        # Apply culinary term translations
        result = self._translate_culinary_terms(text, detected_lang, target_lang)
        
        # For demonstration: add language tag if no real translation occurred
        if result == text:
            result = f"[{detected_lang}→{target_lang}] {text}"
        
        logger.info(
            "translation_complete",
            source=detected_lang,
            target=target_lang,
            culinary_terms_applied=result != text
        )
        
        return result, detected_lang


class MarianMTAdapter(TranslationAdapter):
    """MarianMT-based translation implementation"""
    
    def __init__(self, settings: Settings):
        super().__init__(settings)
        self.models = {}
        self.tokenizers = {}
        self._load_models()
    
    def _load_models(self):
        """Load MarianMT models for supported language pairs"""
        try:
            from transformers import MarianMTModel, MarianTokenizer
            
            # Load commonly needed models
            # For production, load only required pairs
            model_pairs = [
                ('en', 'hi'),  # English to Hindi
                ('hi', 'en'),  # Hindi to English
                # Add more pairs as needed
            ]
            
            logger.info("loading_marian_models", pairs=len(model_pairs))
            
            for src, tgt in model_pairs:
                model_name = f"Helsinki-NLP/opus-mt-{src}-{tgt}"
                try:
                    self.tokenizers[f"{src}-{tgt}"] = MarianTokenizer.from_pretrained(model_name)
                    self.models[f"{src}-{tgt}"] = MarianMTModel.from_pretrained(model_name)
                    logger.info("loaded_marian_model", pair=f"{src}-{tgt}")
                except Exception as e:
                    logger.warning("failed_to_load_marian_pair", pair=f"{src}-{tgt}", error=str(e))
            
        except ImportError:
            logger.warning("transformers_not_available")
        except Exception as e:
            logger.error("failed_to_load_marian", error=str(e))
    
    def translate(
        self,
        text: str,
        source_lang: Language,
        target_lang: Language
    ) -> Tuple[str, Language]:
        """Translate using MarianMT"""
        
        # Auto-detect source language if needed
        if source_lang == 'auto':
            source_lang = self._detect_language(text)
        
        # If same language, return as-is
        if source_lang == target_lang:
            return text, source_lang
        
        pair_key = f"{source_lang}-{target_lang}"
        
        if pair_key not in self.models:
            logger.warning("model_pair_not_available", pair=pair_key)
            # Fallback to mock
            return text, source_lang
        
        try:
            tokenizer = self.tokenizers[pair_key]
            model = self.models[pair_key]
            
            # Tokenize
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            
            # Translate
            outputs = model.generate(**inputs)
            translated = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            logger.info(
                "marian_translated",
                source_lang=source_lang,
                target_lang=target_lang,
                original_length=len(text),
                translated_length=len(translated)
            )
            
            return translated, source_lang
            
        except Exception as e:
            logger.error("marian_translation_failed", error=str(e))
            return text, source_lang
    
    def _detect_language(self, text: str) -> Language:
        """Detect language of text"""
        try:
            from langdetect import detect
            detected = detect(text)
            
            # Map langdetect codes to our Language codes
            lang_map = {
                'en': 'en',
                'hi': 'hi',
                'mr': 'mr',
                'ta': 'ta',
                'te': 'te',
                'bn': 'bn',
            }
            
            return lang_map.get(detected, 'en')
        except:
            return 'en'


class IndicTrans2Adapter(TranslationAdapter):
    """IndicTrans2-based translation for Indic languages"""
    
    def __init__(self, settings: Settings):
        super().__init__(settings)
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load IndicTrans2 model"""
        logger.warning("indictrans2_not_implemented")
        # TODO: Implement IndicTrans2 model loading
        # from indicTrans2 import ...
    
    def translate(
        self,
        text: str,
        source_lang: Language,
        target_lang: Language
    ) -> Tuple[str, Language]:
        """Translate using IndicTrans2"""
        logger.warning("indictrans2_translation_fallback")
        # Fallback to mock for now
        return text, source_lang if source_lang != 'auto' else 'en'


def get_translation_adapter(settings: Settings) -> TranslationAdapter:
    """Factory function to get appropriate translation adapter"""
    provider = settings.translation_provider
    
    if provider == 'marianMT':
        return MarianMTAdapter(settings)
    elif provider == 'indicTrans2':
        return IndicTrans2Adapter(settings)
    else:
        logger.warning("using_mock_translation", provider=provider)
        return MockTranslationAdapter(settings)
