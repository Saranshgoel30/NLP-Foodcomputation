"""
Enhanced Query Parser - Combines LLM intelligence with rule-based fallbacks
"""

from typing import Dict, List, Any, Optional
import asyncio
import json
from .llm_service import llm_service
from .query_parser import QueryParser
from .translation_helper import translator


class EnhancedQueryParser:
    """
    Combines LLM-powered understanding with rule-based query parsing
    LLM provides smart understanding, rules provide reliable fallback
    """
    
    def __init__(self):
        self.llm_service = llm_service
        self.rule_parser = QueryParser()
        self.use_llm = self.llm_service.primary_provider is not None
        
        print(f"🧠 Enhanced Query Parser initialized")
        print(f"   LLM Mode: {'ENABLED' if self.use_llm else 'DISABLED (rule-based fallback)'}")
        if self.use_llm:
            print(f"   Provider: {self.llm_service.primary_provider.value}")
    
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
    
    async def translate_query_to_search_terms(self, query: str) -> dict:
        """
        REVOLUTIONARY: Let LLM decide the BEST search strategy for Typesense
        
        Instead of searching user's exact words, translate INTENT into optimal search terms
        """
        if not self.use_llm:
            # Simple fallback
            return {
                "search_query": query,
                "strategy": "simple",
                "reasoning": "LLM unavailable"
            }
        
        try:
            prompt = f"""You are a search query optimizer for a recipe database with 9,600 recipes.

USER QUERY: "{query}"

Your task: Convert this into the BEST search terms for finding relevant recipes.

CRITICAL INTELLIGENCE:
1. "Jain recipes" → Don't search "jain recipes" (too specific!)
   Instead: Search broadly for vegetarian dishes, THEN filter out onion/garlic
   Better query: "vegetarian indian curry dal paneer sabzi"
   
2. "paneer without onion" → Search "paneer" (broad), filter onion later
   
3. "butter chicken" → Could also be "murgh makhani" → search both: "butter chicken OR murgh makhani"

4. "quick pasta" → Search "pasta", add time filter separately

5. General category (like "jain") → Search for DISH TYPES not the category name
   Example: "breakfast recipes" → "poha upma idli dosa paratha"

STRATEGY OPTIONS:
- "broad": Search general terms, filter later (for restrictive queries like "jain")
- "specific": Search exact dish name (for specific dishes like "butter chicken")
- "multi": Search multiple related terms with OR (for synonyms)

OUTPUT JSON:
{{
  "search_query": "optimized search terms for Typesense",
  "strategy": "broad" | "specific" | "multi",
  "reasoning": "why this search strategy",
  "filter_after": ["constraints to apply after search"]
}}

EXAMPLES:

Query: "Jain recipes (no onion no garlic)"
{{
  "search_query": "dal paneer sabzi curry tikka paratha roti vegetarian",
  "strategy": "broad",
  "reasoning": "Jain is a dietary restriction, not a dish. Search for common vegetarian dishes, then filter out onion/garlic",
  "filter_after": ["no onion", "no garlic", "no root vegetables"]
}}

Query: "butter chicken"
{{
  "search_query": "butter chicken murgh makhani",
  "strategy": "multi",
  "reasoning": "Butter chicken has a synonym in Hindi (murgh makhani), search both",
  "filter_after": []
}}

Query: "paneer tikka without onion"
{{
  "search_query": "paneer tikka",
  "strategy": "specific",
  "reasoning": "Specific dish name, search directly, filter onion after",
  "filter_after": ["no onion"]
}}

Query: "quick breakfast"
{{
  "search_query": "poha upma idli dosa paratha sandwich toast",
  "strategy": "broad",
  "reasoning": "Breakfast is a category, search for common breakfast dishes",
  "filter_after": ["quick cooking time"]
}}

Now optimize: "{query}"
Return ONLY valid JSON."""

            messages = [{"role": "user", "content": prompt}]
            response = await self.llm_service._call_llm(messages, temperature=0.2, max_tokens=500)
            
            if response:
                # Parse response
                response_clean = response.strip()
                if response_clean.startswith("```json"):
                    response_clean = response_clean[7:]
                if response_clean.startswith("```"):
                    response_clean = response_clean[3:]
                if response_clean.endswith("```"):
                    response_clean = response_clean[:-3]
                
                result = json.loads(response_clean.strip())
                
                print(f"\n🎯 LLM Search Optimization:")
                print(f"   Original: {query}")
                print(f"   Optimized: {result.get('search_query', query)}")
                print(f"   Strategy: {result.get('strategy', 'unknown')}")
                print(f"   Reasoning: {result.get('reasoning', 'N/A')}")
                
                return result
                
        except Exception as e:
            print(f"⚠️  Query optimization failed: {e}")
        
        # Fallback
        return {
            "search_query": query,
            "strategy": "simple",
            "reasoning": "Optimization failed",
            "filter_after": []
        }
    
    async def translate_to_english(self, query: str) -> str:
        """
        Translate non-English query to English with semantic understanding
        Uses hybrid approach: rule-based translation + LLM refinement
        """
        # Step 1: Use rule-based semantic translation
        semantic_result = translator.semantic_translation(query)
        
        print(f"\n🌍 Semantic Translation:")
        print(f"  Language Detected: {semantic_result['detected_language']}")
        print(f"  Rule-based Translation: {semantic_result['translated_query']}")
        print(f"  Excluded Ingredients: {semantic_result['excluded_ingredients']}")
        
        # If already English and no complex negations, return as-is
        if semantic_result['detected_language'] == 'English' and not semantic_result['excluded_ingredients']:
            return query
        
        # Step 2: Use LLM for refinement if available
        if self.use_llm:
            try:
                # Generate context-aware prompt
                llm_prompt = translator.get_translation_prompt(query)
                llm_translation = await self.llm_service.translate_query(
                    query, 
                    "English",
                    custom_prompt=llm_prompt
                )
                
                print(f"  LLM Refinement: {llm_translation}")
                
                # Use LLM result if it's significantly different and better
                if llm_translation and llm_translation.lower() != query.lower():
                    return llm_translation
            except Exception as e:
                print(f"  ⚠️  LLM refinement failed: {e}")
        
        # Fallback to rule-based translation
        return semantic_result['translated_query']
    
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
