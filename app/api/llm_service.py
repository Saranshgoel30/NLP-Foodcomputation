"""
LLM-Powered Query Understanding Service
Uses DeepSeek or other LLMs for intelligent recipe search
"""

import json
import os
from typing import Dict, List, Optional, Any
import httpx
from datetime import datetime, timedelta
import hashlib
from functools import lru_cache

from .llm_config import LLMConfig, LLMProvider, SYSTEM_PROMPTS, EXAMPLE_QUERIES


class LLMService:
    """
    LLM Service for intelligent query understanding and translation
    Supports multiple providers with automatic fallback
    """
    
    def __init__(self):
        self.provider = LLMConfig.get_available_provider()
        if not self.provider:
            print("⚠️  No LLM API key found. Using rule-based fallback.")
            print("   Set DEEPSEEK_API_KEY, OPENAI_API_KEY, or GROQ_API_KEY for enhanced features.")
        else:
            config = LLMConfig.get_config(self.provider)
            print(f"✅ LLM Service initialized with {self.provider.value} ({config['model']})")
        
        # Cache for translations and interpretations (1 hour TTL)
        self._cache = {}
        self._cache_ttl = 3600  # 1 hour
    
    def _get_cache_key(self, text: str, task: str) -> str:
        """Generate cache key for text and task"""
        return hashlib.md5(f"{task}:{text}".encode()).hexdigest()
    
    def _get_cached(self, cache_key: str) -> Optional[Any]:
        """Get cached result if not expired"""
        if cache_key in self._cache:
            result, timestamp = self._cache[cache_key]
            if datetime.now().timestamp() - timestamp < self._cache_ttl:
                return result
            else:
                del self._cache[cache_key]
        return None
    
    def _set_cache(self, cache_key: str, result: Any):
        """Cache result with timestamp"""
        self._cache[cache_key] = (result, datetime.now().timestamp())
    
    async def _call_llm(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> Optional[str]:
        """Call LLM API with fallback support"""
        if not self.provider:
            return None
        
        config = LLMConfig.get_config(self.provider)
        api_key = LLMConfig.get_api_key(self.provider)
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": config["model"],
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{config['api_base']}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    print(f"❌ LLM API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            print(f"❌ LLM API call failed: {str(e)}")
            return None
    
    async def understand_query(self, query: str) -> Dict[str, Any]:
        """
        Use LLM to understand user query intent and extract structured information
        Falls back to rule-based parsing if LLM unavailable
        """
        # Check cache first
        cache_key = self._get_cache_key(query, "understand")
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        if not self.provider:
            # Fallback to rule-based parsing
            return self._rule_based_understanding(query)
        
        # Build prompt with few-shot examples
        examples_text = "\n\n".join([
            f"Example {i+1}:\nQuery: \"{ex['query']}\"\nResponse: {json.dumps(ex['response'], indent=2)}"
            for i, ex in enumerate(EXAMPLE_QUERIES["query_understanding"])
        ])
        
        user_prompt = f"""Analyze this recipe search query and return structured JSON:

Query: "{query}"

Examples for reference:
{examples_text}

Now analyze the given query and return JSON with the same structure."""
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPTS["query_understanding"]},
            {"role": "user", "content": user_prompt}
        ]
        
        response = await self._call_llm(messages, temperature=0.2)
        
        if response:
            try:
                # Extract JSON from response (handle markdown code blocks)
                response_clean = response.strip()
                if response_clean.startswith("```json"):
                    response_clean = response_clean[7:]
                if response_clean.startswith("```"):
                    response_clean = response_clean[3:]
                if response_clean.endswith("```"):
                    response_clean = response_clean[:-3]
                
                result = json.loads(response_clean.strip())
                
                # Cache successful result
                self._set_cache(cache_key, result)
                
                return result
            except json.JSONDecodeError as e:
                print(f"⚠️  Failed to parse LLM response: {e}")
                print(f"Response was: {response}")
                return self._rule_based_understanding(query)
        
        return self._rule_based_understanding(query)
    
    async def translate_query(self, query: str, target_language: str = "English", custom_prompt: str = None) -> str:
        """
        Translate query to target language with food context preservation
        
        Args:
            query: The query to translate
            target_language: Target language for translation
            custom_prompt: Optional custom prompt with better context
        """
        # Check cache
        cache_key = self._get_cache_key(f"{query}:{target_language}", "translate")
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        if not self.provider:
            return query  # No translation without LLM
        
        # Use custom prompt if provided, otherwise use default
        if custom_prompt:
            user_prompt = custom_prompt
            messages = [
                {"role": "user", "content": user_prompt}
            ]
        else:
            user_prompt = f"""Translate this recipe query to {target_language}.
Preserve ingredient names and provide alternatives in parentheses.

Query: "{query}"

Target Language: {target_language}

Return only the translated text, nothing else."""
            
            messages = [
                {"role": "system", "content": SYSTEM_PROMPTS["translation"]},
                {"role": "user", "content": user_prompt}
            ]
        
        response = await self._call_llm(messages, temperature=0.2)
        
        if response:
            translated = response.strip()
            self._set_cache(cache_key, translated)
            return translated
        
        return query
    
    async def extract_ingredients(self, query: str) -> Dict[str, List[str]]:
        """
        Extract ingredients from query using LLM understanding
        """
        # Check cache
        cache_key = self._get_cache_key(query, "ingredients")
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        if not self.provider:
            return {"included": [], "excluded": [], "implied": []}
        
        user_prompt = f"""Extract all ingredients from this recipe query:

Query: "{query}"

Consider:
1. Explicit ingredients mentioned
2. Ingredients implied by cooking methods or dish names
3. Negative ingredients (without X, no Y)
4. Dietary restrictions (jain = no onion/garlic, vegan = no dairy/eggs)

Return JSON with "included", "excluded", "implied", and "dietary_context" lists."""
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPTS["ingredient_extraction"]},
            {"role": "user", "content": user_prompt}
        ]
        
        response = await self._call_llm(messages, temperature=0.2)
        
        if response:
            try:
                # Clean and parse response
                response_clean = response.strip()
                if response_clean.startswith("```json"):
                    response_clean = response_clean[7:]
                if response_clean.startswith("```"):
                    response_clean = response_clean[3:]
                if response_clean.endswith("```"):
                    response_clean = response_clean[:-3]
                
                result = json.loads(response_clean.strip())
                self._set_cache(cache_key, result)
                return result
            except json.JSONDecodeError:
                pass
        
        return {"included": [], "excluded": [], "implied": [], "dietary_context": ""}
    
    def _rule_based_understanding(self, query: str) -> Dict[str, Any]:
        """
        Fallback rule-based query understanding
        Used when LLM is unavailable
        """
        query_lower = query.lower()
        
        # Basic pattern matching
        excluded = []
        required = []
        
        # Check for exclusions
        if "without" in query_lower or "no " in query_lower or "bina" in query_lower:
            # Simple extraction (this is where LLM shines!)
            if "onion" in query_lower or "pyaz" in query_lower:
                excluded.append("onion")
            if "garlic" in query_lower or "lahsun" in query_lower:
                excluded.append("garlic")
            if "tomato" in query_lower or "tamatar" in query_lower:
                excluded.append("tomato")
        
        # Detect Jain restrictions
        if "jain" in query_lower:
            excluded.extend(["onion", "garlic", "potato", "root vegetables"])
        
        return {
            "intent": "search",
            "dish_name": query,
            "excluded_ingredients": excluded,
            "required_ingredients": required,
            "dietary_preferences": [],
            "cooking_time": None,
            "cuisine_type": None,
            "spice_level": None,
            "translated_query": query,
            "language_detected": "Unknown"
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            "provider": self.provider.value if self.provider else "None",
            "cache_size": len(self._cache),
            "model": LLMConfig.get_config(self.provider)["model"] if self.provider else "N/A"
        }


# Global instance
llm_service = LLMService()
