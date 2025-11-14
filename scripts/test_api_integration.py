"""
Test the integrated Typesense search API endpoint
"""
import httpx
import json

print("\n" + "="*70)
print("🧪 TESTING INTEGRATED TYPESENSE API")
print("="*70 + "\n")

# Test queries
test_queries = [
    {"text": "healthy breakfast", "lang": "en"},
    {"text": "protein rich food", "lang": "en"},
    {"text": "मसालेदार खाना", "lang": "hi"},  # Spicy food in Hindi
]

backend_url = "http://localhost:8000"

# Check if backend is running
try:
    health_response = httpx.get(f"{backend_url}/health", timeout=5)
    print("✅ Backend is running!")
    print(f"Health check: {health_response.json()}\n")
except Exception as e:
    print(f"❌ Backend is not running: {e}")
    print("\n💡 Start the backend with:")
    print("   cd app/api")
    print("   python main.py")
    print("\n" + "="*70 + "\n")
    exit(1)

# Test search endpoint
print("🔍 Testing Search Endpoint")
print("="*70 + "\n")

for i, query_data in enumerate(test_queries, 1):
    print(f"Test {i}: '{query_data['text']}' ({query_data['lang']})")
    print("-" * 50)
    
    try:
        # Prepare request
        request_data = {
            "query": query_data,
            "page": 1,
            "limit": 5
        }
        
        # Make request
        response = httpx.post(
            f"{backend_url}/search",
            json=request_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            recipes = result.get('recipes', [])
            
            print(f"✅ Success!")
            print(f"  Found: {len(recipes)} results")
            print(f"  Response time: {result.get('metadata', {}).get('duration_ms', 'N/A')}ms")
            
            if recipes:
                print(f"\n  Top results:")
                for j, recipe in enumerate(recipes[:3], 1):
                    print(f"    {j}. {recipe.get('title', 'N/A')}")
        else:
            print(f"❌ Error: Status {response.status_code}")
            print(f"  Response: {response.text[:200]}")
    
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print()

print("="*70)
print("\n🎉 Integration test complete!")
print("\n💡 If tests passed, your Typesense integration is working!")
print("="*70 + "\n")
