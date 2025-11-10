"""
SPARQL Query Builder for MMFOOD GraphDB
Builds precise queries with strict filtering to minimize false positives
Uses patterns from MMFOOD reference queries
"""
from typing import List, Optional, Dict, Any
from models import QueryConstraints
import re


# Namespace prefixes for MMFOOD
PREFIXES = """
PREFIX fkg: <http://purl.org/foodkg#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""


def escape_sparql_string(s: str) -> str:
    """Escape special characters in SPARQL string literals"""
    s = s.replace('\\', '\\\\')
    s = s.replace('"', '\\"')
    s = s.replace('\n', '\\n')
    s = s.replace('\r', '\\r')
    return s


def parse_time_value(time_str: str) -> Optional[int]:
    """
    Extract integer minutes from time expressions
    Examples: "30 minutes" -> 30, "1 hour" -> 60, "PT30M" -> 30
    """
    time_str = time_str.lower().strip()
    
    # Try to extract number followed by "minute" or "min"
    match = re.search(r'(\d+)\s*(minute|min)', time_str)
    if match:
        return int(match.group(1))
    
    # Try to extract hours
    match = re.search(r'(\d+)\s*(hour|hr)', time_str)
    if match:
        return int(match.group(1)) * 60
    
    # Try ISO 8601 duration (PT30M)
    match = re.search(r'PT(\d+)M', time_str.upper())
    if match:
        return int(match.group(1))
    
    match = re.search(r'PT(\d+)H', time_str.upper())
    if match:
        return int(match.group(1)) * 60
    
    # Try plain number
    match = re.search(r'^(\d+)$', time_str)
    if match:
        return int(match.group(1))
    
    return None


def build_ingredient_includes(ingredients: List[str]) -> List[str]:
    """
    Build SPARQL patterns for ingredient inclusion
    Returns list of triple patterns and filters
    """
    patterns = []
    for i, ingredient in enumerate(ingredients):
        ingredient_escaped = escape_sparql_string(ingredient.lower())
        var_name = f"ingredient{i}"
        patterns.append(f"""
  ?recipe fkg:hasActualIngredients ?{var_name} .
  FILTER(CONTAINS(LCASE(STR(?{var_name})), "{ingredient_escaped}"))""")
    return patterns


def build_ingredient_excludes(ingredients: List[str]) -> List[str]:
    """
    Build SPARQL FILTER NOT EXISTS patterns for exclusions
    Critical for reducing false positives
    """
    patterns = []
    for ingredient in ingredients:
        ingredient_escaped = escape_sparql_string(ingredient.lower())
        patterns.append(f"""
  FILTER NOT EXISTS {{
    ?recipe fkg:hasActualIngredients ?excludeIng .
    FILTER(CONTAINS(LCASE(STR(?excludeIng)), "{ingredient_escaped}"))
  }}""")
    return patterns


def build_cuisine_filter(cuisines: List[str]) -> str:
    """Build filter for cuisine matching"""
    if not cuisines:
        return ""
    
    cuisine_conditions = []
    for cuisine in cuisines:
        cuisine_escaped = escape_sparql_string(cuisine.lower())
        cuisine_conditions.append(f'CONTAINS(LCASE(STR(?cuisine)), "{cuisine_escaped}")')
    
    cuisine_filter = " || ".join(cuisine_conditions)
    return f"""
  ?recipe fkg:hasCuisine ?cuisine .
  FILTER({cuisine_filter})"""


def build_diet_filter(diets: List[str]) -> str:
    """Build filter for dietary restrictions"""
    if not diets:
        return ""
    
    diet_conditions = []
    for diet in diets:
        diet_escaped = escape_sparql_string(diet.lower())
        diet_conditions.append(f'CONTAINS(LCASE(STR(?diet)), "{diet_escaped}")')
    
    diet_filter = " || ".join(diet_conditions)
    return f"""
  ?recipe fkg:hasDiet ?diet .
  FILTER({diet_filter})"""


def build_course_filter(courses: List[str]) -> str:
    """Build filter for course types"""
    if not courses:
        return ""
    
    course_conditions = []
    for course in courses:
        course_escaped = escape_sparql_string(course.lower())
        course_conditions.append(f'CONTAINS(LCASE(STR(?course)), "{course_escaped}")')
    
    course_filter = " || ".join(course_conditions)
    return f"""
  ?recipe fkg:hasCourse ?course .
  FILTER({course_filter})"""


def build_time_filter(max_cook: Optional[int], max_total: Optional[int]) -> str:
    """
    Build time constraint filters
    Parses time literals and compares numeric values
    """
    patterns = []
    
    if max_cook is not None:
        patterns.append(f"""
  OPTIONAL {{ ?recipe fkg:hasCookTime ?cookTime . }}
  BIND(
    IF(BOUND(?cookTime),
       xsd:integer(REPLACE(LCASE(STR(?cookTime)), "[^0-9]", "")),
       9999
    ) AS ?cookMinutes
  )
  FILTER(?cookMinutes <= {max_cook})""")
    
    if max_total is not None:
        patterns.append(f"""
  OPTIONAL {{ ?recipe fkg:hasTotalTime ?totalTime . }}
  BIND(
    IF(BOUND(?totalTime),
       xsd:integer(REPLACE(LCASE(STR(?totalTime)), "[^0-9]", "")),
       9999
    ) AS ?totalMinutes
  )
  FILTER(?totalMinutes <= {max_total})""")
    
    return "".join(patterns)


def build_keyword_filter(keywords: List[str]) -> str:
    """
    Build filter for keywords in instructions
    Useful for technique searches like 'dum cook', 'tandoor', etc.
    """
    if not keywords:
        return ""
    
    keyword_conditions = []
    for keyword in keywords:
        keyword_escaped = escape_sparql_string(keyword.lower())
        keyword_conditions.append(f'CONTAINS(LCASE(STR(?instructions)), "{keyword_escaped}")')
    
    keyword_filter = " || ".join(keyword_conditions)
    return f"""
  ?recipe fkg:hasInstructions ?instructions .
  FILTER({keyword_filter})"""


def build_projection() -> str:
    """
    Build SELECT projection with all recipe fields
    Returns DISTINCT results
    """
    return """
  ?recipe
  (SAMPLE(?titleVal) AS ?title)
  (SAMPLE(?urlVal) AS ?url)
  (SAMPLE(?courseVal) AS ?course)
  (SAMPLE(?cuisineVal) AS ?cuisine)
  (SAMPLE(?dietVal) AS ?diet)
  (SAMPLE(?servingsVal) AS ?servings)
  (GROUP_CONCAT(DISTINCT ?ingredientVal; separator="|") AS ?ingredients)
  (SAMPLE(?instructionsVal) AS ?instructions)
  (SAMPLE(?difficultyVal) AS ?difficulty)
  (SAMPLE(?cookTimeVal) AS ?cookTime)
  (SAMPLE(?totalTimeVal) AS ?totalTime)
"""


def build_optional_fields() -> str:
    """Build OPTIONAL patterns for all recipe fields"""
    return """
  OPTIONAL { ?recipe fkg:hasRecipeTitle ?titleVal . }
  OPTIONAL { ?recipe fkg:hasRecipeURL ?urlVal . }
  OPTIONAL { ?recipe fkg:hasCourse ?courseVal . }
  OPTIONAL { ?recipe fkg:hasCuisine ?cuisineVal . }
  OPTIONAL { ?recipe fkg:hasDiet ?dietVal . }
  OPTIONAL { ?recipe fkg:hasServings ?servingsVal . }
  OPTIONAL { ?recipe fkg:hasActualIngredients ?ingredientVal . }
  OPTIONAL { ?recipe fkg:hasInstructions ?instructionsVal . }
  OPTIONAL { ?recipe fkg:hasDifficulty ?difficultyVal . }
  OPTIONAL { ?recipe fkg:hasCookTime ?cookTimeVal . }
  OPTIONAL { ?recipe fkg:hasTotalTime ?totalTimeVal . }
"""


def build_sparql_query(
    constraints: QueryConstraints,
    limit: int = 50,
    named_graph: str = "http://172.31.34.244/fkg"
) -> str:
    """
    Main function to build complete SPARQL query from constraints
    
    Query structure:
    1. FROM clause with named graph
    2. Hard filters (exclusions, diet, cuisine)
    3. Ingredient includes
    4. Time constraints
    5. Keyword searches
    6. Full field projection
    7. GROUP BY and LIMIT
    """
    
    # Start building query parts
    parts = [PREFIXES]
    parts.append(f"\nSELECT DISTINCT")
    parts.append(build_projection())
    parts.append(f"FROM <{named_graph}>")
    parts.append("WHERE {")
    
    # Recipe type pattern (all recipes)
    parts.append("\n  ?recipe rdf:type fkg:Recipe .")
    
    # Add includes (ingredients that must be present)
    if constraints.include:
        parts.extend(build_ingredient_includes(constraints.include))
    
    # Add exclusions (CRITICAL: hard fail)
    if constraints.exclude:
        parts.extend(build_ingredient_excludes(constraints.exclude))
    
    # Add cuisine filter
    if constraints.cuisine:
        parts.append(build_cuisine_filter(constraints.cuisine))
    
    # Add diet filter
    if constraints.diet:
        parts.append(build_diet_filter(constraints.diet))
    
    # Add course filter
    if constraints.course:
        parts.append(build_course_filter(constraints.course))
    
    # Add time constraints
    if constraints.maxCookMinutes or constraints.maxTotalMinutes:
        parts.append(build_time_filter(
            constraints.maxCookMinutes,
            constraints.maxTotalMinutes
        ))
    
    # Add keyword search
    if constraints.keywords:
        parts.append(build_keyword_filter(constraints.keywords))
    
    # Add optional fields
    parts.append(build_optional_fields())
    
    parts.append("\n}")
    parts.append("\nGROUP BY ?recipe")
    parts.append(f"\nLIMIT {limit}")
    
    return "".join(parts)


# Convenience functions for common query patterns

def recipes_with_ingredient(ingredient: str, named_graph: str = "http://172.31.34.244/fkg") -> str:
    """Build query for single ingredient search"""
    constraints = QueryConstraints(include=[ingredient])
    return build_sparql_query(constraints, named_graph=named_graph)


def recipes_with_all(ingredients: List[str], named_graph: str = "http://172.31.34.244/fkg") -> str:
    """Build query for multiple required ingredients"""
    constraints = QueryConstraints(include=ingredients)
    return build_sparql_query(constraints, named_graph=named_graph)


def recipes_include_exclude(
    include: List[str],
    exclude: List[str],
    named_graph: str = "http://172.31.34.244/fkg"
) -> str:
    """Build query with both includes and exclusions"""
    constraints = QueryConstraints(include=include, exclude=exclude)
    return build_sparql_query(constraints, named_graph=named_graph)


def recipes_cuisine_time(
    cuisine: str,
    max_cook: Optional[int] = None,
    named_graph: str = "http://172.31.34.244/fkg"
) -> str:
    """Build query for cuisine with time constraint"""
    constraints = QueryConstraints(
        cuisine=[cuisine],
        maxCookMinutes=max_cook
    )
    return build_sparql_query(constraints, named_graph=named_graph)


def recipes_with_keyword_in_instructions(
    keyword: str,
    named_graph: str = "http://172.31.34.244/fkg"
) -> str:
    """Build query for technique/keyword in instructions"""
    constraints = QueryConstraints(keywords=[keyword])
    return build_sparql_query(constraints, named_graph=named_graph)
