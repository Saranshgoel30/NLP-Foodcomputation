"""
Enhanced Query Parser - Combines LLM intelligence with rule-based fallbacks
"""

from typing import Dict, List, Any, Optional
import asyncio
from .llm_service import llm_service
from .query_parser import QueryParser


class EnhancedQueryParser:
    """
    Combines LLM-powered understanding with rule-based query parsing
    LLM provides smart understanding, rules provide reliable fallback
    """
    
    def __init__(self):
        self.llm_service = llm_service
        self.rule_parser = QueryParser()
        self.use_llm = self.llm_service.provider is not None
        
        print(f"🧠 Enhanced Query Parser initialized")
        print(f"   LLM Mode: {'ENABLED' if self.use_llm else 'DISABLED (rule-based fallback)'}")
    
    async def parse_query(self, query: str) -> Dict[str, Any]:
        """
        Parse user query with LLM intelligence + rule-based fallback
        
        Returns comprehensive parsed query with:
        - Intent detection
        - Ingredient extraction (included/excluded/implied)
        - Dietary preferences
        - Cuisine/cooking time/spice level
        - Language detection and translation
        """
        try:
            # Get LLM understanding (async)
            llm_result = await self.llm_service.understand_query(query)
            
            # Get rule-based parsing (sync) as backup
            rule_result = self.rule_parser.parse_query(query)
            
            # Merge results - LLM takes priority, rules fill gaps
            merged = self._merge_results(llm_result, rule_result)
            
            # Add metadata
            merged["parsing_method"] = "LLM" if self.use_llm else "Rule-based"
            merged["original_query"] = query
            
            return merged
            
        except Exception as e:
            print(f"⚠️  Enhanced parsing failed: {e}")
            # Full fallback to rule-based
            result = self.rule_parser.parse_query(query)
            result["parsing_method"] = "Rule-based (fallback)"
            result["original_query"] = query
            return result
    
    async def translate_to_english(self, query: str) -> str:
        """Translate non-English query to English"""
        if not self.use_llm:
            return query
        
        try:
            return await self.llm_service.translate_query(query, "English")
        except Exception as e:
            print(f"⚠️  Translation failed: {e}")
            return query
    
    async def translate_from_english(self, text: str, target_language: str) -> str:
        """Translate English text to target language"""
        if not self.use_llm or target_language.lower() == "english":
            return text
        
        try:
            return await self.llm_service.translate_query(text, target_language)
        except Exception as e:
            print(f"⚠️  Translation failed: {e}")
            return text
    
    async def extract_smart_ingredients(self, query: str) -> Dict[str, List[str]]:
        """
        Extract ingredients with LLM context understanding
        Understands implied ingredients, dietary restrictions, and context
        """
        try:
            llm_ingredients = await self.llm_service.extract_ingredients(query)
            rule_ingredients = self.rule_parser.extract_ingredients(query)
            
            # Combine and deduplicate
            return {
                "included": list(set(
                    llm_ingredients.get("included", []) + 
                    rule_ingredients.get("included", [])
                )),
                "excluded": list(set(
                    llm_ingredients.get("excluded", []) + 
                    rule_ingredients.get("excluded", [])
                )),
                "implied": llm_ingredients.get("implied", []),
                "dietary_context": llm_ingredients.get("dietary_context", "")
            }
        except Exception as e:
            print(f"⚠️  Smart ingredient extraction failed: {e}")
            return self.rule_parser.extract_ingredients(query)
    
    def _merge_results(self, llm_result: Dict, rule_result: Dict) -> Dict[str, Any]:
        """
        Intelligently merge LLM and rule-based results
        LLM provides depth, rules provide coverage
        """
        merged = {}
        
        # Take LLM results where available and valid
        if llm_result:
            merged = llm_result.copy()
            
            # Add rule-based ingredients if LLM missed any
            if "excluded_ingredients" in rule_result:
                llm_excluded = set(merged.get("excluded_ingredients", []))
                rule_excluded = set(rule_result.get("excluded_ingredients", []))
                merged["excluded_ingredients"] = list(llm_excluded | rule_excluded)
            
            if "required_ingredients" in rule_result:
                llm_required = set(merged.get("required_ingredients", []))
                rule_required = set(rule_result.get("required_ingredients", []))
                merged["required_ingredients"] = list(llm_required | rule_required)
        else:
            # LLM failed, use rule-based
            merged = rule_result.copy()
        
        # Ensure all expected fields exist
        defaults = {
            "intent": "search",
            "dish_name": "",
            "excluded_ingredients": [],
            "required_ingredients": [],
            "dietary_preferences": [],
            "cooking_time": None,
            "cuisine_type": None,
            "spice_level": None,
            "translated_query": "",
            "language_detected": "Unknown"
        }
        
        for key, default_value in defaults.items():
            if key not in merged or merged[key] is None:
                merged[key] = default_value
        
        return merged
    
    def get_stats(self) -> Dict[str, Any]:
        """Get parser statistics"""
        return {
            "llm_enabled": self.use_llm,
            "llm_stats": self.llm_service.get_stats(),
            "rule_parser_loaded": self.rule_parser is not None
        }


# Global instance
enhanced_parser = EnhancedQueryParser()
