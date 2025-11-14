import type { SearchResponse, SearchFiltersType } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function searchIngredients(
  query: string,
  strategy: 'semantic' | 'keyword' | 'hybrid' = 'hybrid',
  filters?: SearchFiltersType
): Promise<SearchResponse> {
  const params = new URLSearchParams({
    text: query,
    strategy: strategy,
  });

  // Add filters if provided
  if (filters?.foodGroups && filters.foodGroups.length > 0) {
    params.append('food_groups', filters.foodGroups.join(','));
  }
  if (filters?.tags && filters.tags.length > 0) {
    params.append('tags', filters.tags.join(','));
  }

  const response = await fetch(`${API_BASE_URL}/search?${params.toString()}`);

  if (!response.ok) {
    throw new Error(`Search failed: ${response.statusText}`);
  }

  const data = await response.json();

  // Transform API response to match our SearchResponse type
  return {
    results: data.recipes || data.results || [],
    total: data.total || (data.recipes?.length || 0),
    facets: data.facets,
  };
}

export async function getHealthCheck(): Promise<{ status: string; timestamp: string }> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error('Health check failed');
  }
  return response.json();
}
