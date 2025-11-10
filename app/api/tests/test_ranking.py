"""
Unit tests for Ranking System
Tests recipe scoring and filtering logic
"""
import pytest
from models import Recipe, QueryConstraints
from ranking import (
    rank_recipes,
    score_recipe,
    verify_exclusions,
    calculate_ingredient_overlap,
    calculate_title_relevance
)


def create_test_recipe(
    iri="http://test/recipe/1",
    title="Test Recipe",
    ingredients=None,
    instructions=None
):
    """Helper to create test recipes"""
    return Recipe(
        iri=iri,
        title=title,
        ingredients=ingredients or [],
        instructions=instructions
    )


def test_exclusion_verification():
    """Test that exclusions are properly detected"""
    recipe = create_test_recipe(ingredients=["chicken", "banana", "rice"])
    
    # Should pass (no banana exclusion)
    assert verify_exclusions(recipe, []) is True
    
    # Should fail (contains banana)
    assert verify_exclusions(recipe, ["banana"]) is False
    
    # Should pass (no apple)
    assert verify_exclusions(recipe, ["apple"]) is True


def test_ingredient_overlap():
    """Test ingredient overlap scoring"""
    recipe = create_test_recipe(ingredients=["chicken", "onion", "garlic"])
    
    # Perfect match
    score1 = calculate_ingredient_overlap(recipe, ["chicken", "onion"])
    assert score1 == 1.0
    
    # Partial match
    score2 = calculate_ingredient_overlap(recipe, ["chicken", "banana"])
    assert 0 < score2 < 1.0
    
    # No match
    score3 = calculate_ingredient_overlap(recipe, ["banana", "apple"])
    assert score3 == 0.0


def test_title_relevance():
    """Test title relevance scoring"""
    recipe = create_test_recipe(title="Chicken Curry")
    
    # Match in title
    score1 = calculate_title_relevance(recipe, ["chicken"])
    assert score1 > 0
    
    # No match
    score2 = calculate_title_relevance(recipe, ["banana"])
    assert score2 == 0.0


def test_recipe_scoring():
    """Test overall recipe scoring"""
    recipe = create_test_recipe(
        title="Chicken Curry",
        ingredients=["chicken", "onion", "tomato"],
        instructions="Cook chicken with dum cook method"
    )
    
    constraints = QueryConstraints(
        include=["chicken", "onion"],
        keywords=["dum cook"]
    )
    
    score = score_recipe(recipe, constraints)
    
    # Should have positive score
    assert score > 0
    assert score <= 1.0


def test_ranking_order():
    """Test that recipes are ranked by relevance"""
    recipe1 = create_test_recipe(
        iri="r1",
        title="Chicken Curry",
        ingredients=["chicken", "onion"]
    )
    recipe2 = create_test_recipe(
        iri="r2",
        title="Banana Bread",
        ingredients=["banana", "flour"]
    )
    recipe3 = create_test_recipe(
        iri="r3",
        title="Chicken Biryani",
        ingredients=["chicken", "rice", "onion"]
    )
    
    recipes = [recipe1, recipe2, recipe3]
    constraints = QueryConstraints(include=["chicken", "onion"])
    
    ranked = rank_recipes(recipes, constraints)
    
    # Chicken Biryani should rank highest (more ingredient matches)
    assert ranked[0].iri == "r3"
    # Banana Bread should rank lowest
    assert ranked[-1].iri == "r2"


def test_exclusion_filtering():
    """Test that recipes with exclusions are filtered out"""
    recipe1 = create_test_recipe(
        iri="r1",
        ingredients=["chicken", "onion"]
    )
    recipe2 = create_test_recipe(
        iri="r2",
        ingredients=["chicken", "banana"]
    )
    
    recipes = [recipe1, recipe2]
    constraints = QueryConstraints(
        include=["chicken"],
        exclude=["banana"]
    )
    
    ranked = rank_recipes(recipes, constraints)
    
    # Only recipe1 should remain
    assert len(ranked) == 1
    assert ranked[0].iri == "r1"


def test_keyword_bonus():
    """Test keyword bonus scoring"""
    recipe_with_keyword = create_test_recipe(
        ingredients=["chicken"],
        instructions="Cook using dum cook method"
    )
    recipe_without_keyword = create_test_recipe(
        ingredients=["chicken"],
        instructions="Cook normally"
    )
    
    constraints = QueryConstraints(
        include=["chicken"],
        keywords=["dum cook"]
    )
    
    score1 = score_recipe(recipe_with_keyword, constraints)
    score2 = score_recipe(recipe_without_keyword, constraints)
    
    # Recipe with keyword should score higher
    assert score1 > score2


def test_empty_recipes():
    """Test ranking with empty recipe list"""
    recipes = []
    constraints = QueryConstraints(include=["chicken"])
    
    ranked = rank_recipes(recipes, constraints)
    
    assert ranked == []


def test_score_attachment():
    """Test that scores are attached to recipes"""
    recipe = create_test_recipe(ingredients=["chicken"])
    recipes = [recipe]
    constraints = QueryConstraints(include=["chicken"])
    
    ranked = rank_recipes(recipes, constraints)
    
    assert ranked[0].score is not None
    assert 0 <= ranked[0].score <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
