"""
LLM Configuration for Smart Recipe Search
Supports DeepSeek, OpenAI, and other providers
"""

import os
from typing import Dict, Optional, List
from enum import Enum

class LLMProvider(Enum):
    """Supported LLM providers"""
    XAI = "xai"
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"

class LLMConfig:
    """LLM Configuration Manager"""
    
    # Provider priorities (fallback order)
    PROVIDERS = [
        LLMProvider.DEEPSEEK,  # Primary - Most cost-effective
        LLMProvider.XAI,       # Secondary - Grok fallback
        LLMProvider.OPENAI,
        LLMProvider.GROQ,
    ]
    
    # Model configurations
    MODELS = {
        LLMProvider.XAI: {
            "model": "grok-beta",
            "api_base": "https://api.x.ai/v1",
            "api_key_env": "XAI_API_KEY",
            "max_tokens": 2000,
            "temperature": 0.3,
            "cost_per_1k_tokens": 0.0005,  # $5 per 1M tokens input, $15 per 1M tokens output
        },
        LLMProvider.DEEPSEEK: {
            "model": "deepseek-chat",
            "api_base": "https://api.deepseek.com/v1",
            "api_key_env": "DEEPSEEK_API_KEY",
            "max_tokens": 2000,
            "temperature": 0.3,  # Lower for more consistent results
            "cost_per_1k_tokens": 0.0001,  # Very cheap!
        },
        LLMProvider.OPENAI: {
            "model": "gpt-4o-mini",
            "api_base": "https://api.openai.com/v1",
            "api_key_env": "OPENAI_API_KEY",
            "max_tokens": 2000,
            "temperature": 0.3,
            "cost_per_1k_tokens": 0.0015,
        },
        LLMProvider.GROQ: {
            "model": "mixtral-8x7b-32768",
            "api_base": "https://api.groq.com/openai/v1",
            "api_key_env": "GROQ_API_KEY",
            "max_tokens": 2000,
            "temperature": 0.3,
            "cost_per_1k_tokens": 0.0,  # Free tier available
        },
    }
    
    @classmethod
    def get_available_provider(cls) -> Optional[LLMProvider]:
        """Get first available provider with API key"""
        for provider in cls.PROVIDERS:
            config = cls.MODELS[provider]
            api_key = os.getenv(config["api_key_env"])
            if api_key:
                return provider
        return None
    
    @classmethod
    def get_config(cls, provider: LLMProvider) -> Dict:
        """Get configuration for specific provider"""
        return cls.MODELS[provider]
    
    @classmethod
    def get_api_key(cls, provider: LLMProvider) -> Optional[str]:
        """Get API key for provider"""
        config = cls.MODELS[provider]
        return os.getenv(config["api_key_env"])

# System prompts for different tasks
SYSTEM_PROMPTS = {
    "query_understanding": """You are an expert Indian cuisine assistant specializing in recipe search.
Your task is to understand user queries about recipes and extract structured information.

You must analyze the query and return a JSON object with:
- "intent": The main intent (search, filter, translate, etc.)
- "dish_name": The primary dish being searched for
- "excluded_ingredients": List of ingredients to exclude
- "required_ingredients": List of ingredients that must be included
- "dietary_preferences": Any dietary requirements (vegetarian, vegan, jain, etc.)
- "cooking_time": Time constraint if mentioned
- "cuisine_type": Cuisine type if specified
- "spice_level": Spice preference if mentioned
- "translated_query": English translation if query was in another language
- "language_detected": Language of the original query

Be intelligent about Indian food context:
- Understand Hindi/Hinglish terms (aloo=potato, pyaz=onion, tamatar=tomato, mirch=chili)
- Recognize regional dishes and their variants
- Understand cooking methods (tadka, bhuna, dum, tandoori)
- Know dietary restrictions (jain = no onion/garlic, satvik = pure vegetarian)

Return ONLY valid JSON, no additional text.""",

    "translation": """You are an expert translator specializing in ALL Indian languages and food terminology.

Your task: Translate recipe search queries to clear, searchable English.

Supported languages: Hindi, Marathi, Tamil, Telugu, Kannada, Malayalam, Bengali, Gujarati, Punjabi, Odia, Assamese

IMPORTANT RULES:
1. Always translate to simple, searchable English
2. Preserve ingredient names (both local and English terms)
3. Maintain cooking instructions and dish context
4. For recipe searches, use common English dish names

Common translations:
- Hindi: pyaz=onion, aloo=potato, tamatar=tomato, mirch=chili, paneer=cottage cheese
- Marathi: kanda=onion, batata=potato, bhaji=vegetable curry, nahi/naslelī=without
- Tamil: vengayam=onion, urulaikizhangu=potato
- Telugu: ullipaya=onion, bangaladumpa=potato

Example translations:
- "कांदा नसलेली पनीर भाजी" → "paneer vegetable curry without onion"
- "प्याज के बिना आलू की सब्जी" → "potato curry without onion"
- "vengayam illama kuzhambu" → "curry without onion"

Return ONLY the English translation, nothing else. Be concise and use standard recipe terminology.""",

    "ingredient_extraction": """You are an expert at identifying ingredients in recipe queries.

Extract ALL ingredients mentioned, including:
- Explicit ingredients (tomato, onion, chicken, etc.)
- Implied ingredients (spicy → chili, creamy → cream/milk)
- Negative ingredients (without X, no Y)

Consider Indian cuisine context:
- "no pyaz" = no onion
- "jain food" = no onion, no garlic, no root vegetables
- "satvik" = pure vegetarian, no onion/garlic

Return JSON with:
- "included": [list of required ingredients]
- "excluded": [list of excluded ingredients]
- "implied": [list of implied ingredients]
- "dietary_context": any dietary restrictions identified

Return ONLY valid JSON."""
}

# Few-shot examples for better understanding
EXAMPLE_QUERIES = {
    "query_understanding": [
        {
            "query": "paneer tikka without onions under 30 minutes",
            "response": {
                "intent": "search",
                "dish_name": "paneer tikka",
                "excluded_ingredients": ["onion", "onions", "pyaz"],
                "required_ingredients": ["paneer"],
                "dietary_preferences": [],
                "cooking_time": {"max_minutes": 30},
                "cuisine_type": "Indian",
                "spice_level": None,
                "translated_query": "paneer tikka without onions under 30 minutes",
                "language_detected": "English"
            }
        },
        {
            "query": "jaldi bina pyaz ke aloo ki sabzi banana hai",
            "response": {
                "intent": "search",
                "dish_name": "aloo sabzi",
                "excluded_ingredients": ["onion", "onions", "pyaz"],
                "required_ingredients": ["potato", "aloo"],
                "dietary_preferences": [],
                "cooking_time": {"preference": "quick"},
                "cuisine_type": "Indian",
                "spice_level": None,
                "translated_query": "quick potato curry without onions",
                "language_detected": "Hindi"
            }
        },
        {
            "query": "jain dal recipe no garlic",
            "response": {
                "intent": "search",
                "dish_name": "dal",
                "excluded_ingredients": ["onion", "garlic", "pyaz", "lahsun", "root vegetables"],
                "required_ingredients": ["lentils", "dal"],
                "dietary_preferences": ["jain", "vegetarian"],
                "cooking_time": None,
                "cuisine_type": "Indian",
                "spice_level": None,
                "translated_query": "jain dal recipe no garlic",
                "language_detected": "English"
            }
        }
    ]
}
