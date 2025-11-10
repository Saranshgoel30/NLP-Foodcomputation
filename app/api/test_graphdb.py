"""
Test GraphDB connection with proper authentication
"""
import httpx
from requests.auth import HTTPBasicAuth
import requests

# Credentials
GRAPHDB_URL = "http://16.170.211.162:7200"
REPOSITORY = "mmfood25_hackathon"
NAMED_GRAPH = "http://172.31.34.244/fkg"
USERNAME = "mmfood25"
PASSWORD = "acm_hackathon"

print("\n" + "="*70)
print("🔍 Testing GraphDB SPARQL Endpoint")
print("="*70)

# Test 1: Simple SPARQL query
print("\n📝 Test 1: Count all recipes")
print("-" * 70)

sparql_query = """
PREFIX : <http://172.31.34.244/fkg#>
SELECT (COUNT(?recipe) as ?count)
FROM <http://172.31.34.244/fkg>
WHERE {
  ?recipe a :FoodRecipes .
}
"""

endpoint = f"{GRAPHDB_URL}/repositories/{REPOSITORY}"
print(f"Endpoint: {endpoint}")
print(f"Username: {USERNAME}")
print(f"Repository: {REPOSITORY}")

try:
    response = requests.post(
        endpoint,
        data=sparql_query,
        headers={
            "Content-Type": "application/sparql-query",
            "Accept": "application/sparql-results+json"
        },
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        timeout=30
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS: GraphDB connection working!")
        result = response.json()
        print(f"\nResponse: {result}")
        
        # Extract count
        if 'results' in result and 'bindings' in result['results']:
            bindings = result['results']['bindings']
            if bindings:
                count = bindings[0].get('count', {}).get('value', 'Unknown')
                print(f"\n🎉 Total recipes in GraphDB: {count}")
    else:
        print(f"❌ ERROR: HTTP {response.status_code}")
        print(f"Response: {response.text[:500]}")

except Exception as e:
    print(f"❌ Exception: {e}")

# Test 2: Get sample recipes
print("\n" + "="*70)
print("📝 Test 2: Get 5 sample recipes with chicken")
print("-" * 70)

sparql_query2 = """
PREFIX : <http://172.31.34.244/fkg#>
SELECT DISTINCT ?recipe ?cuisine ?diet
FROM <http://172.31.34.244/fkg>
WHERE {
  ?recipe a :FoodRecipes .
  ?recipe :hasActualIngredients "chicken" .
  OPTIONAL { ?recipe :hasCuisine ?cuisine . }
  OPTIONAL { ?recipe :hasDiet ?diet . }
}
LIMIT 5
"""

try:
    response = requests.post(
        endpoint,
        data=sparql_query2,
        headers={
            "Content-Type": "application/sparql-query",
            "Accept": "application/sparql-results+json"
        },
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS: Query executed!")
        result = response.json()
        
        if 'results' in result and 'bindings' in result['results']:
            bindings = result['results']['bindings']
            print(f"\nFound {len(bindings)} recipes:")
            
            for i, binding in enumerate(bindings, 1):
                recipe_uri = binding.get('recipe', {}).get('value', 'Unknown')
                cuisine = binding.get('cuisine', {}).get('value', 'Unknown')
                diet = binding.get('diet', {}).get('value', 'Unknown')
                
                # Extract recipe name from URI
                recipe_name = recipe_uri.split('#')[-1] if '#' in recipe_uri else recipe_uri
                
                print(f"\n{i}. {recipe_name}")
                print(f"   Cuisine: {cuisine}")
                print(f"   Diet: {diet}")
        else:
            print("No results found")
    else:
        print(f"❌ ERROR: HTTP {response.status_code}")
        print(f"Response: {response.text[:500]}")

except Exception as e:
    print(f"❌ Exception: {e}")

# Test 3: Test exclusion query
print("\n" + "="*70)
print("📝 Test 3: Recipes with walnuts WITHOUT banana")
print("-" * 70)

sparql_query3 = """
PREFIX : <http://172.31.34.244/fkg#>
SELECT DISTINCT ?recipe
FROM <http://172.31.34.244/fkg>
WHERE {
  ?recipe :hasActualIngredients "walnuts" .
  FILTER NOT EXISTS {
    ?recipe :hasActualIngredients "banana" .
  }
}
LIMIT 5
"""

try:
    response = requests.post(
        endpoint,
        data=sparql_query3,
        headers={
            "Content-Type": "application/sparql-query",
            "Accept": "application/sparql-results+json"
        },
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS: Exclusion query works!")
        result = response.json()
        
        if 'results' in result and 'bindings' in result['results']:
            bindings = result['results']['bindings']
            print(f"\nFound {len(bindings)} recipes with walnuts (excluding banana):")
            
            for i, binding in enumerate(bindings, 1):
                recipe_uri = binding.get('recipe', {}).get('value', 'Unknown')
                recipe_name = recipe_uri.split('#')[-1] if '#' in recipe_uri else recipe_uri
                print(f"{i}. {recipe_name}")
    else:
        print(f"❌ ERROR: HTTP {response.status_code}")

except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "="*70)
print("✅ GraphDB Tests Complete!")
print("="*70 + "\n")
