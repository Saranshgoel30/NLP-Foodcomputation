"""
Production-Grade LLM Service for Food Intelligence Platform
Supports DeepSeek (primary), xAI Grok (validation), with intelligent fallback
Optimized for recipe search, translation, and multilingual understanding
"""

import json
import os
from typing import Dict, List, Optional, Any, Tuple
import httpx
import asyncio
from datetime import datetime
import hashlib

from .llm_config import LLMConfig, LLMProvider, SYSTEM_PROMPTS, EXAMPLE_QUERIES


class LLMService:
    """
    Enterprise-grade LLM Service with:
    - Multi-provider support (DeepSeek, Grok, OpenAI)
    - Intelligent fallback and error handling
    - Response caching (1-hour TTL)
    - Cross-validation mode (compare providers)
    - Cost tracking and optimization
    """
    
    def __init__(self):
        self.primary_provider = LLMConfig.get_available_provider()
        self.all_providers = LLMConfig.get_all_available_providers()
        self.failed_providers = set()  # Track failed providers this session
        
        # Response cache (in-memory, 1 hour TTL)
        self._cache = {}
        self._cache_ttl = 3600  # 1 hour
        
        # Cost tracking
        self.total_cost = 0.0
        self.request_count = 0
        
        # Feature flags from environment
        self.enable_comparison = os.getenv("ENABLE_LLM_COMPARISON", "false").lower() == "true"
        
        if not self.primary_provider:
            print("⚠️  WARNING: No LLM API keys found!")
            print("   Set DEEPSEEK_API_KEY or XAI_API_KEY in .env for enhanced features")
            print("   System will fall back to rule-based parsing")
        else:
            provider_info = LLMConfig.get_provider_info(self.primary_provider)
            print(f"✅ LLM Service initialized")
            print(f"   Primary: {provider_info}")
            
            if len(self.all_providers) > 1:
                print(f"   Available fallbacks: {[p.value for p in self.all_providers[1:]]}")
                if self.enable_comparison:
                    print(f"   🔬 Comparison mode ENABLED - will validate with {self.all_providers[1].value}")
    
    # =========================================================================
    # CACHE MANAGEMENT
    # =========================================================================
    
    def _get_cache_key(self, text: str, task: str, provider: str = "") -> str:
        """Generate cache key for text, task, and provider"""
        key_str = f"{task}:{provider}:{text}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cached(self, cache_key: str) -> Optional[Any]:
        """Get cached result if not expired"""
        if cache_key in self._cache:
            result, timestamp = self._cache[cache_key]
            age = datetime.now().timestamp() - timestamp
            if age < self._cache_ttl:
                print(f"   💾 Cache hit (age: {int(age)}s)")
                return result
            else:
                del self._cache[cache_key]
        return None
    
    def _set_cache(self, cache_key: str, result: Any):
        """Cache result with timestamp"""
        self._cache[cache_key] = (result, datetime.now().timestamp())
    
    def clear_cache(self):
        """Clear all cached responses"""
        self._cache.clear()
        print("🧹 Cache cleared")
    
    # =========================================================================
    # CORE LLM API CALLS
    # =========================================================================
    
    async def _call_llm(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.2,
        max_tokens: int = 4000,
        provider: Optional[LLMProvider] = None,
        retry_with_fallback: bool = True
    ) -> Optional[str]:
        """
        Call LLM API with automatic fallback
        
        Args:
            messages: Chat messages in OpenAI format
            temperature: Sampling temperature (lower = more deterministic)
            max_tokens: Maximum response tokens
            provider: Specific provider to use (None = use primary)
            retry_with_fallback: Try other providers if primary fails
        
        Returns:
            LLM response text or None if all providers fail
        """
        if not provider:
            provider = self.primary_provider
        
        if not provider:
            return None
        
        # Try primary/specified provider first
        result = await self._try_provider(provider, messages, temperature, max_tokens)
        
        if result is not None:
            return result
        
        # Fallback to other providers if enabled
        if retry_with_fallback:
            print(f"   🔄 Trying fallback providers...")
            for fallback_provider in self.all_providers:
                # Skip already failed providers and current provider
                if fallback_provider == provider or fallback_provider in self.failed_providers:
                    continue
                
                print(f"   → Attempting {fallback_provider.value}...")
                result = await self._try_provider(fallback_provider, messages, temperature, max_tokens)
                
                if result is not None:
                    print(f"   ✅ Fallback successful: {fallback_provider.value}")
                    # Update primary provider for future requests
                    self.primary_provider = fallback_provider
                    return result
                else:
                    self.failed_providers.add(fallback_provider)
        
        print("   ❌ All LLM providers failed")
        return None
    
    async def _try_provider(
        self,
        provider: LLMProvider,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> Optional[str]:
        """
        Try calling a specific LLM provider
        
        Returns response text or None on failure
        """
        try:
            config = LLMConfig.get_config(provider)
            api_key = LLMConfig.get_api_key(provider)
            
            if not api_key:
                return None
            
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
            
            # Add response format if supported
            if config.get("supports_json_mode"):
                payload["response_format"] = {"type": "json_object"}
                
                # DeepSeek requires "json" in prompt when using json_object mode
                if provider == LLMProvider.DEEPSEEK:
                    # Add "Return JSON:" to the last user message if not already present
                    if messages and "json" not in messages[-1]["content"].lower():
                        messages[-1]["content"] += "\n\nReturn valid JSON only."
            
            timeout = config.get("timeout", 60)
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{config['api_base']}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    # Track usage and cost
                    usage = result.get("usage", {})
                    input_tokens = usage.get("prompt_tokens", 0)
                    output_tokens = usage.get("completion_tokens", 0)
                    cost = LLMConfig.estimate_cost(provider, input_tokens, output_tokens)
                    
                    self.total_cost += cost
                    self.request_count += 1
                    
                    print(f"   💰 Cost: ${cost:.6f} | Total: ${self.total_cost:.4f} ({self.request_count} requests)")
                    
                    return content
                else:
                    error_text = response.text[:200]
                    print(f"   ❌ {provider.value} API error: {response.status_code}")
                    print(f"      {error_text}")
                    
                    # Mark provider as failed for auth/balance issues
                    if response.status_code in [401, 402, 403, 429]:
                        self.failed_providers.add(provider)
                    
                    return None
                    
        except httpx.TimeoutException:
            print(f"   ⏱️  {provider.value} timeout (>{timeout}s)")
            return None
        except Exception as e:
            print(f"   ❌ {provider.value} error: {str(e)[:100]}")
            return None
    
    async def _call_with_comparison(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 4000
    ) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Call multiple providers and compare results (for validation)
        
        Returns:
            (primary_result, comparison_data)
        """
        if len(self.all_providers) < 2 or not self.enable_comparison:
            # No comparison possible or not enabled
            result = await self._call_llm(messages, temperature, max_tokens)
            return result, None
        
        # Call primary and secondary in parallel
        primary = self.all_providers[0]
        secondary = self.all_providers[1]
        
        print(f"   🔬 Comparison mode: {primary.value} vs {secondary.value}")
        
        tasks = [
            self._try_provider(primary, messages, temperature, max_tokens),
            self._try_provider(secondary, messages, temperature, max_tokens)
        ]
        
        results = await asyncio.gather(*tasks)
        primary_result, secondary_result = results
        
        # Build comparison data
        comparison = {
            "primary_provider": primary.value,
            "secondary_provider": secondary.value,
            "primary_response": primary_result,
            "secondary_response": secondary_result,
            "match": primary_result == secondary_result if (primary_result and secondary_result) else None
        }
        
        if primary_result and secondary_result:
            if primary_result == secondary_result:
                print(f"   ✅ Responses match!")
            else:
                print(f"   ⚠️  Responses differ - using primary ({primary.value})")
        
        # Return primary result (or secondary if primary failed)
        final_result = primary_result if primary_result else secondary_result
        
        return final_result, comparison
    
    # =========================================================================
    # HIGH-LEVEL API METHODS
    # =========================================================================
    
    async def understand_query(self, query: str, enable_comparison: bool = False) -> Dict[str, Any]:
        """
        Parse recipe query into structured data using LLM intelligence
        
        Args:
            query: Natural language recipe query
            enable_comparison: Compare results between providers
        
        Returns:
            Structured query data with dish name, ingredients, dietary prefs, etc.
        """
        # Check cache
        cache_key = self._get_cache_key(query, "understand", self.primary_provider.value if self.primary_provider else "")
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        if not self.primary_provider:
            # No LLM available - return basic structure
            return self._fallback_understanding(query)
        
        # Build prompt
        user_prompt = f"""Analyze this recipe search query:

Query: "{query}"

Return structured JSON following the exact format specified in the system prompt.
"""
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPTS["query_understanding"]},
            {"role": "user", "content": user_prompt}
        ]
        
        # Call LLM (with or without comparison)
        if enable_comparison and len(self.all_providers) >= 2:
            response, comparison = await self._call_with_comparison(messages)
        else:
            response = await self._call_llm(messages)
            comparison = None
        
        if not response:
            return self._fallback_understanding(query)
        
        try:
            # Parse JSON response
            result = self._parse_json_response(response)
            
            # Validate required fields
            required_fields = ["dish_name", "excluded_ingredients", "required_ingredients"]
            if not all(field in result for field in required_fields):
                print(f"   ⚠️  LLM response missing required fields")
                return self._fallback_understanding(query)
            
            # Add metadata
            result["_provider"] = self.primary_provider.value if self.primary_provider else "none"
            result["_comparison"] = comparison
            
            # Cache successful result
            self._set_cache(cache_key, result)
            
            return result
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"   ⚠️  Failed to parse LLM response: {e}")
            return self._fallback_understanding(query)
    
    async def translate_query(
        self, 
        query: str, 
        target_language: str = "English",
        custom_prompt: Optional[str] = None
    ) -> str:
        """
        Translate recipe query to target language
        
        Args:
            query: Query to translate
            target_language: Target language (default: English)
            custom_prompt: Custom prompt override
        
        Returns:
            Translated query string
        """
        # Check cache
        cache_key = self._get_cache_key(f"{query}:{target_language}", "translate")
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        if not self.primary_provider:
            return query  # No translation without LLM
        
        # Build prompt
        if custom_prompt:
            messages = [{"role": "user", "content": custom_prompt}]
        else:
            user_prompt = f"""Translate this recipe query to {target_language}:

Query: "{query}"

Return ONLY the translated text (no explanations, no markdown).
"""
            messages = [
                {"role": "system", "content": SYSTEM_PROMPTS["translation"]},
                {"role": "user", "content": user_prompt}
            ]
        
        response = await self._call_llm(messages, temperature=0.2, max_tokens=500)
        
        if response:
            translated = response.strip().strip('"')
            
            # Handle JSON responses (some LLMs return {"translation": "text"})
            if translated.startswith('{') and '"translation"' in translated:
                try:
                    parsed = json.loads(translated)
                    translated = parsed.get('translation', translated)
                except:
                    pass  # If JSON parsing fails, use as-is
            
            self._set_cache(cache_key, translated)
            return translated
        
        return query
    
    async def extract_ingredients(self, query: str) -> Dict[str, Any]:
        """
        Extract comprehensive ingredient information from query
        
        Returns:
            {
                "included": [...],
                "excluded": [...],
                "implied": [...],
                "dietary_context": "..."
            }
        """
        # Check cache
        cache_key = self._get_cache_key(query, "ingredients")
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        if not self.primary_provider:
            return {
                "included": [],
                "excluded": [],
                "implied": [],
                "dietary_context": "none"
            }
        
        user_prompt = f"""Extract all ingredient information from this query:

Query: "{query}"

Return JSON following the format specified in the system prompt.
"""
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPTS["ingredient_extraction"]},
            {"role": "user", "content": user_prompt}
        ]
        
        response = await self._call_llm(messages, temperature=0.2, max_tokens=1000)
        
        if response:
            try:
                result = self._parse_json_response(response)
                self._set_cache(cache_key, result)
                return result
            except:
                pass
        
        return {
            "included": [],
            "excluded": [],
            "implied": [],
            "dietary_context": "none"
        }
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def _parse_json_response(self, response: str) -> Dict:
        """Parse JSON from LLM response (handle markdown code blocks)"""
        response_clean = response.strip()
        
        # Remove markdown code blocks
        if response_clean.startswith("```json"):
            response_clean = response_clean[7:]
        elif response_clean.startswith("```"):
            response_clean = response_clean[3:]
        
        if response_clean.endswith("```"):
            response_clean = response_clean[:-3]
        
        return json.loads(response_clean.strip())
    
    def _fallback_understanding(self, query: str) -> Dict[str, Any]:
        """Fallback structure when LLM is unavailable"""
        return {
            "intent": "search",
            "dish_name": query,
            "excluded_ingredients": [],
            "required_ingredients": [],
            "dietary_preferences": [],
            "cooking_time": None,
            "cuisine_type": None,
            "spice_level": None,
            "course": None,
            "language_detected": "Unknown",
            "_provider": "fallback"
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            "primary_provider": self.primary_provider.value if self.primary_provider else "none",
            "available_providers": [p.value for p in self.all_providers],
            "failed_providers": [p.value for p in self.failed_providers],
            "total_cost_usd": round(self.total_cost, 4),
            "request_count": self.request_count,
            "avg_cost_per_request": round(self.total_cost / self.request_count, 6) if self.request_count > 0 else 0,
            "cache_size": len(self._cache),
            "comparison_enabled": self.enable_comparison
        }


# Global singleton instance
llm_service = LLMService()
