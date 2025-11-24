"""
OpenAI Whisper Speech-to-Text Service
Provides multilingual voice transcription for recipe search queries
Supports 99 languages including Hindi, Tamil, Bengali, Urdu, etc.
"""

import os
import time
import hashlib
from typing import Dict, Optional, Tuple
import httpx
from dotenv import load_dotenv

load_dotenv()


class WhisperService:
    """
    Enterprise-grade Whisper API integration for speech-to-text
    
    Features:
    - Multilingual transcription (99 languages)
    - Response caching to reduce API costs
    - Automatic language detection
    - Cost tracking and monitoring
    - Fallback error handling
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.api_url = "https://api.openai.com/v1/audio/transcriptions"
        self.model = "whisper-1"
        
        # Cost tracking: $0.006 per minute of audio
        self.cost_per_minute = 0.006
        self.total_cost = 0.0
        self.total_requests = 0
        self.total_duration = 0.0  # in minutes
        
        # Response cache (1-hour TTL)
        self.cache: Dict[str, Tuple[Dict, float]] = {}
        self.cache_ttl = 3600  # 1 hour
        
        print("🎤 Whisper Service initialized")
        print(f"   Model: {self.model}")
        print(f"   Cost: ${self.cost_per_minute} per minute")
    
    def _get_cache_key(self, audio_data: bytes) -> str:
        """Generate cache key from audio data hash"""
        return hashlib.md5(audio_data).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Retrieve cached transcription if not expired"""
        if cache_key in self.cache:
            result, timestamp = self.cache[cache_key]
            age = time.time() - timestamp
            if age < self.cache_ttl:
                print(f"   💾 Cache hit (age: {age:.0f}s)")
                return result
            else:
                # Expired, remove from cache
                del self.cache[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, result: Dict):
        """Store transcription result in cache"""
        self.cache[cache_key] = (result, time.time())
    
    def _estimate_duration(self, audio_size_bytes: int) -> float:
        """
        Estimate audio duration in minutes from file size
        Rough estimate: 1 MB ≈ 1 minute for typical speech audio (varies by format/bitrate)
        """
        mb_size = audio_size_bytes / (1024 * 1024)
        estimated_minutes = mb_size * 1.0  # Conservative estimate
        return max(0.01, estimated_minutes)  # Minimum 0.01 minutes
    
    async def transcribe(
        self, 
        audio_file: bytes, 
        filename: str = "audio.webm",
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> Dict:
        """
        Transcribe audio to text using OpenAI Whisper API
        
        Args:
            audio_file: Audio file bytes (supports mp3, mp4, mpeg, mpga, m4a, wav, webm)
            filename: Original filename (helps with format detection)
            language: Optional ISO-639-1 language code (e.g., 'en', 'hi', 'ta')
                     If not provided, Whisper will auto-detect
            prompt: Optional text prompt to guide transcription (e.g., food-related terms)
        
        Returns:
            Dict with:
                - text: Transcribed text
                - language: Detected language code
                - duration: Estimated audio duration in minutes
                - cost: Estimated cost in USD
                - cached: Whether result was from cache
        """
        start_time = time.time()
        
        # Check cache first
        cache_key = self._get_cache_key(audio_file)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return {**cached_result, "cached": True}
        
        # Estimate duration for cost calculation
        estimated_duration = self._estimate_duration(len(audio_file))
        estimated_cost = estimated_duration * self.cost_per_minute
        
        print(f"\n🎤 Whisper Transcription:")
        print(f"   File: {filename} ({len(audio_file) / 1024:.1f} KB)")
        print(f"   Estimated duration: {estimated_duration:.2f} minutes")
        print(f"   Estimated cost: ${estimated_cost:.6f}")
        
        try:
            # Prepare multipart form data
            files = {
                "file": (filename, audio_file, self._get_mime_type(filename))
            }
            
            data = {
                "model": self.model,
                "response_format": "json"
            }
            
            # Add optional parameters
            if language:
                data["language"] = language
                print(f"   Language hint: {language}")
            
            # Food-specific prompt to improve accuracy
            if prompt is None:
                prompt = (
                    "This is a food recipe search query. "
                    "It may contain dish names, ingredients, or cooking terms in multiple languages."
                )
            data["prompt"] = prompt
            
            # Make API request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    files=files,
                    data=data
                )
            
            # Handle response
            if response.status_code != 200:
                error_detail = response.text
                print(f"   ❌ Whisper API error: {response.status_code}")
                print(f"      {error_detail}")
                raise Exception(f"Whisper API error: {response.status_code} - {error_detail}")
            
            result = response.json()
            transcribed_text = result.get("text", "").strip()
            
            # Update tracking
            self.total_requests += 1
            self.total_duration += estimated_duration
            self.total_cost += estimated_cost
            
            elapsed = time.time() - start_time
            
            print(f"   ✅ Transcribed: '{transcribed_text}'")
            print(f"   ⏱️  Duration: {elapsed:.2f}s")
            print(f"   💰 Cost: ${estimated_cost:.6f} | Total: ${self.total_cost:.4f} ({self.total_requests} requests)")
            
            # Prepare result
            result_data = {
                "text": transcribed_text,
                "language": result.get("language", "unknown"),
                "duration_minutes": estimated_duration,
                "cost_usd": estimated_cost,
                "processing_time_seconds": elapsed,
                "cached": False
            }
            
            # Cache result
            self._cache_result(cache_key, result_data)
            
            return result_data
            
        except httpx.TimeoutException:
            print("   ❌ Whisper API timeout")
            raise Exception("Whisper API timeout - audio file may be too large")
        except Exception as e:
            print(f"   ❌ Whisper error: {str(e)}")
            raise
    
    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type from filename extension"""
        ext = filename.lower().split('.')[-1]
        mime_types = {
            "mp3": "audio/mpeg",
            "mp4": "audio/mp4",
            "mpeg": "audio/mpeg",
            "mpga": "audio/mpeg",
            "m4a": "audio/m4a",
            "wav": "audio/wav",
            "webm": "audio/webm",
            "ogg": "audio/ogg"
        }
        return mime_types.get(ext, "application/octet-stream")
    
    def get_stats(self) -> Dict:
        """Get service statistics"""
        return {
            "total_requests": self.total_requests,
            "total_duration_minutes": round(self.total_duration, 2),
            "total_cost_usd": round(self.total_cost, 4),
            "cache_size": len(self.cache),
            "average_cost_per_request": round(self.total_cost / max(1, self.total_requests), 6)
        }
    
    def clear_cache(self):
        """Clear transcription cache"""
        cache_size = len(self.cache)
        self.cache.clear()
        print(f"🗑️  Cleared Whisper cache ({cache_size} entries)")


# Global service instance
whisper_service = WhisperService()
