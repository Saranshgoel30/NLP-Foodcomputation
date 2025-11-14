"""
Enhanced Speech-to-Text with Indian Language Optimization
Integrates Whisper with LLM post-processing for accuracy
"""
import base64
import io
import wave
from typing import Tuple, Optional, Dict, Any
from pathlib import Path
import structlog
from models import Language

logger = structlog.get_logger()

# Indian language codes and optimizations
INDIAN_LANGUAGES = {
    'hi': {'name': 'Hindi', 'whisper_code': 'hi', 'rtl': False},
    'mr': {'name': 'Marathi', 'whisper_code': 'mr', 'rtl': False},
    'ta': {'name': 'Tamil', 'whisper_code': 'ta', 'rtl': False},
    'te': {'name': 'Telugu', 'whisper_code': 'te', 'rtl': False},
    'bn': {'name': 'Bengali', 'whisper_code': 'bn', 'rtl': False},
    'gu': {'name': 'Gujarati', 'whisper_code': 'gu', 'rtl': False},
    'kn': {'name': 'Kannada', 'whisper_code': 'kn', 'rtl': False},
    'ml': {'name': 'Malayalam', 'whisper_code': 'ml', 'rtl': False},
    'pa': {'name': 'Punjabi', 'whisper_code': 'pa', 'rtl': False},
    'or': {'name': 'Odia', 'whisper_code': 'or', 'rtl': False},
}

# Food-related terminology for better recognition
FOOD_CONTEXT_TERMS = {
    'en': [
        'recipe', 'ingredient', 'cook', 'cuisine', 'dish', 'meal',
        'breakfast', 'lunch', 'dinner', 'snack', 'vegetarian', 'vegan'
    ],
    'hi': [
        'रेसिपी', 'खाना', 'पकाना', 'व्यंजन', 'भोजन', 'नाश्ता',
        'दोपहर का खाना', 'रात का खाना', 'शाकाहारी'
    ],
    'ta': [
        'செய்முறை', 'உணவு', 'சமைக்க', 'உணவு வகை', 'காலை உணவு',
        'மதிய உணவு', 'இரவு உணவு', 'சைவம்'
    ],
    'te': [
        'వంటకం', 'ఆహారం', 'వండటం', 'వంటకాలు', 'అల్పాహారం',
        'మధ్యాహ్న భోజనం', 'రాత్రి భోజనం', 'శాకాహారం'
    ],
    'bn': [
        'রেসিপি', 'খাবার', 'রান্না', 'খাবার', 'নাস্তা',
        'দুপুরের খাবার', 'রাতের খাবার', 'নিরামিষ'
    ],
    'gu': [
        'રેસિપી', 'ખોરાક', 'રાંધવું', 'વાનગી', 'નાસ્તો',
        'બપોરનું ભોજન', 'રાત્રિભોજન', 'શાકાહારી'
    ]
}


class EnhancedSTT:
    """
    Enhanced Speech-to-Text with Indian language optimization
    Uses Whisper + LLM post-processing for better accuracy
    """
    
    def __init__(self, use_llm: bool = True, llm_api_key: Optional[str] = None):
        self.use_llm = use_llm
        self.llm_api_key = llm_api_key
        self.whisper_model = None
        self.llm_client = None
        
        self._initialize_whisper()
        if use_llm and llm_api_key:
            self._initialize_llm()
    
    def _initialize_whisper(self):
        """Initialize Whisper model"""
        try:
            import whisper
            # Use medium model for better accuracy with Indian languages
            self.whisper_model = whisper.load_model("medium")
            logger.info("whisper_initialized", model="medium")
        except Exception as e:
            logger.error("whisper_initialization_failed", error=str(e))
            raise
    
    def _initialize_llm(self):
        """Initialize LLM client for post-processing"""
        try:
            import openai
            self.llm_client = openai.OpenAI(api_key=self.llm_api_key)
            logger.info("llm_initialized_for_stt", provider="openai")
        except Exception as e:
            logger.warning("llm_initialization_failed", error=str(e))
            self.use_llm = False
    
    def transcribe(
        self,
        audio_data: bytes,
        language: Optional[Language] = None,
        task: str = "transcribe"
    ) -> Tuple[str, float, Language]:
        """
        Transcribe audio with Indian language optimization
        
        Args:
            audio_data: Raw audio bytes (WAV, MP3, etc.)
            language: Expected language code (auto-detect if None)
            task: 'transcribe' or 'translate' (to English)
            
        Returns:
            (transcript, confidence, detected_language)
        """
        try:
            # Save audio to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name
            
            # Transcribe with Whisper
            options = {
                'task': task,
                'fp16': False  # Better for CPU
            }
            
            # Add language hint if provided
            if language and language in INDIAN_LANGUAGES:
                whisper_lang = INDIAN_LANGUAGES[language]['whisper_code']
                options['language'] = whisper_lang
                logger.info("transcribing_with_language_hint", language=language)
            
            # Add food context for better recognition
            if language and language in FOOD_CONTEXT_TERMS:
                context_terms = FOOD_CONTEXT_TERMS[language]
                options['initial_prompt'] = f"Food recipe query: {', '.join(context_terms[:5])}"
            
            # Transcribe
            result = self.whisper_model.transcribe(tmp_path, **options)
            
            transcript = result['text'].strip()
            detected_lang = result.get('language', 'en')
            
            # Calculate confidence from segment data
            segments = result.get('segments', [])
            if segments:
                avg_prob = sum(seg.get('no_speech_prob', 0.5) for seg in segments) / len(segments)
                confidence = 1.0 - avg_prob
            else:
                confidence = 0.8
            
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)
            
            logger.info(
                "whisper_transcribed",
                length=len(transcript),
                language=detected_lang,
                confidence=confidence
            )
            
            # Post-process with LLM for better accuracy
            if self.use_llm and self.llm_client:
                transcript = self._llm_postprocess(transcript, detected_lang)
            
            return transcript, confidence, detected_lang
            
        except Exception as e:
            logger.error("transcription_failed", error=str(e))
            raise
    
    def _llm_postprocess(self, transcript: str, language: str) -> str:
        """
        Post-process transcript with LLM for better accuracy
        Corrects food terminology and common misrecognitions
        """
        try:
            lang_name = INDIAN_LANGUAGES.get(language, {}).get('name', 'English')
            
            response = self.llm_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a food terminology expert. Correct transcription errors in {lang_name} food-related queries.

Fix:
1. Ingredient names (paneer, biryani, masala, etc.)
2. Cooking terms (tandoor, dum, tadka, etc.)
3. Common misrecognitions
4. Maintain original meaning
5. Keep it natural

Return ONLY the corrected text, nothing else."""
                    },
                    {
                        "role": "user",
                        "content": f"Correct this food query: {transcript}"
                    }
                ],
                temperature=0.2,
                max_tokens=200
            )
            
            corrected = response.choices[0].message.content.strip()
            
            if corrected and len(corrected) > 0:
                logger.info("llm_correction", original_length=len(transcript), corrected_length=len(corrected))
                return corrected
            
            return transcript
            
        except Exception as e:
            logger.warning("llm_postprocess_failed", error=str(e))
            return transcript
    
    def transcribe_from_base64(
        self,
        audio_base64: str,
        language: Optional[Language] = None,
        task: str = "transcribe"
    ) -> Tuple[str, float, Language]:
        """
        Convenience method to transcribe from base64-encoded audio
        
        Args:
            audio_base64: Base64-encoded audio data
            language: Expected language code
            task: 'transcribe' or 'translate'
            
        Returns:
            (transcript, confidence, detected_language)
        """
        audio_bytes = base64.b64decode(audio_base64)
        return self.transcribe(audio_bytes, language, task)
    
    def transcribe_file(
        self,
        file_path: str,
        language: Optional[Language] = None,
        task: str = "transcribe"
    ) -> Tuple[str, float, Language]:
        """
        Transcribe audio from file
        
        Args:
            file_path: Path to audio file
            language: Expected language code
            task: 'transcribe' or 'translate'
            
        Returns:
            (transcript, confidence, detected_language)
        """
        with open(file_path, 'rb') as f:
            audio_bytes = f.read()
        
        return self.transcribe(audio_bytes, language, task)


class MultichannelSTT:
    """
    Supports multiple STT providers with fallback
    OpenAI Whisper API, Local Whisper, Google Speech API
    """
    
    def __init__(
        self,
        primary_provider: str = "local_whisper",
        openai_key: Optional[str] = None,
        google_credentials: Optional[str] = None
    ):
        self.primary = primary_provider
        self.openai_key = openai_key
        self.google_credentials = google_credentials
        
        # Initialize providers
        if primary_provider == "local_whisper" or primary_provider == "enhanced":
            self.enhanced_stt = EnhancedSTT(use_llm=True, llm_api_key=openai_key)
        
        if openai_key:
            import openai
            self.openai_client = openai.OpenAI(api_key=openai_key)
        
        if google_credentials:
            self._initialize_google()
    
    def _initialize_google(self):
        """Initialize Google Speech API"""
        try:
            from google.cloud import speech
            self.google_client = speech.SpeechClient()
            logger.info("google_stt_initialized")
        except Exception as e:
            logger.warning("google_stt_initialization_failed", error=str(e))
    
    def transcribe(
        self,
        audio_data: bytes,
        language: Optional[Language] = None,
        provider: Optional[str] = None
    ) -> Tuple[str, float, Language]:
        """
        Transcribe with specified or primary provider
        
        Args:
            audio_data: Audio bytes
            language: Expected language
            provider: Override primary provider
            
        Returns:
            (transcript, confidence, language)
        """
        provider = provider or self.primary
        
        try:
            if provider == "local_whisper" or provider == "enhanced":
                return self.enhanced_stt.transcribe(audio_data, language)
            
            elif provider == "openai_api" and self.openai_key:
                return self._transcribe_openai_api(audio_data, language)
            
            elif provider == "google" and hasattr(self, 'google_client'):
                return self._transcribe_google(audio_data, language)
            
            else:
                logger.warning("provider_not_available", provider=provider, falling_back="enhanced")
                return self.enhanced_stt.transcribe(audio_data, language)
                
        except Exception as e:
            logger.error("transcription_failed", provider=provider, error=str(e))
            # Fallback to enhanced STT
            if provider != "enhanced":
                return self.enhanced_stt.transcribe(audio_data, language)
            raise
    
    def _transcribe_openai_api(
        self,
        audio_data: bytes,
        language: Optional[Language]
    ) -> Tuple[str, float, Language]:
        """Transcribe using OpenAI Whisper API"""
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name
        
        with open(tmp_path, 'rb') as audio_file:
            response = self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language if language and language in INDIAN_LANGUAGES else None
            )
        
        Path(tmp_path).unlink(missing_ok=True)
        
        transcript = response.text
        detected_lang = language or 'en'
        confidence = 0.9  # OpenAI API doesn't return confidence
        
        return transcript, confidence, detected_lang
    
    def _transcribe_google(
        self,
        audio_data: bytes,
        language: Optional[Language]
    ) -> Tuple[str, float, Language]:
        """Transcribe using Google Speech API"""
        from google.cloud import speech
        
        # Map our language codes to Google's
        google_lang = {
            'hi': 'hi-IN', 'mr': 'mr-IN', 'ta': 'ta-IN',
            'te': 'te-IN', 'bn': 'bn-IN', 'gu': 'gu-IN',
            'kn': 'kn-IN', 'ml': 'ml-IN', 'pa': 'pa-IN'
        }.get(language, 'en-US')
        
        audio = speech.RecognitionAudio(content=audio_data)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            language_code=google_lang,
            enable_automatic_punctuation=True,
            model='default'
        )
        
        response = self.google_client.recognize(config=config, audio=audio)
        
        if response.results:
            result = response.results[0]
            transcript = result.alternatives[0].transcript
            confidence = result.alternatives[0].confidence
            return transcript, confidence, language or 'en'
        
        return "", 0.0, language or 'en'


# Singleton instances
_enhanced_stt: Optional[EnhancedSTT] = None
_multichannel_stt: Optional[MultichannelSTT] = None


def get_enhanced_stt(use_llm: bool = True, api_key: Optional[str] = None) -> EnhancedSTT:
    """Get or create singleton Enhanced STT"""
    global _enhanced_stt
    if _enhanced_stt is None:
        _enhanced_stt = EnhancedSTT(use_llm=use_llm, llm_api_key=api_key)
    return _enhanced_stt


def get_multichannel_stt(
    primary: str = "enhanced",
    openai_key: Optional[str] = None,
    google_creds: Optional[str] = None
) -> MultichannelSTT:
    """Get or create singleton Multichannel STT"""
    global _multichannel_stt
    if _multichannel_stt is None:
        _multichannel_stt = MultichannelSTT(primary, openai_key, google_creds)
    return _multichannel_stt
