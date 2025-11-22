import json
import random
import os

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'comprehensive_queries.jsonl')
RECIPES_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'updated_recipes.jsonl')

def load_metadata(recipes_file):
    cuisines = set()
    diets = set()
    courses = set()
    ingredients = set()
    
    print("Scanning recipes for metadata...")
    with open(recipes_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                if data.get('cuisine'): cuisines.add(data['cuisine'])
                if data.get('diet'): diets.add(data['diet'])
                if data.get('course'): courses.add(data['course'])
                if data.get('ingredients'):
                    # Take first 5 ingredients to avoid noise
                    for ing in data['ingredients'][:5]:
                        # Clean ingredient name roughly
                        clean_ing = ing.split(' - ')[0].split('(')[0].strip().lower()
                        if len(clean_ing) > 2:
                            ingredients.add(clean_ing)
            except:
                pass
                
    return list(cuisines), list(diets), list(courses), list(ingredients)

def generate_queries(cuisines, diets, courses, ingredients, count=5000):
    queries = []
    
    templates = [
        "recipes for {ingredient}",
        "how to cook {ingredient}",
        "{cuisine} recipes",
        "{diet} {course}",
        "{adj} {course} with {ingredient}",
        "{cuisine} {course}",
        "best {ingredient} recipe",
        "{diet} recipes for dinner",
        "easy {cuisine} dishes",
        "healthy {ingredient} meals",
        "{adj} {diet} food",
        "recipes with {ingredient} and {ingredient}",
        "{cuisine} food using {ingredient}",
        "quick {course} ideas",
        "traditional {cuisine} {course}",
        "low calorie {ingredient} recipe",
        "spicy {cuisine} food",
        "{diet} friendly {course}",
        "what to make with {ingredient}",
        "simple {ingredient} dish"
    ]
    
    adjectives = ["quick", "easy", "healthy", "spicy", "delicious", "simple", "traditional", "authentic", "low carb", "high protein"]
    
    print(f"Generating {count} queries...")
    
    seen = set()
    
    while len(queries) < count:
        template = random.choice(templates)
        
        # Fill template
        q = template
        if "{ingredient}" in q:
            q = q.replace("{ingredient}", random.choice(ingredients), 1)
        if "{ingredient}" in q: # Handle second ingredient
            q = q.replace("{ingredient}", random.choice(ingredients), 1)
        if "{cuisine}" in q:
            q = q.replace("{cuisine}", random.choice(cuisines))
        if "{diet}" in q:
            q = q.replace("{diet}", random.choice(diets))
        if "{course}" in q:
            q = q.replace("{course}", random.choice(courses))
        if "{adj}" in q:
            q = q.replace("{adj}", random.choice(adjectives))
            
        if q not in seen:
            seen.add(q)
            queries.append({"id": str(len(queries)+1), "query": q})
            
    return queries

def main():
    cuisines, diets, courses, ingredients = load_metadata(RECIPES_FILE)
    print(f"Found {len(cuisines)} cuisines, {len(diets)} diets, {len(courses)} courses, {len(ingredients)} ingredients.")
    
    queries = generate_queries(cuisines, diets, courses, ingredients, count=10000)
    
    print(f"Writing to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for q in queries:
            f.write(json.dumps(q) + '\n')
            
    print("Done!")

if __name__ == "__main__":
    main()
