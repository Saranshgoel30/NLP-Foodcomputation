"""
Smart LLM-Powered Recipe Filtering
Uses DeepSeek/LLM to intelligently filter recipes based on context and requirements
"""

from typing import List, Dict, Any, Optional
import json
from .llm_service import llm_service


class SmartRecipeFilter:
    """
    Intelligent recipe filtering using LLM understanding
    Goes beyond simple keyword matching to understand recipe context
    """
    
    def __init__(self):
        self.llm_service = llm_service
    
    async def filter_recipes_smart(
        self,
        recipes: List[Dict[str, Any]],
        original_query: str,
        excluded_ingredients: List[str],
        required_ingredients: List[str],
        dietary_preferences: List[str]
    ) -> Dict[str, Any]:
        """
        Stage 2 filtering: Use LLM to intelligently filter recipes
        
        Returns:
            {
                "perfect_matches": [],  # Recipes that definitely match
                "good_matches": [],     # Recipes that probably match
                "possible_matches": [], # Recipes that might match
                "excluded": []          # Recipes that don't match
            }
        """
        
        if not self.llm_service.provider or len(recipes) == 0:
            # Fallback to rule-based if no LLM
            return self._rule_based_filter(recipes, excluded_ingredients, required_ingredients)
        
        # For large result sets, use batch filtering
        if len(recipes) > 20:
            return await self._batch_smart_filter(
                recipes, original_query, excluded_ingredients, 
                required_ingredients, dietary_preferences
            )
        else:
            return await self._detailed_smart_filter(
                recipes, original_query, excluded_ingredients,
                required_ingredients, dietary_preferences
            )
    
    async def _batch_smart_filter(
        self,
        recipes: List[Dict[str, Any]],
        original_query: str,
        excluded_ingredients: List[str],
        required_ingredients: List[str],
        dietary_preferences: List[str]
    ) -> Dict[str, Any]:
        """
        Batch processing for large result sets
        Analyzes recipes in groups for efficiency
        """
        
        # Create a compact representation for LLM
        recipe_summaries = []
        for i, recipe in enumerate(recipes[:50]):  # Limit to top 50
            doc = recipe.get('document', {})
            summary = {
                'index': i,
                'name': doc.get('name', ''),
                'ingredients': doc.get('ingredients', [])[:10],  # First 10 ingredients
                'cuisine': doc.get('cuisine', ''),
                'diet': doc.get('diet', '')
            }
            recipe_summaries.append(summary)
        
        # Build smart filtering prompt
        prompt = f"""You are an expert recipe analyzer. Analyze these recipes and categorize them based on the user's requirements.

USER QUERY: "{original_query}"

REQUIREMENTS:
- Excluded ingredients: {excluded_ingredients if excluded_ingredients else "None"}
- Required ingredients: {required_ingredients if required_ingredients else "None (just match the query)"}
- Dietary preferences: {dietary_preferences if dietary_preferences else "None"}

RECIPES TO ANALYZE:
{json.dumps(recipe_summaries, indent=2)}

IMPORTANT RULES:
1. **Exclusions are STRICT**: If a recipe contains ANY form of an excluded ingredient (in name OR ingredients), mark it as "excluded"
2. **Requirements are FLEXIBLE**: If no specific requirements, just match the query intent
3. **Be smart about variations**: 
   - "onion" includes: onions, onion paste, onion powder, spring onions, shallots
   - "garlic" includes: garlic, garlic paste, garlic powder
   - "paneer" includes: paneer, cottage cheese
4. **Title matters**: Check recipe names for excluded ingredients too (e.g., "Onion Pakora" should be excluded if onions are excluded)
5. **Query intent**: For "butter chicken", any butter chicken recipe is good even if ingredient list varies

RESPOND with JSON in this EXACT format:
{{
    "perfect_matches": [0, 2, 5],  // Recipe indices that perfectly match all requirements
    "good_matches": [1, 3],        // Recipes that match well but might be missing minor details
    "possible_matches": [4],       // Recipes that partially match
    "excluded": [6, 7, 8],         // Recipes with excluded ingredients or wrong type
    "reasoning": "Brief explanation of categorization logic"
}}

Return ONLY valid JSON, no additional text."""

        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.llm_service._call_llm(messages, temperature=0.1)
            
            if response:
                # Clean response
                response_clean = response.strip()
                if response_clean.startswith("```json"):
                    response_clean = response_clean[7:]
                if response_clean.startswith("```"):
                    response_clean = response_clean[3:]
                if response_clean.endswith("```"):
                    response_clean = response_clean[:-3]
                
                result = json.loads(response_clean.strip())
                
                # Build categorized results
                categorized = {
                    "perfect_matches": [recipes[i] for i in result.get('perfect_matches', []) if i < len(recipes)],
                    "good_matches": [recipes[i] for i in result.get('good_matches', []) if i < len(recipes)],
                    "possible_matches": [recipes[i] for i in result.get('possible_matches', []) if i < len(recipes)],
                    "excluded": [recipes[i] for i in result.get('excluded', []) if i < len(recipes)],
                    "reasoning": result.get('reasoning', '')
                }
                
                print(f"🤖 LLM Smart Filter: {len(categorized['perfect_matches'])} perfect, "
                      f"{len(categorized['good_matches'])} good, "
                      f"{len(categorized['possible_matches'])} possible matches")
                if categorized['reasoning']:
                    print(f"   Reasoning: {categorized['reasoning']}")
                
                return categorized
            
        except Exception as e:
            print(f"⚠️  LLM filtering failed: {e}")
        
        # Fallback to rule-based
        return self._rule_based_filter(recipes, excluded_ingredients, required_ingredients)
    
    async def _detailed_smart_filter(
        self,
        recipes: List[Dict[str, Any]],
        original_query: str,
        excluded_ingredients: List[str],
        required_ingredients: List[str],
        dietary_preferences: List[str]
    ) -> Dict[str, Any]:
        """
        Detailed analysis for smaller result sets
        Provides per-recipe reasoning
        """
        # For now, use batch method (can be enhanced later)
        return await self._batch_smart_filter(
            recipes, original_query, excluded_ingredients,
            required_ingredients, dietary_preferences
        )
    
    def _rule_based_filter(
        self,
        recipes: List[Dict[str, Any]],
        excluded_ingredients: List[str],
        required_ingredients: List[str]
    ) -> Dict[str, Any]:
        """
        Fallback rule-based filtering when LLM unavailable
        """
        perfect_matches = []
        possible_matches = []
        excluded = []
        
        for recipe in recipes:
            doc = recipe.get('document', {})
            ingredients_lower = [ing.lower() for ing in doc.get('ingredients', [])]
            name_lower = doc.get('name', '').lower()
            
            # Check exclusions
            has_excluded = False
            for excl in excluded_ingredients:
                excl_lower = excl.lower()
                # Check in ingredients
                if any(excl_lower in ing for ing in ingredients_lower):
                    has_excluded = True
                    break
                # Check in name
                if excl_lower in name_lower:
                    has_excluded = True
                    break
            
            if has_excluded:
                excluded.append(recipe)
                continue
            
            # If no requirements, all non-excluded are perfect matches
            if not required_ingredients:
                perfect_matches.append(recipe)
            else:
                # Check requirements (flexible)
                matches = sum(1 for req in required_ingredients 
                             if any(req.lower() in ing for ing in ingredients_lower))
                
                if matches >= len(required_ingredients) * 0.5:  # At least 50% match
                    perfect_matches.append(recipe)
                else:
                    possible_matches.append(recipe)
        
        return {
            "perfect_matches": perfect_matches,
            "good_matches": [],
            "possible_matches": possible_matches,
            "excluded": excluded,
            "reasoning": "Rule-based filtering (LLM unavailable)"
        }


# Singleton instance
smart_filter = SmartRecipeFilter()
