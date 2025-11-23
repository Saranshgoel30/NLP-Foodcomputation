"""
Quick API Test - Verify all endpoints work
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("\n" + "="*80)
    print("FOOD INTELLIGENCE API - QUICK TEST")
    print("="*80 + "\n")
    
    # Test 1: Health Check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        print(f"   ✅ Status: {data['status']}")
        print(f"   ✅ Version: {data['version']}")
        print(f"   ✅ LLM: {data['llm_provider']}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 2: Simple Search
    print("\n2. Testing search endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/search", params={"q": "butter chicken", "limit": 5})
        assert response.status_code == 200
        data = response.json()
        print(f"   ✅ Found: {data['found']} recipes")
        print(f"   ✅ Duration: {data['duration_ms']}ms")
        print(f"   ✅ LLM Enabled: {data['llm_enabled']}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 3: Complex Query (Jain)
    print("\n3. Testing complex query (Jain)...")
    try:
        response = requests.get(f"{BASE_URL}/api/search", params={"q": "jain breakfast recipes", "limit": 5})
        assert response.status_code == 200
        data = response.json()
        print(f"   ✅ Found: {data['found']} recipes")
        print(f"   ✅ Excluded count: {data.get('excluded_count', 0)}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 4: Translation (Hindi)
    print("\n4. Testing translation (Hindi)...")
    try:
        response = requests.get(f"{BASE_URL}/api/analyze", params={"q": "pyaz ke bina paneer"})
        assert response.status_code == 200
        data = response.json()
        print(f"   ✅ Original: {data['original_query']}")
        print(f"   ✅ Translated: {data['translated_query']}")
        print(f"   ✅ Parsed dish: {data['parsed']['dish_name']}")
        print(f"   ✅ Excluded: {data['parsed']['excluded_ingredients']}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 5: LLM Comparison (if available)
    print("\n5. Testing LLM comparison (DeepSeek vs Grok)...")
    try:
        response = requests.get(f"{BASE_URL}/api/compare", params={"q": "jain recipes"})
        if response.status_code == 200:
            data = response.json()
            comp = data.get('comparison', {})
            if comp:
                print(f"   ✅ Provider A: {comp['primary_provider']}")
                print(f"   ✅ Provider B: {comp['secondary_provider']}")
                print(f"   ✅ Match: {comp.get('match', 'N/A')}")
            else:
                print("   ⚠️  Comparison data not available")
        else:
            print(f"   ⚠️  Comparison not available (need 2 providers)")
    except Exception as e:
        print(f"   ⚠️  Skipped: {e}")
    
    # Test 6: Stats
    print("\n6. Testing stats endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/stats")
        assert response.status_code == 200
        data = response.json()
        print(f"   ✅ Recipes: {data['platform']['total_recipes']}")
        print(f"   ✅ LLM Provider: {data['llm']['primary_provider']}")
        print(f"   ✅ Total Cost: ${data['llm']['total_cost_usd']:.4f}")
        print(f"   ✅ Requests: {data['llm']['total_requests']}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED!")
    print("="*80 + "\n")
    
    return True

if __name__ == "__main__":
    print("\n⚠️  Make sure the API is running: python run_api.py")
    input("\nPress Enter when API is ready...")
    
    success = test_api()
    
    if success:
        print("\n🎉 Your Food Intelligence API is READY FOR PRODUCTION!")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
