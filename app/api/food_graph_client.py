"""
Food Graph API Client
Integrates with the MongoDB-backed nutrition and ingredient API
"""
import httpx
from typing import Dict, List, Any, Optional
import structlog
from .config import settings

logger = structlog.get_logger()


class FoodGraphClient:
    """Client for Food Graph API (nutrition, ingredients, units)"""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.food_graph_api_url
        self.client = httpx.Client(
            timeout=httpx.Timeout(30.0),
            follow_redirects=True
        )
        logger.info("food_graph_client_initialized", base_url=self.base_url)
    
    def __del__(self):
        """Cleanup HTTP client"""
        try:
            self.client.close()
        except:
            pass
    
    # ========== Nutrition Endpoints ==========
    
    def get_nutrition(self, dish_name: str) -> Optional[Dict[str, Any]]:
        """
        Get nutrition information for a dish
        
        Args:
            dish_name: Name of the dish
            
        Returns:
            Nutrition data dict or None if not found
        """
        try:
            logger.debug("fetching_nutrition", dish=dish_name)
            response = self.client.post(
                f"{self.base_url}/api/nutrition",
                json={"dish_name": dish_name}
            )
            response.raise_for_status()
            data = response.json()
            logger.info("nutrition_fetched", dish=dish_name, has_data=bool(data))
            return data
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.debug("nutrition_not_found", dish=dish_name)
            else:
                logger.warning("nutrition_fetch_error", dish=dish_name, status=e.response.status_code)
            return None
        except Exception as e:
            logger.warning("nutrition_fetch_failed", dish=dish_name, error=str(e))
            return None
    
    def fetch_precalculated_nutrition(self, dish_name: str) -> Optional[Dict[str, Any]]:
        """
        Fetch pre-computed nutrition data (faster than get_nutrition)
        
        Args:
            dish_name: Name of the dish
            
        Returns:
            Pre-calculated nutrition data or None if not available
        """
        try:
            logger.debug("fetching_precalc_nutrition", dish=dish_name)
            response = self.client.post(
                f"{self.base_url}/api/fetch_nutrition",
                json={"dish_name": dish_name}
            )
            response.raise_for_status()
            data = response.json()
            logger.info("precalc_nutrition_fetched", dish=dish_name)
            return data
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.debug("precalc_nutrition_not_found", dish=dish_name)
            else:
                logger.warning("precalc_nutrition_error", dish=dish_name, status=e.response.status_code)
            return None
        except Exception as e:
            logger.warning("precalc_nutrition_failed", dish=dish_name, error=str(e))
            return None
    
    def get_aggregated_nutrition(self, dishes: List[str]) -> Optional[Dict[str, Any]]:
        """
        Get aggregated nutrition for multiple dishes
        
        Args:
            dishes: List of dish names
            
        Returns:
            Combined nutrition data or None on error
        """
        try:
            logger.debug("fetching_agg_nutrition", count=len(dishes))
            response = self.client.post(
                f"{self.base_url}/api/agg_nutrition",
                json={"dishes": dishes}
            )
            response.raise_for_status()
            data = response.json()
            logger.info("agg_nutrition_fetched", dish_count=len(dishes))
            return data
        except Exception as e:
            logger.warning("agg_nutrition_failed", dishes=dishes, error=str(e))
            return None
    
    def get_precalculated_sources(self) -> List[str]:
        """
        Get all unique sources from precalculated nutrition data
        
        Returns:
            List of source names
        """
        try:
            response = self.client.get(f"{self.base_url}/api/get_precalculated_sources")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning("sources_fetch_failed", error=str(e))
            return []
    
    # ========== Ingredient Endpoints ==========
    
    def get_ingredient_mapping(self, dish_name: str) -> Optional[Dict[str, Any]]:
        """
        Get ingredient mapping for a dish
        
        Args:
            dish_name: Name of the dish
            
        Returns:
            Structured ingredient list or None
        """
        try:
            logger.debug("fetching_ingredients", dish=dish_name)
            response = self.client.post(
                f"{self.base_url}/api/ingredients",
                json={"dish_name": dish_name}
            )
            response.raise_for_status()
            data = response.json()
            logger.info("ingredients_fetched", dish=dish_name)
            return data
        except Exception as e:
            logger.warning("ingredients_fetch_failed", dish=dish_name, error=str(e))
            return None
    
    def get_ingredient_nutrition(self, ingredient: str) -> Optional[Dict[str, Any]]:
        """
        Get nutrition per 100g for a single ingredient
        
        Args:
            ingredient: Ingredient name
            
        Returns:
            Nutrition data per 100g or None
        """
        try:
            logger.debug("fetching_ingredient_nutrition", ingredient=ingredient)
            response = self.client.post(
                f"{self.base_url}/api/ingredient_nutrition",
                json={"ingredient_name": ingredient}
            )
            response.raise_for_status()
            data = response.json()
            logger.info("ingredient_nutrition_fetched", ingredient=ingredient)
            return data
        except Exception as e:
            logger.warning("ingredient_nutrition_failed", ingredient=ingredient, error=str(e))
            return None
    
    def nearest_ingredient(self, ingredient: str, k: int = 5) -> List[str]:
        """
        Find top-k closest matching ingredients (fuzzy search)
        
        Args:
            ingredient: Ingredient name (can have typos)
            k: Number of matches to return (default: 5)
            
        Returns:
            List of closest matching ingredient names
        """
        try:
            logger.debug("finding_nearest_ingredient", ingredient=ingredient, k=k)
            response = self.client.post(
                f"{self.base_url}/api/nearest_ingredient",
                params={"k": k},
                json={"ingredient_name": ingredient}
            )
            response.raise_for_status()
            matches = response.json()
            logger.info("nearest_ingredients_found", ingredient=ingredient, count=len(matches))
            return matches
        except Exception as e:
            logger.warning("nearest_ingredient_failed", ingredient=ingredient, error=str(e))
            return []
    
    # ========== Unit Conversion Endpoints ==========
    
    def convert_to_grams(self, ingredient_string: str) -> Optional[Dict[str, Any]]:
        """
        Convert natural language ingredient string to grams
        
        Args:
            ingredient_string: e.g., "2 cups rice", "1 tbsp oil"
            
        Returns:
            Dict with parsed ingredient, quantity in grams
        """
        try:
            logger.debug("converting_to_grams", input=ingredient_string)
            response = self.client.post(
                f"{self.base_url}/api/nl_to_grams",
                json={"ingredient_string": ingredient_string}
            )
            response.raise_for_status()
            data = response.json()
            logger.info("converted_to_grams", input=ingredient_string, grams=data.get("grams"))
            return data
        except Exception as e:
            logger.warning("grams_conversion_failed", input=ingredient_string, error=str(e))
            return None
    
    def match_unit_and_ingredient(
        self, 
        unit: str, 
        ingredient: str, 
        quantity: float
    ) -> Optional[Dict[str, Any]]:
        """
        Use fuzzy unit matcher to convert to grams
        
        Args:
            unit: e.g., "cup", "tbsp", "kg"
            ingredient: e.g., "rice", "oil", "sugar"
            quantity: Amount (e.g., 2.0)
            
        Returns:
            Dict with matched unit, ingredient, conversion value
        """
        try:
            logger.debug("matching_unit", unit=unit, ingredient=ingredient, quantity=quantity)
            response = self.client.post(
                f"{self.base_url}/api/unit_and_ingredient_to_grams",
                json={
                    "unit": unit,
                    "ingredient": ingredient,
                    "quantity": quantity
                }
            )
            response.raise_for_status()
            data = response.json()
            logger.info("unit_matched", unit=unit, ingredient=ingredient)
            return data
        except Exception as e:
            logger.warning("unit_match_failed", unit=unit, ingredient=ingredient, error=str(e))
            return None
    
    def get_unique_units(self) -> List[str]:
        """
        Get all available unit names in the system
        
        Returns:
            List of unit names (e.g., ["cup", "tbsp", "kg", ...])
        """
        try:
            response = self.client.get(f"{self.base_url}/api/unique_units")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning("unique_units_failed", error=str(e))
            return []
    
    # ========== Autocomplete Endpoint ==========
    
    def autocomplete_dish(self, query: str) -> List[Dict[str, Any]]:
        """
        Get dish name suggestions with matching scores
        
        Args:
            query: Partial dish name (e.g., "pane")
            
        Returns:
            List of dicts with 'name' and 'score' keys
        """
        try:
            logger.debug("autocomplete", query=query)
            response = self.client.post(
                f"{self.base_url}/api/autocomplete",
                json={"query": query}
            )
            response.raise_for_status()
            suggestions = response.json()
            logger.info("autocomplete_done", query=query, count=len(suggestions))
            return suggestions
        except Exception as e:
            logger.warning("autocomplete_failed", query=query, error=str(e))
            return []
    
    # ========== Recipes Endpoints (MongoDB data) ==========
    
    def get_all_recipes(self) -> List[Dict[str, Any]]:
        """
        Get all recipes from MongoDB
        
        Returns:
            List of recipe objects with full details
        """
        try:
            logger.debug("fetching_all_recipes")
            response = self.client.get(f"{self.base_url}/recipes")
            response.raise_for_status()
            recipes = response.json()
            logger.info("recipes_fetched", count=len(recipes))
            return recipes
        except Exception as e:
            logger.warning("recipes_fetch_failed", error=str(e))
            return []
    
    def get_recipe_by_id(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """
        Get single recipe by MongoDB _id
        
        Args:
            recipe_id: MongoDB ObjectId as string
            
        Returns:
            Recipe object or None if not found
        """
        try:
            logger.debug("fetching_recipe", recipe_id=recipe_id)
            response = self.client.get(f"{self.base_url}/recipes/{recipe_id}")
            response.raise_for_status()
            recipe = response.json()
            logger.info("recipe_fetched", recipe_id=recipe_id)
            return recipe
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.debug("recipe_not_found", recipe_id=recipe_id)
            else:
                logger.warning("recipe_fetch_error", recipe_id=recipe_id, status=e.response.status_code)
            return None
        except Exception as e:
            logger.warning("recipe_fetch_failed", recipe_id=recipe_id, error=str(e))
            return None
    
    # ========== Health Check ==========
    
    def health_check(self) -> bool:
        """
        Check if Food Graph API is healthy
        
        Returns:
            True if API is reachable and healthy
        """
        try:
            response = self.client.get(
                f"{self.base_url}/health",
                timeout=5.0
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning("food_graph_health_check_failed", error=str(e))
            return False


# Singleton instance
_food_graph_client: Optional[FoodGraphClient] = None


def get_food_graph_client() -> FoodGraphClient:
    """Get or create singleton FoodGraphClient instance"""
    global _food_graph_client
    if _food_graph_client is None:
        _food_graph_client = FoodGraphClient()
    return _food_graph_client
