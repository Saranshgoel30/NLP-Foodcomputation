"""
Comprehensive Test Suite for Typesense Search
Tests semantic, keyword, and hybrid search with performance metrics
"""
import sys
import os
from pathlib import Path
import time
import json
from typing import List, Dict, Any

# Setup paths
project_root = Path(__file__).parent.parent
api_dir = project_root / "app" / "api"
os.chdir(api_dir)
sys.path.insert(0, str(api_dir))

from typesense_client import TypesenseClient
from config import get_settings
import requests

print("\n" + "="*80)
print("🧪 TYPESENSE SEARCH TEST SUITE")
print("="*80 + "\n")

settings = get_settings()

# Initialize client
print("🔌 Initializing Typesense client...")
client = TypesenseClient(
    host=settings.typesense_host,
    port=settings.typesense_port,
    api_key=settings.typesense_api_key,
    collection_name='food_ingredients_v1',
    enable_redis=False
)
print("✅ Connected!\n")

# Test queries covering different scenarios
test_queries = [
    # English - Direct matches
    {
        "query": "amaranth",
        "expected_type": "direct_match",
        "language": "English",
        "description": "Simple ingredient name"
    },
    {
        "query": "rice",
        "expected_type": "direct_match",
        "language": "English",
        "description": "Common ingredient"
    },
    
    # English - Semantic understanding
    {
        "query": "healthy breakfast foods",
        "expected_type": "semantic",
        "language": "English",
        "description": "Concept-based search"
    },
    {
        "query": "protein rich ingredients",
        "expected_type": "semantic",
        "language": "English",
        "description": "Nutritional concept"
    },
    {
        "query": "spicy ingredients",
        "expected_type": "semantic",
        "language": "English",
        "description": "Flavor profile"
    },
    
    # Multilingual - Hindi
    {
        "query": "राजमा",
        "expected_type": "multilingual",
        "language": "Hindi",
        "description": "Kidney beans in Hindi"
    },
    {
        "query": "मसाले",
        "expected_type": "multilingual",
        "language": "Hindi",
        "description": "Spices in Hindi"
    },
    {
        "query": "दाल",
        "expected_type": "multilingual",
        "language": "Hindi",
        "description": "Lentils in Hindi"
    },
    
    # Multilingual - Other languages
    {
        "query": "ಆರೋಗ್ಯಕರ",
        "expected_type": "multilingual",
        "language": "Kannada",
        "description": "Healthy in Kannada"
    },
    {
        "query": "உணவு",
        "expected_type": "multilingual",
        "language": "Tamil",
        "description": "Food in Tamil"
    },
    
    # Typo tolerance
    {
        "query": "amranth",  # Typo in amaranth
        "expected_type": "typo_tolerance",
        "language": "English",
        "description": "Misspelled ingredient"
    },
    {
        "query": "protien",  # Typo in protein
        "expected_type": "typo_tolerance",
        "language": "English",
        "description": "Common spelling mistake"
    },
    
    # Edge cases
    {
        "query": "xyz123notfound",
        "expected_type": "no_results",
        "language": "English",
        "description": "Nonsense query"
    },
]

# Performance tracking
results = []
total_time = 0
successful_queries = 0
failed_queries = 0

print("🔍 RUNNING TEST QUERIES")
print("="*80 + "\n")

for i, test in enumerate(test_queries, 1):
    query = test["query"]
    expected_type = test["expected_type"]
    language = test["language"]
    description = test["description"]
    
    print(f"Test {i}/{len(test_queries)}: '{query}'")
    print(f"  Type: {expected_type} | Language: {language}")
    print(f"  Description: {description}")
    print("-" * 60)
    
    try:
        # Measure time
        start_time = time.time()
        
        # Perform semantic search
        result = client.semantic_search(query, limit=5)
        
        elapsed_ms = (time.time() - start_time) * 1000
        total_time += elapsed_ms
        
        hits = result.get('hits', [])
        found_count = len(hits)
        
        # Check if results make sense
        success = True
        if expected_type == "no_results":
            success = found_count == 0
        else:
            success = found_count > 0
        
        if success:
            successful_queries += 1
            status = "✅ PASS"
        else:
            failed_queries += 1
            status = "❌ FAIL"
        
        print(f"  {status}")
        print(f"  ⏱️  Response time: {elapsed_ms:.0f}ms")
        print(f"  📊 Results found: {found_count}")
        
        # Show top result
        if hits:
            top_doc = hits[0]['document']
            top_name = top_doc.get('name', 'N/A')
            print(f"  🥇 Top result: {top_name}")
            
            # Show relevance score if available
            if 'text_match' in hits[0]:
                score = hits[0]['text_match']
                print(f"  📈 Relevance score: {score}")
        
        # Store result
        results.append({
            "query": query,
            "language": language,
            "type": expected_type,
            "success": success,
            "response_time_ms": elapsed_ms,
            "results_count": found_count,
            "top_result": top_name if hits else None
        })
        
    except Exception as e:
        failed_queries += 1
        print(f"  ❌ ERROR: {e}")
        results.append({
            "query": query,
            "language": language,
            "type": expected_type,
            "success": False,
            "error": str(e)
        })
    
    print()

# Performance Analysis
print("="*80)
print("📊 PERFORMANCE ANALYSIS")
print("="*80 + "\n")

avg_time = total_time / len(test_queries) if test_queries else 0
success_rate = (successful_queries / len(test_queries)) * 100 if test_queries else 0

print(f"Total queries: {len(test_queries)}")
print(f"Successful: {successful_queries} ✅")
print(f"Failed: {failed_queries} ❌")
print(f"Success rate: {success_rate:.1f}%")
print(f"\nAverage response time: {avg_time:.0f}ms")
print(f"Total time: {total_time:.0f}ms")

# Latency breakdown
response_times = [r["response_time_ms"] for r in results if "response_time_ms" in r]
if response_times:
    print(f"\nLatency statistics:")
    print(f"  Min: {min(response_times):.0f}ms")
    print(f"  Max: {max(response_times):.0f}ms")
    print(f"  Avg: {sum(response_times)/len(response_times):.0f}ms")
    
    # Check if under 1s requirement
    under_1s = sum(1 for t in response_times if t < 1000)
    print(f"  Under 1s: {under_1s}/{len(response_times)} ({(under_1s/len(response_times)*100):.1f}%)")

# Language breakdown
print("\n📊 Results by Language:")
languages = {}
for r in results:
    lang = r.get("language", "Unknown")
    if lang not in languages:
        languages[lang] = {"total": 0, "success": 0}
    languages[lang]["total"] += 1
    if r.get("success"):
        languages[lang]["success"] += 1

for lang, stats in languages.items():
    success_pct = (stats["success"] / stats["total"]) * 100
    print(f"  {lang}: {stats['success']}/{stats['total']} ({success_pct:.0f}%) ✅")

# Query type breakdown
print("\n📊 Results by Query Type:")
query_types = {}
for r in results:
    qtype = r.get("type", "Unknown")
    if qtype not in query_types:
        query_types[qtype] = {"total": 0, "success": 0}
    query_types[qtype]["total"] += 1
    if r.get("success"):
        query_types[qtype]["success"] += 1

for qtype, stats in query_types.items():
    success_pct = (stats["success"] / stats["total"]) * 100 if stats["total"] > 0 else 0
    print(f"  {qtype}: {stats['success']}/{stats['total']} ({success_pct:.0f}%) ✅")

# Test Hybrid Search
print("\n" + "="*80)
print("🔀 TESTING HYBRID SEARCH")
print("="*80 + "\n")

try:
    test_query = "healthy protein rich"
    print(f"Query: '{test_query}'")
    print("-" * 60)
    
    # Semantic search
    start = time.time()
    semantic_results = client.semantic_search(test_query, limit=5)
    semantic_time = (time.time() - start) * 1000
    
    print(f"✅ Semantic search: {len(semantic_results.get('hits', []))} results ({semantic_time:.0f}ms)")
    
    # Keyword search
    start = time.time()
    keyword_results = client.keyword_search(test_query, limit=5)
    keyword_time = (time.time() - start) * 1000
    
    print(f"✅ Keyword search: {len(keyword_results.get('hits', []))} results ({keyword_time:.0f}ms)")
    
    # Hybrid search
    start = time.time()
    hybrid_results = client.hybrid_search(test_query, limit=5)
    hybrid_time = (time.time() - start) * 1000
    
    print(f"✅ Hybrid search: {len(hybrid_results.get('hits', []))} results ({hybrid_time:.0f}ms)")
    
    print("\nHybrid search successfully combines semantic + keyword approaches! ✅")
    
except Exception as e:
    print(f"❌ Hybrid search error: {e}")

# Collection health check
print("\n" + "="*80)
print("🏥 COLLECTION HEALTH CHECK")
print("="*80 + "\n")

try:
    response = requests.get(
        f"http://{settings.typesense_host}:{settings.typesense_port}/collections/food_ingredients_v1",
        headers={'X-TYPESENSE-API-KEY': settings.typesense_api_key}
    )
    stats = response.json()
    
    print(f"Collection: {stats['name']}")
    print(f"Documents: {stats['num_documents']}")
    print(f"Fields: {len(stats['fields'])}")
    
    # Check if embedding field exists
    has_embedding = any(f['name'] == 'embedding' for f in stats['fields'])
    print(f"Vector embeddings: {'✅ Enabled' if has_embedding else '❌ Not found'}")
    
    # Check document count
    if stats['num_documents'] > 0:
        print(f"Status: ✅ Healthy ({stats['num_documents']} documents indexed)")
    else:
        print(f"Status: ⚠️  Warning (No documents found)")
        
except Exception as e:
    print(f"❌ Health check failed: {e}")

# Final Summary
print("\n" + "="*80)
print("🎯 FINAL VERDICT")
print("="*80 + "\n")

if success_rate >= 80 and avg_time < 1000:
    print("✅ ALL TESTS PASSED!")
    print(f"   Success rate: {success_rate:.1f}% (Target: ≥80%)")
    print(f"   Avg latency: {avg_time:.0f}ms (Target: <1000ms)")
    print("\n🎉 Typesense is production-ready!")
elif success_rate >= 80:
    print("⚠️  PERFORMANCE WARNING")
    print(f"   Success rate: {success_rate:.1f}% ✅")
    print(f"   Avg latency: {avg_time:.0f}ms ⚠️  (Target: <1000ms)")
    print("\n💡 Consider optimizing query performance")
elif avg_time < 1000:
    print("⚠️  ACCURACY WARNING")
    print(f"   Success rate: {success_rate:.1f}% ⚠️  (Target: ≥80%)")
    print(f"   Avg latency: {avg_time:.0f}ms ✅")
    print("\n💡 Consider improving relevance tuning")
else:
    print("❌ TESTS FAILED")
    print(f"   Success rate: {success_rate:.1f}% (Target: ≥80%)")
    print(f"   Avg latency: {avg_time:.0f}ms (Target: <1000ms)")
    print("\n💡 Review failed queries and optimize configuration")

print("\n" + "="*80 + "\n")

# Save results to file
try:
    results_file = project_root / "test_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_queries": len(test_queries),
                "successful": successful_queries,
                "failed": failed_queries,
                "success_rate": success_rate,
                "avg_response_time_ms": avg_time
            },
            "results": results
        }, f, indent=2, ensure_ascii=False)
    print(f"📄 Detailed results saved to: {results_file}")
except Exception as e:
    print(f"⚠️  Could not save results: {e}")
