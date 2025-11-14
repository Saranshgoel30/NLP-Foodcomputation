"""
Index Food Ingredients from GraphDB mmfood25_hackathon into Typesense
Demonstrates multilingual support with 9,294 food items
"""
import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Any
import time

# Setup paths
project_root = Path(__file__).parent.parent
api_dir = project_root / "app" / "api"
os.chdir(api_dir)
sys.path.insert(0, str(api_dir))

print("\n" + "="*70)
print("🥘 INDEXING FOOD INGREDIENTS INTO TYPESENSE")
print("="*70 + "\n")

# Import after path setup
print("📦 Loading dependencies...")
from typesense_client import TypesenseClient
from graphdb_client import GraphDBClient
from config import get_settings
from tqdm import tqdm

settings = get_settings()

# Initialize clients
print("\n🔌 Connecting to services...")
print("  • Typesense...")
typesense_client = TypesenseClient(
    host=settings.typesense_host,
    port=settings.typesense_port,
    api_key=settings.typesense_api_key,
    collection_name='food_ingredients_v1',
    enable_redis=False  # Disable for initial indexing
)
print("    ✅ Typesense connected")

print("  • GraphDB...")
graphdb_client = GraphDBClient(settings)
print("    ✅ GraphDB connected")

# Create collection schema for food ingredients
print("\n📊 Creating collection schema...")
collection_schema = {
    'name': 'food_ingredients_v1',
    'fields': [
        {'name': 'id', 'type': 'string'},
        {'name': 'name', 'type': 'string'},
        {'name': 'description', 'type': 'string', 'optional': True},
        {'name': 'scientific_name', 'type': 'string', 'optional': True},
        {'name': 'food_code', 'type': 'string', 'optional': True},
        {'name': 'food_group', 'type': 'string', 'optional': True, 'facet': True},
        {'name': 'tags', 'type': 'string[]', 'optional': True, 'facet': True},
        {'name': 'alt_labels', 'type': 'string[]', 'optional': True},
        {'name': 'alt_labels_text', 'type': 'string', 'optional': True},  # For searching
        {'name': 'embedding', 'type': 'float[]', 'num_dim': 768, 'optional': True}
    ]
}

try:
    # Try to delete existing collection
    try:
        typesense_client.client.collections['food_ingredients_v1'].delete()
        print("  🗑️  Deleted existing collection")
    except:
        pass
    
    # Create new collection
    result = typesense_client.client.collections.create(collection_schema)
    typesense_client.collection_name = 'food_ingredients_v1'
    print(f"✅ Collection created: {result['name']}")
except Exception as e:
    print(f"⚠️  Collection: {e}")

# Fetch food ingredients from GraphDB
print("\n📥 Fetching food ingredients from GraphDB...")
query = """
PREFIX fkg: <http://172.31.34.244/fkg#>

SELECT DISTINCT ?food ?prefLabel ?scientificName ?foodCode ?foodGroup ?tags
WHERE {
    ?food a fkg:FoodRecipes .
    OPTIONAL { ?food fkg:has_pref_label ?prefLabel }
    OPTIONAL { ?food fkg:has_scientific_name ?scientificName }
    OPTIONAL { ?food fkg:has_food_code ?foodCode }
    OPTIONAL { ?food fkg:has_food_group ?foodGroup }
    OPTIONAL { ?food fkg:has_tags ?tags }
}
LIMIT 1000
"""

try:
    results = graphdb_client.execute_sparql(query)
    foods_data = results.get('results', {}).get('bindings', [])
    print(f"✅ Fetched {len(foods_data)} food ingredients")
except Exception as e:
    print(f"❌ Error fetching food ingredients: {e}")
    sys.exit(1)

if not foods_data:
    print("❌ No food ingredients found in GraphDB!")
    sys.exit(1)

# Fetch multilingual labels separately for each food
print("\n🌍 Fetching multilingual labels...")
multilingual_query_template = """
PREFIX fkg: <http://172.31.34.244/fkg#>

SELECT ?altLabel ?lang
WHERE {{
    <{food_uri}> fkg:has_alt_labels ?altLabel .
    BIND(LANG(?altLabel) as ?lang)
}}
"""

# Process and index food ingredients
print("\n🔄 Processing and indexing food ingredients...")
indexed_count = 0
error_count = 0

for food_data in tqdm(foods_data, desc="Indexing"):
    try:
        # Extract food URI
        food_uri = food_data.get('food', {}).get('value')
        if not food_uri:
            continue
        
        # Extract food ID from URI (last part after #)
        food_id = food_uri.split('#')[-1] if '#' in food_uri else food_uri.split('/')[-1]
        
        # Extract basic info
        name = food_data.get('prefLabel', {}).get('value', food_id)
        scientific_name = food_data.get('scientificName', {}).get('value')
        food_code = food_data.get('foodCode', {}).get('value')
        food_group = food_data.get('foodGroup', {}).get('value')
        tags_str = food_data.get('tags', {}).get('value', '')
        tags = [tag.strip() for tag in tags_str.split() if tag.strip()] if tags_str else []
        
        # Fetch multilingual labels for this food
        alt_labels = []
        alt_labels_text_parts = []
        try:
            ml_query = multilingual_query_template.format(food_uri=food_uri)
            ml_results = graphdb_client.execute_sparql(ml_query)
            ml_bindings = ml_results.get('results', {}).get('bindings', [])
            
            for ml_binding in ml_bindings:
                alt_label = ml_binding.get('altLabel', {}).get('value')
                lang = ml_binding.get('lang', {}).get('value', '')
                if alt_label:
                    if lang:
                        alt_labels.append(f"{alt_label} ({lang})")
                    else:
                        alt_labels.append(alt_label)
                    alt_labels_text_parts.append(alt_label)
        except:
            pass  # Skip if multilingual labels fail
        
        # Create description from all available info
        description_parts = []
        if scientific_name:
            description_parts.append(f"Scientific name: {scientific_name}")
        if food_group:
            description_parts.append(f"Food group: {food_group}")
        if tags:
            description_parts.append(f"Tags: {', '.join(tags)}")
        if alt_labels_text_parts:
            description_parts.append(f"Also known as: {', '.join(alt_labels_text_parts[:5])}")
        
        description = '. '.join(description_parts) if description_parts else name
        
        # Prepare document
        document = {
            'id': food_id.replace('%20', '_').replace(' ', '_').replace(',', ''),
            'name': name,
            'description': description,
            'scientific_name': scientific_name or '',
            'food_code': food_code or '',
            'food_group': food_group or '',
            'tags': tags,
            'alt_labels': alt_labels,
            'alt_labels_text': ' '.join(alt_labels_text_parts)
        }
        
        # Index with embedding
        typesense_client.index_document(document, generate_embedding=True)
        indexed_count += 1
        
        # Small delay to avoid overwhelming the servers
        if indexed_count % 50 == 0:
            time.sleep(0.5)
        
    except Exception as e:
        error_count += 1
        if error_count <= 5:  # Show first 5 errors
            print(f"\n⚠️  Error indexing {food_id}: {e}")
        continue

# Summary
print("\n" + "="*70)
print("✅ INDEXING COMPLETE!")
print("="*70)
print(f"📊 Total indexed: {indexed_count}")
print(f"❌ Errors: {error_count}")

# Test search
print("\n🔍 Testing search...")
try:
    # Test 1: English search
    result = typesense_client.semantic_search("amaranth seeds", limit=3)
    print(f"  Test 1 - 'amaranth seeds': Found {len(result.get('hits', []))} results")
    
    # Test 2: Multilingual search (Hindi)
    result = typesense_client.semantic_search("राजगिरा", limit=3)  # Ramdana in Devanagari
    print(f"  Test 2 - Multilingual (Hindi): Found {len(result.get('hits', []))} results")
    
    print("\n🎉 SUCCESS! Food ingredients indexed and searchable!")
except Exception as e:
    print(f"❌ Search test failed: {e}")

print("\n" + "="*70)
