"""
Unit tests for SPARQL Query Builder
Tests that constraints generate correct SPARQL patterns
"""
import pytest
from models import QueryConstraints
from sparql_builder import (
    build_sparql_query,
    recipes_with_ingredient,
    recipes_include_exclude,
    parse_time_value
)


def test_basic_ingredient_query():
    """Test simple ingredient inclusion"""
    constraints = QueryConstraints(include=["chicken"])
    sparql = build_sparql_query(constraints)
    
    assert "fkg:hasActualIngredients" in sparql
    assert 'CONTAINS(LCASE(STR(?ingredient0)), "chicken")' in sparql
    assert "FROM <http://172.31.34.244/fkg>" in sparql


def test_exclusion_query():
    """Test ingredient exclusion with FILTER NOT EXISTS"""
    constraints = QueryConstraints(exclude=["banana"])
    sparql = build_sparql_query(constraints)
    
    assert "FILTER NOT EXISTS" in sparql
    assert 'CONTAINS(LCASE(STR(?excludeIng)), "banana")' in sparql


def test_multiple_includes():
    """Test AND logic for multiple ingredients"""
    constraints = QueryConstraints(include=["chicken", "carrot", "potato"])
    sparql = build_sparql_query(constraints)
    
    assert sparql.count("fkg:hasActualIngredients") >= 3
    assert "chicken" in sparql
    assert "carrot" in sparql
    assert "potato" in sparql


def test_cuisine_filter():
    """Test cuisine filtering"""
    constraints = QueryConstraints(cuisine=["Chinese", "Indian"])
    sparql = build_sparql_query(constraints)
    
    assert "fkg:hasCuisine" in sparql
    assert "chinese" in sparql.lower()
    assert "indian" in sparql.lower()


def test_diet_filter():
    """Test dietary restriction filtering"""
    constraints = QueryConstraints(diet=["Jain", "Vegetarian"])
    sparql = build_sparql_query(constraints)
    
    assert "fkg:hasDiet" in sparql
    assert "jain" in sparql.lower()
    assert "vegetarian" in sparql.lower()


def test_time_constraint():
    """Test cooking time filtering"""
    constraints = QueryConstraints(maxCookMinutes=30)
    sparql = build_sparql_query(constraints)
    
    assert "fkg:hasCookTime" in sparql
    assert "?cookMinutes <= 30" in sparql


def test_keyword_search():
    """Test keyword in instructions"""
    constraints = QueryConstraints(keywords=["dum cook", "tandoor"])
    sparql = build_sparql_query(constraints)
    
    assert "fkg:hasInstructions" in sparql
    assert "dum cook" in sparql
    assert "tandoor" in sparql


def test_complex_query():
    """Test complex query with multiple constraints"""
    constraints = QueryConstraints(
        include=["dal"],
        exclude=["rajma"],
        diet=["Jain"],
        maxCookMinutes=30
    )
    sparql = build_sparql_query(constraints)
    
    # Should include all parts
    assert "dal" in sparql
    assert "FILTER NOT EXISTS" in sparql
    assert "rajma" in sparql
    assert "jain" in sparql.lower()
    assert "?cookMinutes <= 30" in sparql


def test_time_parsing():
    """Test time value extraction"""
    assert parse_time_value("30 minutes") == 30
    assert parse_time_value("1 hour") == 60
    assert parse_time_value("PT30M") == 30
    assert parse_time_value("45") == 45
    assert parse_time_value("invalid") is None


def test_convenience_functions():
    """Test convenience wrapper functions"""
    sparql1 = recipes_with_ingredient("brown rice")
    assert "brown rice" in sparql1
    
    sparql2 = recipes_include_exclude(["walnuts"], ["banana"])
    assert "walnuts" in sparql2
    assert "banana" in sparql2
    assert "FILTER NOT EXISTS" in sparql2


def test_escaping():
    """Test special character escaping"""
    constraints = QueryConstraints(include=["chicken's"])
    sparql = build_sparql_query(constraints)
    # Should not break SPARQL syntax
    assert "chicken" in sparql


def test_limit():
    """Test LIMIT clause"""
    constraints = QueryConstraints(include=["chicken"])
    sparql = build_sparql_query(constraints, limit=10)
    
    assert "LIMIT 10" in sparql


def test_named_graph():
    """Test custom named graph"""
    constraints = QueryConstraints(include=["chicken"])
    custom_graph = "http://example.org/custom"
    sparql = build_sparql_query(constraints, named_graph=custom_graph)
    
    assert f"FROM <{custom_graph}>" in sparql


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
