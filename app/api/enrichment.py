"""
Recipe Enrichment Service
Enriches recipes from GraphDB with nutrition data from Food Graph API
"""
from typing import List, Optional, Dict, Any
import structlog
from models import Recipe, NutritionInfo, EnhancedIngredient
from food_graph_client import FoodGraphClient
from config import settings

logger = structlog.get_logger()


class RecipeEnricher:
    """
    Enriches recipes with nutrition and ingredient data from Food Graph API
    
    This service adds:
    - Nutrition information (calories, macros, etc.)
    - Enhanced ingredient data with nutrition per 100g
    - Standardized ingredient names (fuzzy matching)
    """
    
    def __init__(self, food_graph_client: FoodGraphClient):
        self.fg_client = food_graph_client
        self.enabled = settings.enable_nutrition_enrichment
        logger.info("recipe_enricher_initialized", enabled=self.enabled)
    
    async def enrich_recipe(self, recipe: Recipe) -> Recipe:
        """
        Add nutrition and enhanced ingredient data to a single recipe
        
        Args:
            recipe: Recipe object from GraphDB
            
        Returns:
            Enriched recipe with nutrition data
        """
        if not self.enabled:
            logger.debug("enrichment_disabled", recipe=recipe.title)
            return recipe
        
        try:
            # Step 1: Try to get precalculated nutrition (fastest)
            nutrition_data = self._fetch_nutrition(recipe.title)
            if nutrition_data:
                recipe.nutrition = self._parse_nutrition(nutrition_data)
                recipe.nutrition_source = "precalculated" if recipe.nutrition else None
                logger.info(
                    "nutrition_enriched",
                    recipe=recipe.title,
                    source=recipe.nutrition_source,
                    has_data=recipe.nutrition is not None
                )
            
            # Step 2: Enhance ingredients with nutrition data
            if settings.enable_ingredient_standardization and recipe.ingredients:
                recipe.enhanced_ingredients = await self._enrich_ingredients(recipe.ingredients)
                logger.info(
                    "ingredients_enriched",
                    recipe=recipe.title,
                    count=len(recipe.enhanced_ingredients)
                )
            
        except Exception as e:
            logger.error(
                "enrichment_error",
                recipe=recipe.title,
                error=str(e),
                exc_info=True
            )
            # Return original recipe on error (fail gracefully)
        
        return recipe
    
    async def enrich_recipes(self, recipes: List[Recipe], max_batch: Optional[int] = None) -> List[Recipe]:
        """
        Enrich multiple recipes in batch
        
        Args:
            recipes: List of Recipe objects
            max_batch: Maximum number to enrich (None = all)
            
        Returns:
            List of enriched recipes
        """
        if not self.enabled:
            logger.debug("enrichment_disabled_batch", count=len(recipes))
            return recipes
        
        # Apply batch limit
        batch_size = max_batch or settings.enrichment_batch_size
        recipes_to_enrich = recipes[:batch_size] if batch_size else recipes
        
        logger.info(
            "enriching_recipes_batch",
            total=len(recipes),
            enriching=len(recipes_to_enrich)
        )
        
        enriched = []
        for recipe in recipes_to_enrich:
            try:
                enriched_recipe = await self.enrich_recipe(recipe)
                enriched.append(enriched_recipe)
            except Exception as e:
                logger.error(
                    "recipe_enrichment_failed",
                    recipe=recipe.title,
                    error=str(e)
                )
                # Return original if enrichment fails
                enriched.append(recipe)
        
        # Add non-enriched recipes (if batch limit applied)
        if batch_size and len(recipes) > batch_size:
            enriched.extend(recipes[batch_size:])
            logger.info(
                "batch_enrichment_complete",
                enriched=batch_size,
                skipped=len(recipes) - batch_size
            )
        
        return enriched
    
    def _fetch_nutrition(self, dish_name: str) -> Optional[Dict[str, Any]]:
        """
        Fetch nutrition data (try precalculated first, then computed)
        
        Args:
            dish_name: Name of the dish
            
        Returns:
            Nutrition data dict or None
        """
        # Try precalculated first (faster)
        nutrition = self.fg_client.fetch_precalculated_nutrition(dish_name)
        if nutrition:
            return nutrition
        
        # Fallback to computed nutrition
        nutrition = self.fg_client.get_nutrition(dish_name)
        if nutrition:
            return nutrition
        
        # Try fuzzy matching if exact name doesn't work
        suggestions = self.fg_client.autocomplete_dish(dish_name[:20])  # First 20 chars
        if suggestions:
            # Try the best match
            best_match = suggestions[0].get("name") or suggestions[0].get("dish_name")
            if best_match and best_match != dish_name:
                logger.debug(
                    "trying_fuzzy_match",
                    original=dish_name,
                    matched=best_match
                )
                nutrition = self.fg_client.fetch_precalculated_nutrition(best_match)
                if nutrition:
                    return nutrition
        
        logger.debug("nutrition_not_found", dish=dish_name)
        return None
    
    def _parse_nutrition(self, nutrition_data: Dict[str, Any]) -> Optional[NutritionInfo]:
        """
        Parse nutrition data from Food Graph API into NutritionInfo model
        
        Args:
            nutrition_data: Raw nutrition data from API
            
        Returns:
            NutritionInfo object or None if parsing fails
        """
        try:
            # Extract common nutrition fields (handle different API response formats)
            return NutritionInfo(
                calories=nutrition_data.get("calories") or nutrition_data.get("energy_kcal"),
                protein_g=nutrition_data.get("protein_g") or nutrition_data.get("protein"),
                carbs_g=nutrition_data.get("carbs_g") or nutrition_data.get("carbohydrate") or nutrition_data.get("carbohydrates"),
                fat_g=nutrition_data.get("fat_g") or nutrition_data.get("fat") or nutrition_data.get("total_fat"),
                fiber_g=nutrition_data.get("fiber_g") or nutrition_data.get("fiber") or nutrition_data.get("dietary_fiber"),
                sodium_mg=nutrition_data.get("sodium_mg") or nutrition_data.get("sodium"),
                sugar_g=nutrition_data.get("sugar_g") or nutrition_data.get("sugar") or nutrition_data.get("total_sugars"),
            )
        except Exception as e:
            logger.warning("nutrition_parse_error", error=str(e), data=nutrition_data)
            return None
    
    async def _enrich_ingredients(self, ingredients: List[str]) -> List[EnhancedIngredient]:
        """
        Enhance ingredient list with standardized names and nutrition data
        
        Args:
            ingredients: List of ingredient names from GraphDB
            
        Returns:
            List of EnhancedIngredient objects
        """
        enhanced = []
        
        for ing in ingredients:
            try:
                # Step 1: Standardize ingredient name (fuzzy match)
                matches = self.fg_client.nearest_ingredient(ing, k=1)
                standardized_name = matches[0] if matches else ing
                
                # Step 2: Get nutrition per 100g
                ing_nutrition_data = self.fg_client.get_ingredient_nutrition(standardized_name)
                ing_nutrition = None
                if ing_nutrition_data:
                    ing_nutrition = self._parse_nutrition(ing_nutrition_data)
                
                # Create enhanced ingredient
                enhanced_ing = EnhancedIngredient(
                    name=ing,
                    standardized_name=standardized_name if standardized_name != ing else None,
                    nutrition_per_100g=ing_nutrition
                )
                enhanced.append(enhanced_ing)
                
                logger.debug(
                    "ingredient_enriched",
                    original=ing,
                    standardized=standardized_name,
                    has_nutrition=ing_nutrition is not None
                )
                
            except Exception as e:
                logger.warning(
                    "ingredient_enrichment_failed",
                    ingredient=ing,
                    error=str(e)
                )
                # Add basic ingredient on error
                enhanced.append(EnhancedIngredient(name=ing))
        
        return enhanced
    
    def enrich_with_autocomplete(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Get autocomplete suggestions for a query
        
        Args:
            query: Partial dish name
            top_k: Number of suggestions to return
            
        Returns:
            List of suggestions with scores
        """
        if not settings.enable_autocomplete:
            return []
        
        try:
            suggestions = self.fg_client.autocomplete_dish(query)
            return suggestions[:top_k]
        except Exception as e:
            logger.warning("autocomplete_error", query=query, error=str(e))
            return []


# Singleton instance
_recipe_enricher: Optional[RecipeEnricher] = None


def get_recipe_enricher(food_graph_client: Optional[FoodGraphClient] = None) -> RecipeEnricher:
    """Get or create singleton RecipeEnricher instance"""
    global _recipe_enricher
    if _recipe_enricher is None:
        from .food_graph_client import get_food_graph_client
        fg_client = food_graph_client or get_food_graph_client()
        _recipe_enricher = RecipeEnricher(fg_client)
    return _recipe_enricher
