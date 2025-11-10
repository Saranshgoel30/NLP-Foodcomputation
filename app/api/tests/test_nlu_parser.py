"""
Unit tests for NLU Parser
Tests constraint extraction from natural language
"""
import pytest
from nlu_parser import (
    parse_query,
    extract_exclusions,
    extract_time_constraints,
    extract_cuisines,
    extract_diets,
    extract_courses,
    extract_keywords
)


def test_simple_ingredient():
    """Test simple ingredient extraction"""
    constraints, confidence = parse_query("chicken recipe")
    assert "chicken" in (constraints.include or [])


def test_exclusion_without():
    """Test 'without' exclusion pattern"""
    exclusions = extract_exclusions("recipe without banana")
    assert "banana" in exclusions


def test_exclusion_no():
    """Test 'no' exclusion pattern"""
    exclusions = extract_exclusions("no onion no garlic")
    assert "onion" in exclusions
    assert "garlic" in exclusions


def test_time_extraction():
    """Test time constraint extraction"""
    max_cook, max_total = extract_time_constraints("under 30 minutes")
    assert max_cook == 30
    
    max_cook, max_total = extract_time_constraints("less than 45 minutes")
    assert max_cook == 45


def test_cuisine_extraction():
    """Test cuisine type extraction"""
    cuisines = extract_cuisines("Chinese chicken recipe")
    assert "Chinese" in cuisines
    
    cuisines = extract_cuisines("North Indian dal")
    assert "North Indian" in cuisines


def test_diet_extraction():
    """Test dietary restriction extraction"""
    diets = extract_diets("Jain dal recipe")
    assert "Jain" in diets
    
    diets = extract_diets("vegan gluten-free")
    assert "Vegan" in diets
    assert "Gluten-Free" in diets


def test_course_extraction():
    """Test course type extraction"""
    courses = extract_courses("breakfast recipe")
    assert "Breakfast" in courses
    
    courses = extract_courses("main course dinner")
    assert "Main Course" in courses or "Dinner" in courses


def test_keyword_extraction():
    """Test technique keyword extraction"""
    keywords = extract_keywords("dum cook biryani")
    assert "dum cook" in keywords


def test_complex_query_1():
    """Test: 'Chinese chicken under 30 minutes'"""
    constraints, confidence = parse_query("Chinese chicken under 30 minutes")
    
    assert "chicken" in (constraints.include or [])
    assert "Chinese" in (constraints.cuisine or [])
    assert constraints.maxCookMinutes == 30
    assert confidence > 0.7


def test_complex_query_2():
    """Test: 'Jain dal without rajma'"""
    constraints, confidence = parse_query("Jain dal without rajma")
    
    assert "dal" in (constraints.include or [])
    assert "rajma" in (constraints.exclude or [])
    assert "Jain" in (constraints.diet or [])


def test_complex_query_3():
    """Test: 'brown rice recipe'"""
    constraints, confidence = parse_query("brown rice recipe")
    
    assert "brown rice" in (constraints.include or []) or "rice" in (constraints.include or [])


def test_complex_query_4():
    """Test: 'walnuts without banana'"""
    constraints, confidence = parse_query("walnuts without banana")
    
    assert "walnuts" in (constraints.include or [])
    assert "banana" in (constraints.exclude or [])


def test_no_onion_garlic():
    """Test common Indian constraint: 'no onion no garlic'"""
    constraints, confidence = parse_query("sabzi no onion no garlic")
    
    assert "onion" in (constraints.exclude or [])
    assert "garlic" in (constraints.exclude or [])


def test_multiple_exclusions():
    """Test multiple exclusions"""
    constraints, confidence = parse_query("recipe without banana, onion, and garlic")
    
    assert "banana" in (constraints.exclude or [])
    assert "onion" in (constraints.exclude or [])
    assert "garlic" in (constraints.exclude or [])


def test_time_variations():
    """Test different time expressions"""
    c1, _ = parse_query("cook time under 20 minutes")
    assert c1.maxCookMinutes == 20
    
    c2, _ = parse_query("less than 45 min")
    assert c2.maxCookMinutes == 45
    
    c3, _ = parse_query("max 60 minutes")
    assert c3.maxCookMinutes == 60


def test_confidence_scoring():
    """Test confidence scoring"""
    # Simple query should have lower confidence
    _, conf1 = parse_query("chicken")
    
    # Complex query should have higher confidence
    _, conf2 = parse_query("Chinese chicken without banana under 30 minutes")
    
    assert conf2 >= conf1


def test_empty_query():
    """Test empty query handling"""
    constraints, confidence = parse_query("")
    
    # Should not crash, return minimal constraints
    assert constraints is not None
    assert confidence <= 1.0


def test_stopword_filtering():
    """Test that stopwords are filtered"""
    constraints, _ = parse_query("give me a recipe for chicken")
    
    # "give", "me", "a", "for" should not be in includes
    includes = constraints.include or []
    assert "give" not in includes
    assert "me" not in includes
    assert "a" not in includes
    assert "for" not in includes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
