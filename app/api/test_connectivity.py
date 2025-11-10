"""Quick test script for Food Graph API integration"""
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

import httpx

def test_food_graph_api():
    """Test Food Graph API connectivity"""
    base_url = "http://16.170.211.162:8001"
    
    print("\n" + "="*60)
    print("🔍 Testing Food Graph API Integration")
    print("="*60)
    
    try:
        # Test 1: Health Check
        print("\n1️⃣ Testing Health Endpoint...")
        client = httpx.Client(timeout=10.0)
        response = client.get(f"{base_url}/health")
        
        if response.status_code == 200:
            print("   ✅ Health Check: CONNECTED")
            print(f"   Status Code: {response.status_code}")
        else:
            print(f"   ⚠️  Health Check: HTTP {response.status_code}")
        
        # Test 2: Root Endpoint
        print("\n2️⃣ Testing Root Endpoint...")
        response = client.get(f"{base_url}/")
        if response.status_code == 200:
            print("   ✅ Root Endpoint: CONNECTED")
            data = response.json()
            print(f"   API Title: {data.get('title', 'N/A')}")
        else:
            print(f"   ⚠️  Root Endpoint: HTTP {response.status_code}")
        
        # Test 3: Autocomplete
        print("\n3️⃣ Testing Autocomplete...")
        response = client.post(
            f"{base_url}/api/autocomplete",
            json={"query": "pane"}
        )
        if response.status_code == 200:
            suggestions = response.json()
            print(f"   ✅ Autocomplete: {len(suggestions)} suggestions found")
            if suggestions:
                print(f"   First suggestion: {suggestions[0]}")
        else:
            print(f"   ⚠️  Autocomplete: HTTP {response.status_code}")
        
        # Test 4: Nutrition Endpoint
        print("\n4️⃣ Testing Nutrition Endpoint...")
        response = client.post(
            f"{base_url}/api/nutrition",
            json={"dish_name": "Paneer Butter Masala"}
        )
        if response.status_code == 200:
            nutrition = response.json()
            print("   ✅ Nutrition: Data retrieved")
            if nutrition:
                print(f"   Sample data: {list(nutrition.keys())[:3]}")
        else:
            print(f"   ⚠️  Nutrition: HTTP {response.status_code}")
        
        # Test 5: Recipes Endpoint
        print("\n5️⃣ Testing Recipes Endpoint...")
        response = client.get(f"{base_url}/recipes")
        if response.status_code == 200:
            recipes = response.json()
            print(f"   ✅ Recipes: {len(recipes)} recipes found")
        else:
            print(f"   ⚠️  Recipes: HTTP {response.status_code}")
        
        client.close()
        
        print("\n" + "="*60)
        print("✅ All Tests Completed!")
        print("="*60 + "\n")
        
        return True
        
    except httpx.ConnectError as e:
        print(f"\n❌ Connection Error: Cannot reach {base_url}")
        print(f"   Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   - Check if the API server is running")
        print("   - Verify the URL is correct")
        print("   - Check your internet connection")
        return False
    
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        return False


def test_graphdb():
    """Test GraphDB connectivity"""
    print("\n" + "="*60)
    print("🔍 Testing GraphDB Integration")
    print("="*60)
    
    graphdb_url = "http://16.170.211.162:7200"
    repository = "mmfood_hackathon"
    username = "mmfood25"
    password = "acm_hackathon"
    
    try:
        print("\n1️⃣ Testing GraphDB Connection...")
        client = httpx.Client(
            auth=(username, password),
            timeout=10.0
        )
        
        # Test SPARQL endpoint
        endpoint = f"{graphdb_url}/repositories/{repository}"
        sparql_query = """
        PREFIX : <http://172.31.34.244/fkg#>
        SELECT (COUNT(?recipe) as ?count)
        FROM <http://172.31.34.244/fkg>
        WHERE {
          ?recipe a :FoodRecipes .
        }
        """
        
        response = client.post(
            endpoint,
            headers={"Content-Type": "application/sparql-query"},
            data=sparql_query
        )
        
        if response.status_code == 200:
            print("   ✅ GraphDB: CONNECTED")
            print(f"   Status Code: {response.status_code}")
            print(f"   Repository: {repository}")
            print(f"   Response size: {len(response.text)} bytes")
        else:
            print(f"   ⚠️  GraphDB: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
        
        client.close()
        
        print("\n" + "="*60)
        print("✅ GraphDB Test Completed!")
        print("="*60 + "\n")
        
        return True
        
    except httpx.ConnectError as e:
        print(f"\n❌ Connection Error: Cannot reach GraphDB")
        print(f"   Error: {e}")
        return False
    
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        return False


if __name__ == "__main__":
    print("\n🚀 MMFOOD API Integration Tests")
    print("="*60)
    
    # Test Food Graph API
    food_graph_ok = test_food_graph_api()
    
    # Test GraphDB
    graphdb_ok = test_graphdb()
    
    # Final Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"Food Graph API:  {'✅ CONNECTED' if food_graph_ok else '❌ FAILED'}")
    print(f"GraphDB:         {'✅ CONNECTED' if graphdb_ok else '❌ FAILED'}")
    print("="*60 + "\n")
    
    if food_graph_ok and graphdb_ok:
        print("🎉 All systems operational! Ready to proceed with integration.\n")
        sys.exit(0)
    else:
        print("⚠️  Some systems are not reachable. Check the errors above.\n")
        sys.exit(1)
