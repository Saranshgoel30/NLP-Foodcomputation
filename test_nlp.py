"""
Test NLP query parsing functionality
"""
import requests
import json

backend_url = "http://localhost:8080"

# Test queries with different NLP features
test_queries = [
    "vegetarian paneer recipes without onion",
    "quick chicken curry under 30 minutes",
    "South Indian breakfast recipes",
    "vegan desserts without dairy",
    "Punjabi food with paneer",
    "gluten-free pasta recipes",
]

print("=" * 80)
print("🧠 NLP QUERY PARSING TESTS")
print("=" * 80)

for query in test_queries:
    print(f"\n📝 Query: \"{query}\"")
    print("-" * 80)
    
    try:
        response = requests.post(
            f"{backend_url}/parse-query",
            json={"text": query, "lang": "en"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            constraints = data.get("constraints", {})
            confidence = data.get("confidence", 0)
            
            print(f"✅ Confidence: {confidence:.2%}")
            print(f"\n🎯 Extracted Constraints:")
            
            if constraints.get("include"):
                print(f"   ✓ Include: {', '.join(constraints['include'])}")
            if constraints.get("exclude"):
                print(f"   ✗ Exclude: {', '.join(constraints['exclude'])}")
            if constraints.get("cuisine"):
                print(f"   🍛 Cuisine: {', '.join(constraints['cuisine'])}")
            if constraints.get("diet"):
                print(f"   🥗 Diet: {', '.join(constraints['diet'])}")
            if constraints.get("course"):
                print(f"   🍽️  Course: {', '.join(constraints['course'])}")
            if constraints.get("maxCookMinutes"):
                print(f"   ⏱️  Max Cook Time: {constraints['maxCookMinutes']} minutes")
            
            if not any(constraints.values()):
                print(f"   (No structured constraints extracted)")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")

print("\n" + "=" * 80)
print("🔍 Now testing integrated search with NLP...")
print("=" * 80)

# Test integrated search
search_query = "vegetarian paneer without onion"
print(f"\n📝 Search Query: \"{search_query}\"")

try:
    response = requests.post(
        f"{backend_url}/search",
        json={"query": {"text": search_query, "lang": "en"}},
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        count = data.get("count", 0)
        print(f"✅ Found {count} matching recipes")
        print(f"⏱️  Search took {data.get('durationMs', 0):.0f}ms")
        
        if count > 0:
            print(f"\n📋 First 3 results:")
            for i, recipe in enumerate(data.get("results", [])[:3], 1):
                print(f"   {i}. {recipe.get('title')}")
                if recipe.get("diet"):
                    print(f"      Diet: {recipe['diet']}")
                if recipe.get("cuisine"):
                    print(f"      Cuisine: {recipe['cuisine']}")
    else:
        print(f"❌ Error: {response.status_code}")
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "=" * 80)
