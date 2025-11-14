"""
Recipe Ranking System
Scores and sorts recipes to minimize false positives
Prioritizes exact matches and relevance
"""
from typing import List
import structlog
from models import Recipe, QueryConstraints

logger = structlog.get_logger()


def tokenize(text: str) -> set:
    """Convert text to lowercase tokens"""
    if not text:
        return set()
    return set(text.lower().split())


def calculate_ingredient_overlap(recipe: Recipe, query_includes: List[str]) -> float:
    """
    Calculate overlap score between recipe ingredients and query
    
    Args:
        recipe: Recipe object with ingredients
        query_includes: List of ingredient keywords from query
        
    Returns:
        Score from 0.0 to 1.0
    """
    if not query_includes or not recipe.ingredients:
        return 0.0
    
    # Tokenize recipe ingredients
    recipe_tokens = set()
    for ingredient in recipe.ingredients:
        recipe_tokens.update(tokenize(ingredient))
    
    # Count matches
    matches = 0
    for query_ingredient in query_includes:
        query_tokens = tokenize(query_ingredient)
        # Check if any query token appears in recipe tokens
        if any(qt in recipe_tokens for qt in query_tokens):
            matches += 1
    
    # Normalize by number of query ingredients
    return matches / len(query_includes)


def calculate_title_relevance(recipe: Recipe, query_includes: List[str]) -> float:
    """
    Calculate relevance score based on title match
    
    Args:
        recipe: Recipe object with title
        query_includes: List of ingredient keywords from query
        
    Returns:
        Score from 0.0 to 1.0
    """
    if not query_includes or not recipe.title:
        return 0.0
    
    title_tokens = tokenize(recipe.title)
    
    matches = 0
    for query_ingredient in query_includes:
        query_tokens = tokenize(query_ingredient)
        if any(qt in title_tokens for qt in query_tokens):
            matches += 1
    
    return matches / len(query_includes)


def calculate_keyword_bonus(recipe: Recipe, keywords: List[str]) -> float:
    """
    Bonus score for recipes containing specific keywords in instructions
    
    Args:
        recipe: Recipe object with instructions
        keywords: List of technique keywords
        
    Returns:
        Bonus score (0.0 to 0.3)
    """
    if not keywords or not recipe.instructions:
        return 0.0
    
    instructions_lower = recipe.instructions.lower()
    matches = sum(1 for kw in keywords if kw.lower() in instructions_lower)
    
    # Cap bonus at 0.3
    return min(matches * 0.1, 0.3)


def verify_exclusions(recipe: Recipe, exclusions: List[str]) -> bool:
    """
    Verify that recipe doesn't contain excluded ingredients
    This is a safety check in addition to SPARQL filters
    
    Args:
        recipe: Recipe object
        exclusions: List of excluded ingredients
        
    Returns:
        True if recipe is safe (no exclusions found), False otherwise
    """
    if not exclusions or not recipe.ingredients:
        return True
    
    # Convert ingredients to lowercase for comparison
    ingredients_lower = [ing.lower() for ing in recipe.ingredients]
    ingredients_text = " ".join(ingredients_lower)
    
    for exclusion in exclusions:
        exclusion_lower = exclusion.lower()
        # Check if exclusion appears in any ingredient
        if any(exclusion_lower in ing for ing in ingredients_lower):
            logger.warning(
                "exclusion_found_in_recipe",
                recipe_iri=recipe.iri,
                exclusion=exclusion,
                title=recipe.title
            )
            return False
        # Also check combined text
        if exclusion_lower in ingredients_text:
            logger.warning(
                "exclusion_found_in_combined",
                recipe_iri=recipe.iri,
                exclusion=exclusion
            )
            return False
    
    return True


def score_recipe(recipe: Recipe, constraints: QueryConstraints) -> float:
    """
    Calculate overall relevance score for a recipe
    
    Scoring factors:
    1. Ingredient overlap (0-0.5)
    2. Title relevance (0-0.3)
    3. Keyword bonus (0-0.2)
    
    Total possible score: 1.0
    
    Args:
        recipe: Recipe object
        constraints: Query constraints
        
    Returns:
        Relevance score from 0.0 to 1.0
    """
    score = 0.0
    
    # Ingredient overlap (most important)
    if constraints.include:
        overlap = calculate_ingredient_overlap(recipe, constraints.include)
        score += overlap * 0.5
    
    # Title relevance
    if constraints.include:
        title_rel = calculate_title_relevance(recipe, constraints.include)
        score += title_rel * 0.3
    
    # Keyword bonus
    if constraints.keywords:
        bonus = calculate_keyword_bonus(recipe, constraints.keywords)
        score += bonus * 0.2
    
    return round(score, 3)


def rank_recipes(
    recipes: List[Recipe],
    constraints: QueryConstraints
) -> List[Recipe]:
    """
    Rank and filter recipes based on relevance
    
    Process:
    1. Filter out recipes with excluded ingredients (safety check)
    2. Score remaining recipes
    3. Sort by score (descending)
    4. Attach score to each recipe
    
    Args:
        recipes: List of Recipe objects from GraphDB
        constraints: Original query constraints
        
    Returns:
        Sorted and scored list of Recipe objects
    """
    logger.info("ranking_recipes", input_count=len(recipes))
    
    # Safety filter: remove recipes with exclusions
    if constraints.exclude:
        filtered = [r for r in recipes if verify_exclusions(r, constraints.exclude)]
        removed_count = len(recipes) - len(filtered)
        if removed_count > 0:
            logger.warning(
                "recipes_filtered_by_exclusion",
                removed=removed_count,
                exclusions=constraints.exclude
            )
        recipes = filtered
    
    # Score all recipes
    for recipe in recipes:
        recipe.score = score_recipe(recipe, constraints)
    
    # Sort by score (descending)
    ranked = sorted(recipes, key=lambda r: r.score or 0.0, reverse=True)
    
    logger.info(
        "recipes_ranked",
        output_count=len(ranked),
        top_score=ranked[0].score if ranked else 0.0,
        bottom_score=ranked[-1].score if ranked else 0.0
    )
    
    return ranked
