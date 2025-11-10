# SPARQL Query Patterns

This document describes the SPARQL query patterns used for querying the MMFOOD GraphDB.

## Graph Configuration

- **Endpoint**: `http://16.170.211.162:7200/repositories/mmfood_hackathon`
- **Named Graph**: `http://172.31.34.244/fkg`
- **Namespace**: `fkg: <http://purl.org/foodkg#>`

## Basic Recipe Query

```sparql
PREFIX fkg: <http://purl.org/foodkg#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT DISTINCT ?recipe ?title ?cuisine
FROM <http://172.31.34.244/fkg>
WHERE {
  ?recipe rdf:type fkg:Recipe .
  OPTIONAL { ?recipe fkg:hasRecipeTitle ?title . }
  OPTIONAL { ?recipe fkg:hasCuisine ?cuisine . }
}
LIMIT 10
```

## Ingredient Inclusion

Search for recipes containing "chicken":

```sparql
PREFIX fkg: <http://purl.org/foodkg#>

SELECT DISTINCT ?recipe ?title
FROM <http://172.31.34.244/fkg>
WHERE {
  ?recipe rdf:type fkg:Recipe .
  ?recipe fkg:hasActualIngredients ?ingredient .
  FILTER(CONTAINS(LCASE(STR(?ingredient)), "chicken"))
  OPTIONAL { ?recipe fkg:hasRecipeTitle ?title . }
}
LIMIT 50
```

## Ingredient Exclusion

Search for recipes WITHOUT "banana":

```sparql
PREFIX fkg: <http://purl.org/foodkg#>

SELECT DISTINCT ?recipe ?title
FROM <http://172.31.34.244/fkg>
WHERE {
  ?recipe rdf:type fkg:Recipe .
  FILTER NOT EXISTS {
    ?recipe fkg:hasActualIngredients ?excludeIng .
    FILTER(CONTAINS(LCASE(STR(?excludeIng)), "banana"))
  }
  OPTIONAL { ?recipe fkg:hasRecipeTitle ?title . }
}
LIMIT 50
```

## Multiple Ingredients (AND)

Search for recipes with "chicken" AND "carrot":

```sparql
PREFIX fkg: <http://purl.org/foodkg#>

SELECT DISTINCT ?recipe ?title
FROM <http://172.31.34.244/fkg>
WHERE {
  ?recipe rdf:type fkg:Recipe .
  
  ?recipe fkg:hasActualIngredients ?ing1 .
  FILTER(CONTAINS(LCASE(STR(?ing1)), "chicken"))
  
  ?recipe fkg:hasActualIngredients ?ing2 .
  FILTER(CONTAINS(LCASE(STR(?ing2)), "carrot"))
  
  OPTIONAL { ?recipe fkg:hasRecipeTitle ?title . }
}
LIMIT 50
```

## Cuisine Filter

Search for Chinese recipes:

```sparql
PREFIX fkg: <http://purl.org/foodkg#>

SELECT DISTINCT ?recipe ?title ?cuisine
FROM <http://172.31.34.244/fkg>
WHERE {
  ?recipe rdf:type fkg:Recipe .
  ?recipe fkg:hasCuisine ?cuisine .
  FILTER(CONTAINS(LCASE(STR(?cuisine)), "chinese"))
  OPTIONAL { ?recipe fkg:hasRecipeTitle ?title . }
}
LIMIT 50
```

## Diet Filter

Search for Vegetarian recipes:

```sparql
PREFIX fkg: <http://purl.org/foodkg#>

SELECT DISTINCT ?recipe ?title ?diet
FROM <http://172.31.34.244/fkg>
WHERE {
  ?recipe rdf:type fkg:Recipe .
  ?recipe fkg:hasDiet ?diet .
  FILTER(CONTAINS(LCASE(STR(?diet)), "vegetarian"))
  OPTIONAL { ?recipe fkg:hasRecipeTitle ?title . }
}
LIMIT 50
```

## Time Constraint

Search for recipes with cook time <= 30 minutes:

```sparql
PREFIX fkg: <http://purl.org/foodkg#>

SELECT DISTINCT ?recipe ?title ?cookTime
FROM <http://172.31.34.244/fkg>
WHERE {
  ?recipe rdf:type fkg:Recipe .
  OPTIONAL { ?recipe fkg:hasCookTime ?cookTime . }
  BIND(
    IF(BOUND(?cookTime),
       xsd:integer(REPLACE(LCASE(STR(?cookTime)), "[^0-9]", "")),
       9999
    ) AS ?cookMinutes
  )
  FILTER(?cookMinutes <= 30)
  OPTIONAL { ?recipe fkg:hasRecipeTitle ?title . }
}
LIMIT 50
```

## Keyword in Instructions

Search for recipes with "dum cook" technique:

```sparql
PREFIX fkg: <http://purl.org/foodkg#>

SELECT DISTINCT ?recipe ?title ?instructions
FROM <http://172.31.34.244/fkg>
WHERE {
  ?recipe rdf:type fkg:Recipe .
  ?recipe fkg:hasInstructions ?instructions .
  FILTER(CONTAINS(LCASE(STR(?instructions)), "dum cook"))
  OPTIONAL { ?recipe fkg:hasRecipeTitle ?title . }
}
LIMIT 50
```

## Complete Recipe Details

Full projection with all fields:

```sparql
PREFIX fkg: <http://purl.org/foodkg#>

SELECT DISTINCT
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
FROM <http://172.31.34.244/fkg>
WHERE {
  ?recipe rdf:type fkg:Recipe .
  
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
}
GROUP BY ?recipe
LIMIT 50
```

## Complex Example

Jain dal without rajma, under 30 minutes:

```sparql
PREFIX fkg: <http://purl.org/foodkg#>

SELECT DISTINCT ?recipe ?title ?diet ?cookTime
FROM <http://172.31.34.244/fkg>
WHERE {
  ?recipe rdf:type fkg:Recipe .
  
  # Include: dal
  ?recipe fkg:hasActualIngredients ?ing1 .
  FILTER(CONTAINS(LCASE(STR(?ing1)), "dal"))
  
  # Exclude: rajma
  FILTER NOT EXISTS {
    ?recipe fkg:hasActualIngredients ?excludeIng .
    FILTER(CONTAINS(LCASE(STR(?excludeIng)), "rajma"))
  }
  
  # Diet: Jain
  ?recipe fkg:hasDiet ?diet .
  FILTER(CONTAINS(LCASE(STR(?diet)), "jain"))
  
  # Time: <= 30 minutes
  OPTIONAL { ?recipe fkg:hasCookTime ?cookTime . }
  BIND(
    IF(BOUND(?cookTime),
       xsd:integer(REPLACE(LCASE(STR(?cookTime)), "[^0-9]", "")),
       9999
    ) AS ?cookMinutes
  )
  FILTER(?cookMinutes <= 30)
  
  OPTIONAL { ?recipe fkg:hasRecipeTitle ?title . }
}
LIMIT 50
```

## Performance Tips

1. Always use `FROM <named_graph>` clause
2. Use `FILTER NOT EXISTS` for exclusions (more efficient)
3. Use `LCASE` and `CONTAINS` for case-insensitive matching
4. Limit results to avoid timeouts
5. Use OPTIONAL for fields that may not exist
6. Use GROUP BY with SAMPLE/GROUP_CONCAT for aggregation
