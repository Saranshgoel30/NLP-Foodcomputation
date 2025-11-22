"""
Test LLM Integration
Quick script to test LLM-powered features
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.enhanced_query_parser import enhanced_parser


async def test_query_understanding():
    """Test LLM query understanding"""
    print("\n" + "="*70)
    print("🧪 Testing Query Understanding")
    print("="*70)
    
    test_queries = [
        "jain recipes without tomatoes",
        "pyaz aur lahsun ke bina sabzi",
        "quick pasta under 20 minutes",
        "chocolate cake no eggs",
        "spicy chicken with garlic"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        print("-" * 70)
        
        try:
            result = await enhanced_parser.parse_query(query)
            
            print(f"  Method: {result.get('parsing_method', 'Unknown')}")
            print(f"  Language: {result.get('language_detected', 'Unknown')}")
            print(f"  Dish: {result.get('dish_name', 'N/A')}")
            print(f"  Excluded: {result.get('excluded_ingredients', [])}")
            print(f"  Required: {result.get('required_ingredients', [])}")
            print(f"  Dietary: {result.get('dietary_preferences', [])}")
            print(f"  Cuisine: {result.get('cuisine_type', 'N/A')}")
            print(f"  Time: {result.get('cooking_time', 'N/A')}")
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")


async def test_translation():
    """Test translation features"""
    print("\n" + "="*70)
    print("🌍 Testing Translation")
    print("="*70)
    
    test_cases = [
        ("chicken curry", "Hindi"),
        ("chocolate cake", "Hindi"),
        ("pasta recipe", "Hindi")
    ]
    
    for text, target in test_cases:
        print(f"\n📝 Text: {text} → {target}")
        print("-" * 70)
        
        try:
            translated = await enhanced_parser.translate_from_english(text, target)
            print(f"  Original: {text}")
            print(f"  Translated: {translated}")
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")


async def test_ingredient_extraction():
    """Test smart ingredient extraction"""
    print("\n" + "="*70)
    print("🥕 Testing Ingredient Extraction")
    print("="*70)
    
    test_queries = [
        "biryani without onion",
        "jain sabzi",
        "vegan cake no eggs no dairy"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        print("-" * 70)
        
        try:
            ingredients = await enhanced_parser.extract_smart_ingredients(query)
            
            print(f"  Included: {ingredients.get('included', [])}")
            print(f"  Excluded: {ingredients.get('excluded', [])}")
            print(f"  Implied: {ingredients.get('implied', [])}")
            print(f"  Context: {ingredients.get('dietary_context', 'N/A')}")
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")


async def test_stats():
    """Display system stats"""
    print("\n" + "="*70)
    print("📊 System Stats")
    print("="*70)
    
    stats = enhanced_parser.get_stats()
    
    print(f"\n  LLM Enabled: {stats['llm_enabled']}")
    if stats['llm_enabled']:
        print(f"  Provider: {stats['llm_stats']['provider']}")
        print(f"  Model: {stats['llm_stats']['model']}")
        print(f"  Cache Size: {stats['llm_stats']['cache_size']}")
    else:
        print("  Mode: Rule-based fallback")
    
    print(f"  Rule Parser: {'✅' if stats['rule_parser_loaded'] else '❌'}")


async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🚀 LLM Integration Test Suite")
    print("="*70)
    
    # Show stats first
    await test_stats()
    
    # Test query understanding
    await test_query_understanding()
    
    # Test translation
    await test_translation()
    
    # Test ingredient extraction
    await test_ingredient_extraction()
    
    print("\n" + "="*70)
    print("✅ Tests Complete!")
    print("="*70)
    print("\nNote: Results depend on whether LLM API key is configured.")
    print("Without key: Uses rule-based fallback (still works!)")
    print("With key: Uses LLM for enhanced understanding")
    print("\nTo enable LLM: Add DEEPSEEK_API_KEY to .env file")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
