"""
Test script to examine Food Graph API response structure
"""
import requests
import json

# Fetch one recipe
response = requests.get('http://16.170.211.162:8001/recipes', params={'limit': 1})
recipes = response.json()

if recipes:
    recipe = recipes[0]
    
    print("=" * 80)
    print("RECIPE NAME:", recipe.get('name'))
    print("=" * 80)
    
    print("\n--- INGREDIENT STRUCTURE ---")
    ingredient_desc = recipe.get('ingredient_description', [])
    print(f"Type: {type(ingredient_desc)}")
    print(f"Length: {len(ingredient_desc) if isinstance(ingredient_desc, list) else 'N/A'}")
    if ingredient_desc:
        print("\nFirst section structure:")
        print(json.dumps(ingredient_desc[0], indent=2)[:500])
    
    print("\n--- INSTRUCTION STRUCTURE ---")
    instruction_desc = recipe.get('instruction_description', [])
    print(f"Type: {type(instruction_desc)}")
    print(f"Length: {len(instruction_desc) if isinstance(instruction_desc, list) else 'N/A'}")
    if instruction_desc:
        print("\nFirst section structure:")
        print(json.dumps(instruction_desc[0], indent=2)[:500])
    
    print("\n--- NUTRITION STRUCTURE ---")
    nutrition_info = recipe.get('nutritional_info', {})
    print(f"Type: {type(nutrition_info)}")
    if nutrition_info:
        print("\nKeys:", list(nutrition_info.keys()))
        print("\nFull nutrition data:")
        print(json.dumps(nutrition_info, indent=2))
    else:
        print("NO NUTRITION DATA FOUND")
    
    print("\n--- FULL RECIPE KEYS ---")
    print(recipe.keys())
