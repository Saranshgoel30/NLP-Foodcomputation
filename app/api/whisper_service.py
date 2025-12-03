"""
OpenAI Whisper Speech-to-Text Service 
Optimized for Indian vernacular dishes, noisy environments, and multilingual queries
"""

import os
import time
import hashlib
import json
from typing import Dict, Optional, Tuple, List
import httpx
from dotenv import load_dotenv
from difflib import get_close_matches

load_dotenv()


class WhisperService:
    """
    Enterprise-grade Whisper API integration for speech-to-text
    ENHANCED with Indian food vocabulary and fuzzy correction
    
    Features:
    - Multilingual transcription (99 languages)
    - Indian food vocabulary injection
    - Fuzzy matching for dish name correction
    - Response caching to reduce API costs
    - Automatic language detection
    - Noisy audio handling
    """
    
    # CRITICAL: Comprehensive Indian food vocabulary for Whisper prompt
    INDIAN_FOOD_VOCABULARY = [
        # Popular North Indian dishes
        "paneer tikka", "butter chicken", "dal makhani", "chole bhature", 
        "aloo gobi", "palak paneer", "rajma", "kadai paneer", "malai kofta",
        "naan", "roti", "paratha", "kulcha", "bhatura",
        
        # South Indian dishes
        "dosa", "idli", "vada", "sambhar", "rasam", "uttapam", "pongal",
        "upma", "medu vada", "masala dosa", "rava dosa", "set dosa",
        
        # Rice dishes
        "biryani", "pulao", "khichdi", "curd rice", "lemon rice", "tamarind rice",
        "hyderabadi biryani", "lucknowi biryani", "vegetable pulao",
        
        # Snacks & Street Food
        "samosa", "pakora", "bhaji", "pav bhaji", "vada pav", "chaat",
        "aloo tikki", "dahi vada", "kachori", "jalebi", "dhokla",
        
        # Curries & Gravies
        "curry", "sabzi", "sabji", "kuzhambu", "koora", "bhaji",
        "aloo curry", "tomato curry", "egg curry", "chicken curry",
        
        # Sweets
        "gulab jamun", "rasgulla", "kheer", "halwa", "laddu", "barfi",
        "payasam", "shrikhand", "rabri", "kulfi",
        
        # Common ingredients (for "X without Y" queries)
        "onion", "garlic", "tomato", "potato", "paneer", "chicken",
        "mutton", "fish", "prawn", "mushroom", "capsicum",
        
        # Vernacular terms
        "pyaz", "lahsun", "aloo", "tamatar", "mirch", "haldi",
        "jeera", "dhaniya", "kanda", "batata", "vengayam",
        
        # Cooking styles
        "tandoori", "masala", "makhani", "kadai", "tawa", "dum",
        
        # Dietary terms
        "jain", "vegan", "vegetarian", "satvik", "no onion", "no garlic"
    ]
    
    # Common transcription errors and corrections
    COMMON_CORRECTIONS = {
        # Phonetic variations
        "panel": "paneer",
        "panir": "paneer",
        "panner": "paneer",
        "doser": "dosa",
        "dosai": "dosa",
        "idly": "idli",
        "wada": "vada",
        "biriyani": "biryani",
        "pulav": "pulao",
        "poori": "puri",
        "rotti": "roti",
        "chapathi": "chapati",
        "aalu": "aloo",
        "alu": "aloo",
        "pyaaz": "pyaz",
        "piyaz": "pyaz",
        "lasan": "lahsun",
        "lasun": "lahsun",
        "tamater": "tamatar",
        "tomater": "tamatar",
        
        # Common mishearings
        "better chicken": "butter chicken",
        "dollar": "dal",
        "doll": "dal",
        "cholay": "chole",
        "chole bhatura": "chole bhature",
        "power": "palak",
        "malai coffee": "malai kofta",
        
        # Negation corrections
        "no onions": "no onion",
        "without onions": "without onion",
        "no garlics": "no garlic",
        "without garlics": "without garlic",
    }
    
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
        
        # Load knowledge graph vocabulary (if available)
        self.knowledge_graph_dishes = self._load_knowledge_graph_vocabulary()
        
        print("🎤 Whisper Service initialized (ENHANCED)")
        print(f"   Model: {self.model}")
        print(f"   Cost: ${self.cost_per_minute} per minute")
        print(f"   Food vocabulary: {len(self.INDIAN_FOOD_VOCABULARY)} terms")
        print(f"   Knowledge graph dishes: {len(self.knowledge_graph_dishes)} loaded")
    
    def _load_knowledge_graph_vocabulary(self) -> List[str]:
        """
        Load dish names from your knowledge graph/database
        This helps with fuzzy matching against actual available recipes
        """
        try:
            # Try to load from a vocabulary file (you can generate this from your DB)
            vocab_path = os.path.join(os.path.dirname(__file__), "nlp_data", "dish_vocabulary.json")
            if os.path.exists(vocab_path):
                with open(vocab_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"   ⚠️  Could not load knowledge graph vocabulary: {e}")
        
        # Fallback: return empty list (fuzzy matching will use INDIAN_FOOD_VOCABULARY)
        return []
    
    def _generate_food_prompt(self, language_hint: Optional[str] = None) -> str:
        """
        Generate context-rich prompt for Whisper with food vocabulary
        This DRAMATICALLY improves accuracy for food-related queries
        """
        # Base prompt with common dish names (helps Whisper recognize them)
        prompt_parts = [
            "Recipe search query with Indian dishes:",
            ", ".join(self.INDIAN_FOOD_VOCABULARY[:50])  # First 50 terms
        ]
        
        # Add language-specific context
        if language_hint == "hi":
            prompt_parts.append("Hindi food terms: pyaz, lahsun, aloo, tamatar, sabzi, dal, roti, paneer")
        elif language_hint == "ta":
            prompt_parts.append("Tamil food terms: vengayam, thakkali, dosa, idli, sambhar, rasam")
        elif language_hint == "te":
            prompt_parts.append("Telugu food terms: ullipaya, tamata, biryani, koora, vada")
        elif language_hint == "ml":
            prompt_parts.append("Malayalam food terms: ulli, thakkali, dosa, idli, payasam")
        elif language_hint == "kn":
            prompt_parts.append("Kannada food terms: eerulli, tomato, dosa, idli, vada")
        elif language_hint == "bn":
            prompt_parts.append("Bengali food terms: piyaj, aalu, rasgulla, mishti")
        
        # Common query patterns
        prompt_parts.append("Common phrases: without onion, no garlic, quick recipe, spicy, healthy")
        
        return " ".join(prompt_parts)
    
    def _apply_fuzzy_correction(self, text: str) -> Tuple[str, List[str]]:
        """
        Apply fuzzy matching to correct common transcription errors
        Returns: (corrected_text, list_of_corrections_applied)
        """
        corrected = text
        corrections_applied = []
        
        # Step 1: Direct replacements from COMMON_CORRECTIONS
        for wrong, right in self.COMMON_CORRECTIONS.items():
            if wrong.lower() in corrected.lower():
                corrected = corrected.replace(wrong, right)
                corrected = corrected.replace(wrong.capitalize(), right.capitalize())
                corrected = corrected.replace(wrong.upper(), right.upper())
                corrections_applied.append(f"{wrong} → {right}")
        
        # Step 2: Fuzzy match individual words against vocabulary
        words = corrected.split()
        corrected_words = []
        
        for word in words:
            word_lower = word.lower()
            
            # Skip short words and common words
            if len(word_lower) < 4 or word_lower in ['with', 'without', 'quick', 'spicy']:
                corrected_words.append(word)
                continue
            
            # Try fuzzy matching against food vocabulary
            all_vocab = self.INDIAN_FOOD_VOCABULARY + self.knowledge_graph_dishes
            matches = get_close_matches(word_lower, 
                                       [v.lower() for v in all_vocab], 
                                       n=1, 
                                       cutoff=0.75)  # 75% similarity threshold
            
            if matches:
                # Find the original case version
                matched_word = next((v for v in all_vocab if v.lower() == matches[0]), matches[0])
                if matched_word.lower() != word_lower:
                    corrected_words.append(matched_word)
                    corrections_applied.append(f"{word} → {matched_word}")
                else:
                    corrected_words.append(word)
            else:
                corrected_words.append(word)
        
        corrected = " ".join(corrected_words)
        
        return corrected, corrections_applied
    
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
        prompt: Optional[str] = None,
        enable_fuzzy_correction: bool = True
    ) -> Dict:
        """
        Transcribe audio to text using OpenAI Whisper API
        ENHANCED with Indian food vocabulary and fuzzy correction
        
        Args:
            audio_file: Audio file bytes (supports mp3, mp4, mpeg, mpga, m4a, wav, webm)
            filename: Original filename (helps with format detection)
            language: Optional ISO-639-1 language code (e.g., 'en', 'hi', 'ta')
                     If None, Whisper will auto-detect (recommended for Indian languages)
            prompt: Optional custom prompt (if None, uses food-optimized prompt)
            enable_fuzzy_correction: Apply fuzzy matching to correct errors (default: True)
        
        Returns:
            Dict with:
                - text: Transcribed text (corrected)
                - raw_text: Original transcription before correction
                - corrections_applied: List of corrections made
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
        
        print(f"\n🎤 Whisper Transcription (ENHANCED):")
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
            
            # CRITICAL: Language handling
            # For Indian accents, auto-detection often works better than forcing English
            # But we can provide a hint
            if language:
                data["language"] = language
                print(f"   Language hint: {language}")
            else:
                print(f"   Language: auto-detect (recommended for Indian languages)")
            
            # CRITICAL: Use food-optimized prompt
            if prompt is None:
                prompt = self._generate_food_prompt(language)
            
            data["prompt"] = prompt
            print(f"   Prompt length: {len(prompt)} chars")
            
            # Make API request with better error handling
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
            raw_transcription = result.get("text", "").strip()
            
            # Apply fuzzy correction
            corrected_text = raw_transcription
            corrections_applied = []
            
            if enable_fuzzy_correction:
                corrected_text, corrections_applied = self._apply_fuzzy_correction(raw_transcription)
                
                if corrections_applied:
                    print(f"   🔧 Applied {len(corrections_applied)} corrections:")
                    for correction in corrections_applied:
                        print(f"      • {correction}")
            
            # Update tracking
            self.total_requests += 1
            self.total_duration += estimated_duration
            self.total_cost += estimated_cost
            
            elapsed = time.time() - start_time
            
            print(f"   ✅ Raw: '{raw_transcription}'")
            if corrected_text != raw_transcription:
                print(f"   ✅ Corrected: '{corrected_text}'")
            print(f"   🌍 Language: {result.get('language', 'unknown')}")
            print(f"   ⏱️  Duration: {elapsed:.2f}s")
            print(f"   💰 Cost: ${estimated_cost:.6f} | Total: ${self.total_cost:.4f} ({self.total_requests} requests)")
            
            # Prepare result
            result_data = {
                "text": corrected_text,
                "raw_text": raw_transcription,
                "corrections_applied": corrections_applied,
                "language": result.get("language", "unknown"),
                "duration_minutes": estimated_duration,
                "cost_usd": estimated_cost,
                "processing_time_seconds": elapsed,
                "cached": False
            }
            
            # Cache result
            self._cache_result(cache_key, result_data)
            
            return result_data
            
        except httpx.ConnectError as e:
            print(f"   ❌ Network connection failed: {str(e)}")
            error_msg = (
                "Cannot connect to OpenAI API. Possible causes:\n"
                "1. No internet connection\n"
                "2. Firewall/Proxy blocking api.openai.com\n"
                "3. DNS resolution issues\n"
                "4. VPN interference\n\n"
                "Try: Check your internet connection and firewall settings"
            )
            raise Exception(error_msg)
        except httpx.TimeoutException:
            print("   ❌ Whisper API timeout")
            raise Exception("Whisper API timeout - audio file may be too large or slow connection")
        except httpx.HTTPStatusError as e:
            print(f"   ❌ HTTP error: {e.response.status_code}")
            raise Exception(f"Whisper API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"   ❌ Whisper error: {str(e)}")
            # Provide more helpful error message for common issues
            if "getaddrinfo failed" in str(e) or "11001" in str(e):
                raise Exception(
                    "DNS resolution failed for api.openai.com. "
                    "Check your internet connection, DNS settings, or try using a different network."
                )
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
            "average_cost_per_request": round(self.total_cost / max(1, self.total_requests), 6),
            "vocabulary_size": len(self.INDIAN_FOOD_VOCABULARY),
            "knowledge_graph_dishes": len(self.knowledge_graph_dishes)
        }
    
    def clear_cache(self):
        """Clear transcription cache"""
        cache_size = len(self.cache)
        self.cache.clear()
        print(f"🗑️  Cleared Whisper cache ({cache_size} entries)")
    
    def add_vocabulary(self, terms: List[str]):
        """
        Dynamically add new food terms to vocabulary
        Useful for adding new dishes from your knowledge graph
        """
        new_terms = [term for term in terms if term not in self.INDIAN_FOOD_VOCABULARY]
        self.INDIAN_FOOD_VOCABULARY.extend(new_terms)
        print(f"📚 Added {len(new_terms)} new terms to vocabulary")


# Global service instance
whisper_service = WhisperService()