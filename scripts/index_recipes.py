"""
Indexer Script.
Reads from data/updated_recipes.jsonl and indexes to Typesense using the SearchClient.
"""

import sys
import os
import json
import time
from typing import List, Dict, Any

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.search_client import SearchClient

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'updated_recipes.jsonl')

def load_recipes_generator(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def parse_instructions(instructions_data):
    """Parse instructions into a list of strings."""
    if not instructions_data:
        return []
    
    # If it's already a list
    if isinstance(instructions_data, list):
        result = []
        for item in instructions_data:
            if isinstance(item, dict):
                # Extract 'instructions' key from dict
                step = item.get('instructions', str(item))
            else:
                step = str(item)
            result.append(step.strip())
        return result
    
    # If it's a string, split by common delimiters
    elif isinstance(instructions_data, str):
        # Try splitting by numbered patterns like "1.", "2.", etc.
        import re
        steps = re.split(r'\s*\d+\.\s*', instructions_data)
        # Remove empty strings and strip whitespace
        return [step.strip() for step in steps if step.strip()]
    
    return []

def transform(item):
    # The JSONL data is already in a good format, just need to ensure types
    return {
        'name': item.get('name'),
        'description': item.get('description', ''),
        'instructions': parse_instructions(item.get('instructions')),
        'ingredients': item.get('ingredients', []),
        'cuisine': item.get('cuisine'),
        'course': item.get('course'),
        'diet': item.get('diet'),
        'difficulty': item.get('difficulty'),
        'prep_time': int(item.get('prep_time')) if item.get('prep_time') else 0,
        'cook_time': int(item.get('cook_time')) if item.get('cook_time') else 0,
        'total_time': int(item.get('total_time')) if item.get('total_time') else 0,
        'servings': int(item.get('servings')) if str(item.get('servings')).isdigit() else 4,
        'url': item.get('url')
    }

def main():
    print("Initializing Search Client...")
    client = SearchClient()
    client.ensure_collection()
    
    print(f"Reading from {DATA_FILE}...")
    
    batch_size = 500
    batch = []
    count = 0
    
    for raw_item in load_recipes_generator(DATA_FILE):
        doc = transform(raw_item)
        if doc:
            batch.append(doc)
            
        if len(batch) >= batch_size:
            client.index_documents(batch)
            count += len(batch)
            print(f"Indexed {count} recipes...")
            batch = []
            
    if batch:
        client.index_documents(batch)
        count += len(batch)
        
    print(f"Done! Total indexed: {count}")

if __name__ == "__main__":
    main()
