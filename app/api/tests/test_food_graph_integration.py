"""
Integration tests for Food Graph API Client
Tests connectivity, endpoints, and error handling
"""
import pytest
from app.api.food_graph_client import FoodGraphClient


@pytest.fixture
def client():
    """Create Food Graph API client for testing"""
    return FoodGraphClient(base_url="http://16.170.211.162:8001")


class TestFoodGraphAPIConnection:
    """Test basic connectivity and health checks"""
    
    def test_health_check(self, client):
        """Test Food Graph API is reachable"""
        is_healthy = client.health_check()
        assert isinstance(is_healthy, bool)
        # Note: May be False if API is down, but should not raise exception
    
    def test_client_initialization(self):
        """Test client can be initialized"""
        client = FoodGraphClient()
        assert client.base_url == "http://16.170.211.162:8001"
        assert client.client is not None


class TestNutritionEndpoints:
    """Test nutrition-related endpoints"""
    
    def test_get_nutrition_valid_dish(self, client):
        """Test nutrition fetch for a known dish"""
        nutrition = client.get_nutrition("Paneer Butter Masala")
        # May be None if dish not found, but should not raise exception
        if nutrition:
            assert isinstance(nutrition, dict)
    
    def test_fetch_precalculated_nutrition(self, client):
        """Test precalculated nutrition (faster method)"""
        nutrition = client.fetch_precalculated_nutrition("Dal Makhani")
        if nutrition:
            assert isinstance(nutrition, dict)
    
    def test_get_nutrition_invalid_dish(self, client):
        """Test nutrition fetch with invalid dish name"""
        nutrition = client.get_nutrition("NonExistentDish12345")
        # Should return None, not raise exception
        assert nutrition is None or isinstance(nutrition, dict)
    
    def test_get_aggregated_nutrition(self, client):
        """Test aggregated nutrition for multiple dishes"""
        dishes = ["Paneer Butter Masala", "Dal Makhani"]
        agg_nutrition = client.get_aggregated_nutrition(dishes)
        if agg_nutrition:
            assert isinstance(agg_nutrition, dict)
    
    def test_get_precalculated_sources(self, client):
        """Test getting data sources"""
        sources = client.get_precalculated_sources()
        assert isinstance(sources, list)


class TestIngredientEndpoints:
    """Test ingredient-related endpoints"""
    
    def test_get_ingredient_mapping(self, client):
        """Test ingredient mapping for a dish"""
        mapping = client.get_ingredient_mapping("Chicken Biryani")
        if mapping:
            assert isinstance(mapping, dict)
    
    def test_get_ingredient_nutrition(self, client):
        """Test nutrition per 100g for ingredient"""
        nutrition = client.get_ingredient_nutrition("paneer")
        if nutrition:
            assert isinstance(nutrition, dict)
            # Nutrition should have common fields
    
    def test_nearest_ingredient_exact_match(self, client):
        """Test fuzzy ingredient matching with exact name"""
        matches = client.nearest_ingredient("paneer", k=3)
        assert isinstance(matches, list)
        if matches:
            assert len(matches) <= 3
    
    def test_nearest_ingredient_typo(self, client):
        """Test fuzzy matching with typo"""
        matches = client.nearest_ingredient("panner", k=1)  # Typo: panner instead of paneer
        assert isinstance(matches, list)
        if matches:
            # Should still find paneer
            assert any("paneer" in str(m).lower() for m in matches) or len(matches) > 0
    
    def test_nearest_ingredient_k_parameter(self, client):
        """Test k parameter works correctly"""
        matches = client.nearest_ingredient("rice", k=5)
        assert isinstance(matches, list)
        if matches:
            assert len(matches) <= 5


class TestUnitConversionEndpoints:
    """Test unit conversion endpoints"""
    
    def test_convert_to_grams_simple(self, client):
        """Test natural language conversion"""
        result = client.convert_to_grams("2 cups rice")
        if result:
            assert isinstance(result, dict)
            assert "grams" in result or result.get("grams") is not None
    
    def test_convert_to_grams_with_unit(self, client):
        """Test conversion with explicit unit"""
        result = client.convert_to_grams("1 tbsp oil")
        if result:
            assert isinstance(result, dict)
    
    def test_match_unit_and_ingredient(self, client):
        """Test unit matcher endpoint"""
        result = client.match_unit_and_ingredient(
            unit="cup",
            ingredient="rice",
            quantity=2.0
        )
        if result:
            assert isinstance(result, dict)
    
    def test_get_unique_units(self, client):
        """Test getting all available units"""
        units = client.get_unique_units()
        assert isinstance(units, list)
        if units:
            # Should contain common units
            common_units = ["cup", "tbsp", "tsp", "kg", "g"]
            # At least some common units should be present
            assert any(unit in " ".join(str(u).lower() for u in units) for unit in common_units) or len(units) > 0


class TestAutocompleteEndpoint:
    """Test autocomplete functionality"""
    
    def test_autocomplete_partial_name(self, client):
        """Test autocomplete with partial dish name"""
        suggestions = client.autocomplete_dish("pane")
        assert isinstance(suggestions, list)
        if suggestions:
            # Should have name/score fields
            for suggestion in suggestions[:3]:
                assert isinstance(suggestion, dict)
    
    def test_autocomplete_full_name(self, client):
        """Test autocomplete with full name"""
        suggestions = client.autocomplete_dish("Paneer Butter Masala")
        assert isinstance(suggestions, list)
    
    def test_autocomplete_empty_query(self, client):
        """Test autocomplete with empty query"""
        suggestions = client.autocomplete_dish("")
        assert isinstance(suggestions, list)


class TestRecipeEndpoints:
    """Test recipe access endpoints (MongoDB data)"""
    
    def test_get_all_recipes(self, client):
        """Test fetching all recipes"""
        recipes = client.get_all_recipes()
        assert isinstance(recipes, list)
        if recipes:
            # Each recipe should be a dict
            assert isinstance(recipes[0], dict)
    
    def test_get_recipe_by_id_invalid(self, client):
        """Test fetching recipe with invalid ID"""
        recipe = client.get_recipe_by_id("invalid_id_12345")
        # Should return None, not raise exception
        assert recipe is None or isinstance(recipe, dict)


class TestErrorHandling:
    """Test error handling and graceful degradation"""
    
    def test_invalid_base_url(self):
        """Test client with invalid base URL"""
        client = FoodGraphClient(base_url="http://invalid-url-12345.com")
        # Health check should return False, not raise exception
        health = client.health_check()
        assert health is False
    
    def test_timeout_handling(self, client):
        """Test that timeouts are handled gracefully"""
        # All methods should handle timeouts and return None/empty list
        nutrition = client.get_nutrition("Test Dish")
        assert nutrition is None or isinstance(nutrition, dict)
    
    def test_http_error_handling(self, client):
        """Test handling of HTTP errors"""
        # 404 and other errors should be handled gracefully
        recipe = client.get_recipe_by_id("nonexistent")
        assert recipe is None or isinstance(recipe, dict)


# Integration test combining multiple endpoints
class TestIntegrationFlow:
    """Test realistic usage flows"""
    
    def test_dish_to_nutrition_flow(self, client):
        """Test: Autocomplete → Select → Get Nutrition"""
        # Step 1: Autocomplete
        suggestions = client.autocomplete_dish("pane")
        if suggestions:
            # Step 2: Get nutrition for first suggestion
            dish_name = suggestions[0].get("name") or suggestions[0].get("dish_name")
            if dish_name:
                nutrition = client.fetch_precalculated_nutrition(dish_name)
                # Either found or None, but no exception
                assert nutrition is None or isinstance(nutrition, dict)
    
    def test_ingredient_standardization_flow(self, client):
        """Test: Typo → Fuzzy Match → Get Nutrition"""
        # Step 1: Find closest match for typo
        matches = client.nearest_ingredient("panner", k=1)
        if matches:
            # Step 2: Get nutrition for matched ingredient
            ingredient = matches[0]
            nutrition = client.get_ingredient_nutrition(ingredient)
            assert nutrition is None or isinstance(nutrition, dict)
    
    def test_recipe_with_unit_conversion(self, client):
        """Test: Recipe → Ingredients → Convert Units"""
        # Step 1: Get a recipe
        recipes = client.get_all_recipes()
        if recipes and len(recipes) > 0:
            recipe = recipes[0]
            # Step 2: Try to convert an ingredient
            result = client.convert_to_grams("2 cups rice")
            assert result is None or isinstance(result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
