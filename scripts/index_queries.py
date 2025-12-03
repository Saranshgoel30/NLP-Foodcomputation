import sys
import os
import json
import typesense

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.search_client import SearchClient

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'comprehensive_queries.jsonl')
PROGRESS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.queries_progress')

def load_progress():
    """Load the last indexed line number from progress file."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            try:
                return int(f.read().strip())
            except:
                return 0
    return 0

def save_progress(line_num):
    """Save the current progress to file."""
    with open(PROGRESS_FILE, 'w') as f:
        f.write(str(line_num))

def clear_progress():
    """Clear progress file when done."""
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)

def load_queries(file_path, start_line=0):
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f):
            if line_num < start_line:
                continue
            if line.strip():
                yield line_num, json.loads(line)

def main():
    print("Initializing Search Client...", flush=True)
    client = SearchClient()
    
    # Define schema for queries
    schema = {
        'name': 'queries',
        'fields': [
            {'name': 'query', 'type': 'string'},
            {'name': 'embedding', 'type': 'float[]', 'num_dim': 768, 'optional': True}
        ]
    }
    
    try:
        client.client.collections['queries'].retrieve()
        print("Collection 'queries' exists.", flush=True)
    except:
        print("Creating collection 'queries'...", flush=True)
        client.client.collections.create(schema)
    
    # Check for resume point
    start_line = load_progress()
    if start_line > 0:
        print(f"Resuming from line {start_line}...", flush=True)
        
    print(f"Reading from {DATA_FILE}...", flush=True)
    
    batch = []
    count = start_line
    last_line = start_line
    
    for line_num, item in load_queries(DATA_FILE, start_line):
        # Generate embedding for the query text
        embedding = client.generate_embedding(item['query'])
        if embedding:
            item['embedding'] = embedding
        batch.append(item)
        last_line = line_num + 1
        
        if len(batch) >= 100:
            client.client.collections['queries'].documents.import_(batch, {'action': 'upsert'})
            count += len(batch)
            save_progress(last_line)
            print(f"Indexed {count} queries (line {last_line})...", flush=True)
            batch = []
            
    if batch:
        client.client.collections['queries'].documents.import_(batch, {'action': 'upsert'})
        count += len(batch)
        save_progress(last_line)
        
    print(f"Done! Total queries indexed: {count}", flush=True)
    clear_progress()

if __name__ == "__main__":
    main()
