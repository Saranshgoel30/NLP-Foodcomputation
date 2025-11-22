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
        
        # Build REVOLUTIONARY scoring prompt
        prompt = f"""You are a MASTER CHEF + FOOD SCIENTIST + CULTURAL EXPERT evaluating recipe relevance.

MISSION: Score each recipe on a scale of 0-100 based on MULTI-DIMENSIONAL relevance.

USER QUERY: "{original_query}"
DETECTED CONTEXT: {dietary_preferences if dietary_preferences else "general"}

CRITICAL CONSTRAINTS (MUST SATISFY):
- HARD EXCLUSIONS (allergy/religion): {excluded_ingredients if excluded_ingredients else "None"}
- Required ingredients: {required_ingredients if required_ingredients else "Match query intent"}
- Dietary preferences: {dietary_preferences if dietary_preferences else "None"}

RECIPES TO SCORE (max 50):
{json.dumps(recipe_summaries, indent=2)}

SCORING RUBRIC (100 points total):

🎯 DIMENSION 1: LITERAL MATCH (0-25 points)
- Recipe name contains query terms? +10 points
- Exact ingredient matches? +10 points
- Cuisine type matches? +5 points

🧠 DIMENSION 2: SEMANTIC MATCH (0-25 points)
- Satisfies user's INTENT? +15 points
  Example: "comfort food" → traditional, familiar dishes
  Example: "quick meal" → <30 min prep time
- Similar cooking technique? +5 points
- Cultural similarity? +5 points

⚖️ DIMENSION 3: CONSTRAINT SATISFACTION (0-25 points)
- HARD CONSTRAINTS:
  * Contains excluded ingredient? INSTANT -100 (FAILS completely)
  * Variations count! "onion" = onions, onion paste, pyaz, kanda, spring onion, shallot
  * Check NAME too! "Onion Pakora" fails if onions excluded
- SOFT CONSTRAINTS:
  * Missing preferred ingredient? -5 points
  * Wrong meal type? -3 points

🌟 DIMENSION 4: CONTEXTUAL FIT (0-25 points)
- Matches meal type context? +8 points
- Appropriate difficulty level? +5 points
- Seasonal match? +5 points
- Social context (family/party/solo)? +7 points

INTELLIGENCE RULES:
1. **Exclusion variations (CRITICAL)**:
   - onion: onions, onion paste, onion powder, spring onion, shallot, scallion, pyaz, kanda, vengayam, ullipaya, peyaj, dungri
   - garlic: garlic paste, garlic powder, lahsun, lasun, poondu, velluli, rasun, lasan
   - paneer: cottage cheese, Indian cottage cheese
   
2. **Query intent examples**:
   - "butter chicken" → North Indian, creamy, tomato-based, mild-medium spice
   - "jain food" → NO onion/garlic/root veg AT ALL (auto -100 if present)
   - "quick meal" → prep_time <30 min, simple cooking
   - "comfort food" → traditional, familiar, satisfying

3. **Name checking**: 
   - "Onion Bhaji" automatically -100 if onions excluded
   - "Lahsuni Dal" automatically -100 if garlic excluded

RESPOND with JSON (EXACT format):
{{
  "scored_recipes": [
    {{
      "index": 0,
      "relevance_score": 95,
      "literal_match": 23,
      "semantic_match": 24,
      "constraint_satisfaction": 25,
      "contextual_fit": 23,
      "reasoning": "Perfect match: Paneer Tikka, no onion, North Indian, vegetarian",
      "constraint_violations": [],
      "bonuses": ["vegetarian", "north_indian", "protein_rich"],
      "category": "perfect"
    }},
    {{
      "index": 1,
      "relevance_score": 75,
      "literal_match": 18,
      "semantic_match": 20,
      "constraint_satisfaction": 20,
      "contextual_fit": 17,
      "reasoning": "Good match: Similar dish, slightly different spice profile",
      "constraint_violations": [],
      "bonuses": ["vegetarian"],
      "category": "good"
    }},
    {{
      "index": 2,
      "relevance_score": -100,
      "literal_match": 0,
      "semantic_match": 0,
      "constraint_satisfaction": -100,
      "contextual_fit": 0,
      "reasoning": "EXCLUDED: Contains onion paste in ingredients",
      "constraint_violations": ["onion"],
      "bonuses": [],
      "category": "excluded"
    }}
  ]
}}

CATEGORIZATION THRESHOLDS:
- perfect_matches: score >= 85
- good_matches: score 70-84
- possible_matches: score 50-69
- excluded: score < 50 OR constraint_violations present

Return ONLY valid JSON, no markdown, no explanations outside JSON."""

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
                
                # Process scored recipes
                scored_recipes = result.get('scored_recipes', [])
                
                # Sort by relevance score (descending)
                scored_recipes.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
                
                # Categorize based on scores and violations
                perfect_matches = []
                good_matches = []
                possible_matches = []
                excluded = []
                
                for scored in scored_recipes:
                    idx = scored.get('index', -1)
                    if idx < 0 or idx >= len(recipes):
                        continue
                    
                    recipe = recipes[idx]
                    score = scored.get('relevance_score', 0)
                    violations = scored.get('constraint_violations', [])
                    category = scored.get('category', 'possible')
                    
                    # Add scoring metadata to recipe
                    if 'document' not in recipe:
                        recipe['document'] = {}
                    recipe['document']['_llm_score'] = score
                    recipe['document']['_llm_reasoning'] = scored.get('reasoning', '')
                    
                    # Categorize
                    if violations or score < 0:
                        excluded.append(recipe)
                    elif score >= 85 or category == 'perfect':
                        perfect_matches.append(recipe)
                    elif score >= 70 or category == 'good':
                        good_matches.append(recipe)
                    elif score >= 50 or category == 'possible':
                        possible_matches.append(recipe)
                    else:
                        excluded.append(recipe)
                
                categorized = {
                    "perfect_matches": perfect_matches,
                    "good_matches": good_matches,
                    "possible_matches": possible_matches,
                    "excluded": excluded,
                    "reasoning": f"Scored {len(scored_recipes)} recipes using multi-dimensional relevance"
                }
                
                print(f"🤖 LLM Smart Scoring: {len(perfect_matches)} perfect (≥85), "
                      f"{len(good_matches)} good (70-84), "
                      f"{len(possible_matches)} possible (50-69), "
                      f"{len(excluded)} excluded (<50 or violations)")
                
                # Show top 3 scores
                if scored_recipes[:3]:
                    print(f"   Top 3 scores:")
                    for i, s in enumerate(scored_recipes[:3], 1):
                        print(f"      {i}. Score {s.get('relevance_score', 0)}: {s.get('reasoning', 'N/A')[:60]}")
                
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
