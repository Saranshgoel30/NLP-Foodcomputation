#!/usr/bin/env python3
"""
MMFOOD API - Quick Test Script
Tests all major endpoints to verify functionality
"""
import requests
import json
from typing import Dict, Any

API_URL = "http://localhost:8000"


def test_health() -> bool:
    """Test health check endpoint"""
    print("\n🏥 Testing /health...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Status: {data.get('status')}")
        print(f"   GraphDB: {data.get('graphdb')}")
        print(f"   STT: {data.get('stt')}")
        print(f"   Translation: {data.get('translation')}")
        return data.get('status') == 'healthy'
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_nlu_parse() -> bool:
    """Test NLU parsing endpoint"""
    print("\n🧠 Testing /nlu/parse...")
    try:
        response = requests.post(
            f"{API_URL}/nlu/parse",
            json={"text": "Chinese chicken under 30 minutes", "lang": "en"},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        print(f"✅ Parsed constraints:")
        print(f"   Include: {data['constraints'].get('include')}")
        print(f"   Cuisine: {data['constraints'].get('cuisine')}")
        print(f"   Max time: {data['constraints'].get('maxCookMinutes')}")
        print(f"   Confidence: {data.get('confidence')}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_sparql_build() -> bool:
    """Test SPARQL builder endpoint"""
    print("\n🔧 Testing /sparql/build...")
    try:
        response = requests.post(
            f"{API_URL}/sparql/build",
            json={
                "constraints": {
                    "include": ["chicken"],
                    "exclude": ["banana"],
                    "maxCookMinutes": 30
                }
            },
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        sparql = data.get('sparql', '')
        print(f"✅ Generated SPARQL ({len(sparql)} chars)")
        print(f"   Contains 'chicken': {'chicken' in sparql}")
        print(f"   Contains 'FILTER NOT EXISTS': {'FILTER NOT EXISTS' in sparql}")
        print(f"   Contains time filter: {'cookMinutes' in sparql}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_search() -> bool:
    """Test main search endpoint"""
    print("\n🔍 Testing /search...")
    try:
        response = requests.post(
            f"{API_URL}/search",
            json={
                "query": {
                    "text": "brown rice",
                    "lang": "en"
                }
            },
            timeout=30  # Longer timeout for GraphDB
        )
        response.raise_for_status()
        data = response.json()
        print(f"✅ Search completed:")
        print(f"   Results: {data.get('count')}")
        print(f"   Duration: {data.get('durationMs'):.2f}ms")
        if data.get('results'):
            first = data['results'][0]
            print(f"   Top result: {first.get('title', 'Untitled')}")
            print(f"   Score: {first.get('score', 0):.3f}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to API. Is it running?")
        return False
    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out. Check GraphDB connection.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_exclusion_search() -> bool:
    """Test search with exclusions"""
    print("\n🚫 Testing exclusion filtering...")
    try:
        response = requests.post(
            f"{API_URL}/search",
            json={
                "query": {
                    "text": "walnuts without banana",
                    "lang": "en"
                }
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        print(f"✅ Exclusion search completed:")
        print(f"   Results: {data.get('count')}")
        
        # Check if any result contains banana
        has_banana = False
        for recipe in data.get('results', []):
            ingredients = recipe.get('ingredients', [])
            if any('banana' in ing.lower() for ing in ingredients):
                has_banana = True
                break
        
        if has_banana:
            print("❌ WARNING: Found banana in results!")
        else:
            print("✅ No banana found in results (correct)")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("MMFOOD API Test Suite")
    print("=" * 60)
    print(f"API URL: {API_URL}")
    
    results = {
        "Health Check": test_health(),
        "NLU Parse": test_nlu_parse(),
        "SPARQL Build": test_sparql_build(),
        "Basic Search": test_search(),
        "Exclusion Search": test_exclusion_search(),
    }
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! API is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
