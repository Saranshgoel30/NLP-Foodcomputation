"""
Revolutionary Query Expansion Engine
Uses DeepSeek to expand queries with synonyms, regional variants, and semantic alternatives
"""

from typing import List, Dict, Any
import json
from .llm_service import llm_service


class QueryExpansionEngine:
    """
    Expands search queries to find MORE relevant results
    Example: "butter chicken" → ["murgh makhani", "makhani chicken", "butter chicken curry"]
    """
    
    def __init__(self):
        self.llm_service = llm_service
        self._cache = {}  # Cache expansions to avoid repeated calls
    
    async def expand_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Expand a query into multiple semantically equivalent searches
        
        Returns:
        {
            "primary_query": "original query",
            "expanded_queries": [
                {"query": "synonym1", "weight": 1.0, "reason": "exact_synonym"},
                {"query": "variant1", "weight": 0.9, "reason": "regional_variant"},
                ...
            ],
            "search_strategy": "parallel" | "cascading"
        }
        """
        
        # Check cache
        cache_key = f"expand:{query}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        if not self.llm_service.provider:
            # Fallback: just use original query
            return {
                "primary_query": query,
                "expanded_queries": [{"query": query, "weight": 1.0, "reason": "original"}],
                "search_strategy": "single"
            }
        
        # Build expansion prompt
        prompt = f"""You are a CULINARY ENCYCLOPEDIA with deep knowledge of food terminology across cultures.

MISSION: Expand this search query into ALL semantically equivalent variations.

USER QUERY: "{query}"
CONTEXT: {json.dumps(context) if context else "general search"}

EXPANSION CATEGORIES:

1. **EXACT SYNONYMS** (weight: 1.0)
   - Regional names: "butter chicken" = "murgh makhani" = "makhani murgh"
   - Alternate spellings: "biryani" = "biriyani" = "beriani"
   - Language variants: "sabzi" = "sabji" = "curry"

2. **REGIONAL VARIANTS** (weight: 0.95)
   - "Punjabi butter chicken", "Delhi butter chicken"
   - "Hyderabadi biryani", "Lucknowi biryani"
   - "North Indian paneer" vs "South Indian paneer"

3. **INGREDIENT SUBSTITUTIONS** (weight: 0.9)
   - "paneer" = "cottage cheese" (in some contexts)
   - "coriander" = "cilantro" = "dhaniya"
   - "chickpeas" = "chana" = "garbanzo beans"

4. **ANGLICIZED/TRANSLITERATED** (weight: 0.9)
   - "dal makhani" = "daal makhani" = "dhal makhani"
   - "chole" = "chhole" = "chole bhature"

5. **SIMPLIFIED DESCRIPTIONS** (weight: 0.85)
   - "butter chicken" = "creamy tomato chicken" = "indian chicken in butter sauce"
   - "dal" = "lentil curry" = "indian lentil soup"

6. **RELATED DISHES** (weight: 0.7) - Similar but not identical
   - "butter chicken" → "chicken tikka masala" (similar style)
   - "aloo gobi" → "aloo matar" (similar vegetable combos)
   - Only include if VERY similar!

7. **DISH CATEGORY** (weight: 0.6) - Broader category
   - "paneer tikka" → "paneer appetizer" → "indian paneer starter"
   - Only for discovery, not primary results

INTELLIGENCE RULES:
1. Preserve EXCLUSIONS in ALL expansions!
   - "paneer without onion" → ALL variants must have "without onion"
   - "no garlic dal" → ALL variants must have "no garlic"

2. Understand COMPOUND TERMS:
   - "chole bhature" = dish name (don't split into "chole" + "bhature")
   - "dum aloo" = cooking style + ingredient (keep together)

3. Cultural context:
   - "jain food" → don't expand to dishes with onion/garlic
   - "vegan" → don't suggest dairy-heavy variants

4. Time/context preservation:
   - "quick pasta" → all variants must be quick
   - "breakfast" → only breakfast-appropriate variants

RESPOND with JSON (max 10 expansions):
{{
  "primary_query": "{query}",
  "expanded_queries": [
    {{
      "query": "murgh makhani",
      "weight": 1.0,
      "reason": "exact_synonym",
      "confidence": "high"
    }},
    {{
      "query": "makhani chicken",
      "weight": 1.0,
      "reason": "alternate_word_order",
      "confidence": "high"
    }},
    {{
      "query": "butter chicken curry",
      "weight": 0.95,
      "reason": "common_suffix",
      "confidence": "high"
    }},
    {{
      "query": "Punjabi butter chicken",
      "weight": 0.9,
      "reason": "regional_variant",
      "confidence": "medium"
    }},
    {{
      "query": "chicken tikka masala",
      "weight": 0.7,
      "reason": "similar_dish",
      "confidence": "medium"
    }}
  ],
  "search_strategy": "parallel",
  "reasoning": "Butter chicken has multiple exact names in Indian cuisine"
}}

SEARCH STRATEGIES:
- "parallel": Search all queries simultaneously, merge by score (for synonyms)
- "cascading": Try primary first, then fallbacks if needed (for discovery)

Return ONLY valid JSON, no markdown."""

        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.llm_service._call_llm(messages, temperature=0.3)
            
            if response:
                # Clean and parse
                response_clean = response.strip()
                if response_clean.startswith("```json"):
                    response_clean = response_clean[7:]
                if response_clean.startswith("```"):
                    response_clean = response_clean[3:]
                if response_clean.endswith("```"):
                    response_clean = response_clean[:-3]
                
                result = json.loads(response_clean.strip())
                
                # Cache result
                self._cache[cache_key] = result
                
                print(f"🔍 Query Expansion: '{query}' → {len(result.get('expanded_queries', []))} variants")
                for exp in result.get('expanded_queries', [])[:3]:
                    print(f"   • {exp.get('query', '')} (weight: {exp.get('weight', 0)}) - {exp.get('reason', '')}")
                
                return result
                
        except Exception as e:
            print(f"⚠️  Query expansion failed: {e}")
        
        # Fallback: original query only
        return {
            "primary_query": query,
            "expanded_queries": [{"query": query, "weight": 1.0, "reason": "original"}],
            "search_strategy": "single"
        }


# Global instance
query_expander = QueryExpansionEngine()
