# Optimal Search Strategy for Recipe Discovery

## Research Findings from Typesense Documentation

### Key Parameters for Comprehensive Results:

1. **exhaustive_search: true** - Consider all variations of prefixes and typos exhaustively
2. **max_candidates: 100** - Consider top 100 prefix/typo variations (default is only 4!)
3. **drop_tokens_threshold: 0** - Don't drop query words
4. **typo_tokens_threshold: 100** - Start typo correction only after 100 results
5. **text_match_type: sum_score** - Sum field-level scores for better ranking
6. **prioritize_num_matching_fields: true** - Favor recipes matching more fields

### Multi-Stage Search Approach:

**Stage 1: Broad Keyword Search**
- Use exact keywords from query
- High per_page (250)
- Minimal filtering
- Purpose: Cast wide net

**Stage 2: Semantic Search (if needed)**
- Vector embeddings for semantic similarity
- Use when Stage 1 < 50 results
- Purpose: Find conceptually similar recipes

**Stage 3: Smart Filtering**
- LLM-based intelligent filtering
- Only for critical constraints (allergens, dietary)
- Purpose: Remove truly incompatible results

**Stage 4: Re-ranking**
- Combine text_match + semantic score
- Boost exact matches
- Purpose: Order results by relevance

### Hybrid Search Formula:
```
Final Score = (0.7 × keyword_match_score) + (0.3 × semantic_similarity_score)
```

### Why Current Approach Fails:

1. Only fetching 150 results (should fetch 250 max)
2. max_candidates=4 (default) means only considering 4 word variations
3. LLM filtering happening too early and too aggressively
4. Not using exhaustive_search for comprehensive coverage
5. Vector search limiting results unnecessarily

### Recommended Implementation:

```python
# STAGE 1: Exhaustive Keyword Search
results_stage1 = search_with_params({
    'q': query,
    'per_page': 250,  # Max allowed
    'exhaustive_search': True,  # Don't stop early
    'max_candidates': 100,  # Consider 100 variations
    'drop_tokens_threshold': 0,  # Keep all words
    'typo_tokens_threshold': 100,  # Be strict with typos initially
    'text_match_type': 'sum_score',  # Sum across fields
    'prioritize_num_matching_fields': True
})

# STAGE 2: Semantic Search (if needed)
if len(results_stage1) < 50:
    results_stage2 = vector_search(query, limit=250)
    results = merge_and_deduplicate(results_stage1, results_stage2)
else:
    results = results_stage1

# STAGE 3: Light Filtering (only critical constraints)
if has_critical_constraints(query):
    results = llm_filter_critical_only(results, constraints)

# STAGE 4: Re-rank
results = rerank_by_relevance(results, query)
```

## Expected Improvements:

- **10x more results** from exhaustive search
- **Better recall** from max_candidates=100
- **Higher precision** from hybrid keyword+semantic
- **Less false negatives** from lighter LLM filtering
- **Better ranking** from multi-factor scoring
