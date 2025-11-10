"""
Speech-to-Text Adapter
Supports Whisper and Vosk for multilingual transcription
"""
import base64
import io
import structlog
from typing import Tuple
from config import Settings
from models import Language

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
    """Whisper-based STT implementation"""
    
    def __init__(self, settings: Settings):
        super().__init__(settings)
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model"""
        try:
            import whisper
            model_name = self.settings.stt_model_name
            logger.info("loading_whisper_model", model=model_name)
            self.model = whisper.load_model(model_name)
            logger.info("whisper_model_loaded", model=model_name)
        except Exception as e:
            logger.error("failed_to_load_whisper", error=str(e))
            raise
    
    def transcribe(self, audio_base64: str, format: str = 'webm') -> Tuple[str, float, Language]:
        """Transcribe using Whisper"""
        if not self.model:
            raise RuntimeError("Whisper model not loaded")
        
        try:
            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_base64)
            
            # Save to temporary file (Whisper works with files)
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=f'.{format}', delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            
            # Transcribe
            result = self.model.transcribe(
                tmp_path,
                language=None,  # Auto-detect
                task='transcribe'
            )
            
            transcript = result['text'].strip()
            # Whisper doesn't provide confidence, use segments average if available
            confidence = 0.9  # Default high confidence for Whisper
            if 'segments' in result and result['segments']:
                confidences = [seg.get('confidence', 0.9) for seg in result['segments']]
                confidence = sum(confidences) / len(confidences)
            
            detected_lang = result.get('language', 'en')
            
            # Clean up temp file
            import os
            os.unlink(tmp_path)
            
            logger.info(
                "whisper_transcribed",
                transcript_length=len(transcript),
                confidence=confidence,
                language=detected_lang
            )
            
            return transcript, confidence, detected_lang
            
        except Exception as e:
            logger.error("whisper_transcription_failed", error=str(e))
            raise


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
