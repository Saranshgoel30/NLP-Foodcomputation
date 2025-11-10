"""
Speech-to-Text Adapter
Supports Whisper and Vosk for multilingual transcription
"""
import base64
import io
import structlog
from typing import Tuple
from .config import Settings
from .models import Language

logger = structlog.get_logger()


class STTAdapter:
    """Abstract STT adapter interface"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.provider = settings.stt_provider
    
    def transcribe(self, audio_base64: str, format: str = 'webm') -> Tuple[str, float, Language]:
        """
        Transcribe audio to text
        
        Args:
            audio_base64: Base64 encoded audio data
            format: Audio format (webm, wav, pcm)
            
        Returns:
            (transcript, confidence, detected_language)
        """
        raise NotImplementedError


class WhisperSTT(STTAdapter):
    """
    Production-grade Whisper STT implementation
    Supports multiple audio formats and Indian languages
    """
    
    # Language code mapping: Whisper -> ISO 639-1
    LANG_MAP = {
        'hindi': 'hi',
        'bengali': 'bn',
        'telugu': 'te',
        'marathi': 'mr',
        'tamil': 'ta',
        'gujarati': 'gu',
        'kannada': 'kn',
        'malayalam': 'ml',
        'odia': 'or',
        'punjabi': 'pa',
        'english': 'en'
    }
    
    def __init__(self, settings: Settings):
        super().__init__(settings)
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model with error handling"""
        try:
            import whisper
            import torch
            
            model_name = self.settings.stt_model_name or "base"
            
            # Check CUDA availability
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info("loading_whisper_model", model=model_name, device=device)
            
            self.model = whisper.load_model(model_name, device=device)
            
            logger.info(
                "whisper_model_loaded",
                model=model_name,
                device=device,
                supported_languages=len(whisper.tokenizer.LANGUAGES)
            )
        except ImportError as e:
            logger.error("whisper_not_installed", error=str(e))
            raise RuntimeError("Whisper library not installed. Run: pip install openai-whisper")
        except Exception as e:
            logger.error("failed_to_load_whisper", error=str(e))
            raise RuntimeError(f"Failed to load Whisper model: {str(e)}")
    
    def transcribe(self, audio_base64: str, format: str = 'webm') -> Tuple[str, float, str]:
        """
        Transcribe audio using Whisper with robust error handling
        
        Args:
            audio_base64: Base64 encoded audio data
            format: Audio format (webm, wav, mp3, ogg, m4a)
            
        Returns:
            (transcript, confidence, detected_language_code)
            
        Raises:
            ValueError: Invalid audio data
            RuntimeError: Transcription failed
        """
        if not self.model:
            raise RuntimeError("Whisper model not loaded")
        
        import tempfile
        import os
        
        tmp_path = None
        try:
            # Validate base64 input
            if not audio_base64:
                raise ValueError("Empty audio data")
            
            # Decode base64 audio
            try:
                audio_bytes = base64.b64decode(audio_base64)
            except Exception as e:
                raise ValueError(f"Invalid base64 audio data: {str(e)}")
            
            # Validate audio size (max 25MB)
            audio_size_mb = len(audio_bytes) / (1024 * 1024)
            if audio_size_mb > 25:
                raise ValueError(f"Audio file too large: {audio_size_mb:.1f}MB (max 25MB)")
            
            logger.info("transcribing_audio", size_mb=f"{audio_size_mb:.2f}", format=format)
            
            # Save to temporary file (Whisper requires file input)
            with tempfile.NamedTemporaryFile(suffix=f'.{format}', delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            
            # Transcribe with Whisper
            result = self.model.transcribe(
                tmp_path,
                language=None,  # Auto-detect language
                task='transcribe',
                fp16=False,  # Use FP32 for better accuracy
                verbose=False
            )
            
            # Extract transcript and clean it
            transcript = result['text'].strip()
            
            if not transcript:
                logger.warning("empty_transcription")
                return "", 0.0, "en"
            
            # Calculate average confidence from segments
            confidence = 0.9  # Default for Whisper (no direct confidence)
            if 'segments' in result and result['segments']:
                # Some Whisper versions provide no_speech_prob per segment
                seg_confidences = []
                for seg in result['segments']:
                    # Confidence = 1 - no_speech_probability
                    no_speech = seg.get('no_speech_prob', 0.1)
                    seg_confidences.append(1.0 - no_speech)
                
                if seg_confidences:
                    confidence = sum(seg_confidences) / len(seg_confidences)
            
            # Map language to ISO code
            detected_lang = result.get('language', 'en').lower()
            lang_code = self.LANG_MAP.get(detected_lang, detected_lang)
            
            logger.info(
                "transcription_complete",
                transcript_length=len(transcript),
                word_count=len(transcript.split()),
                confidence=f"{confidence:.2%}",
                detected_language=lang_code,
                audio_duration=result.get('duration', 0)
            )
            
            return transcript, confidence, lang_code
            
        except ValueError:
            raise  # Re-raise validation errors
        except Exception as e:
            logger.error("whisper_transcription_failed", error=str(e), error_type=type(e).__name__)
            raise RuntimeError(f"Transcription failed: {str(e)}")
        finally:
            # Always clean up temp file
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                    logger.debug("cleaned_temp_file", path=tmp_path)
                except Exception as e:
                    logger.warning("failed_to_cleanup_temp_file", path=tmp_path, error=str(e))


class VoskSTT(STTAdapter):
    """Vosk-based STT implementation"""
    
    def __init__(self, settings: Settings):
        super().__init__(settings)
        self.model = None
        self.recognizer = None
        self._load_model()
    
    def _load_model(self):
        """Load Vosk model"""
        try:
            from vosk import Model, KaldiRecognizer
            import json
            
            model_path = self.settings.stt_model_path
            if not model_path:
                raise ValueError("Vosk requires stt_model_path to be set")
            
            logger.info("loading_vosk_model", path=model_path)
            self.model = Model(model_path)
            logger.info("vosk_model_loaded")
        except Exception as e:
            logger.error("failed_to_load_vosk", error=str(e))
            raise
    
    def transcribe(self, audio_base64: str, format: str = 'webm') -> Tuple[str, float, Language]:
        """Transcribe using Vosk"""
        if not self.model:
            raise RuntimeError("Vosk model not loaded")
        
        try:
            from vosk import KaldiRecognizer
            import json
            import wave
            
            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_base64)
            
            # Convert to WAV if needed (Vosk expects WAV)
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                if format != 'wav':
                    # Convert using pydub or similar
                    # For now, assume WAV input
                    pass
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            
            # Open WAV file
            wf = wave.open(tmp_path, "rb")
            rec = KaldiRecognizer(self.model, wf.getframerate())
            
            # Process audio
            results = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    if 'text' in result:
                        results.append(result['text'])
            
            # Get final result
            final_result = json.loads(rec.FinalResult())
            if 'text' in final_result:
                results.append(final_result['text'])
            
            transcript = ' '.join(results).strip()
            confidence = 0.85  # Vosk doesn't provide confidence easily
            detected_lang = 'en'  # Vosk requires language-specific models
            
            # Clean up
            wf.close()
            import os
            os.unlink(tmp_path)
            
            logger.info(
                "vosk_transcribed",
                transcript_length=len(transcript),
                confidence=confidence
            )
            
            return transcript, confidence, detected_lang
            
        except Exception as e:
            logger.error("vosk_transcription_failed", error=str(e))
            raise


def get_stt_adapter(settings: Settings) -> STTAdapter:
    """Factory function to get appropriate STT adapter"""
    if settings.stt_provider == 'whisper':
        return WhisperSTT(settings)
    elif settings.stt_provider == 'vosk':
        return VoskSTT(settings)
    else:
        raise ValueError(f"Unknown STT provider: {settings.stt_provider}")
