export interface Ingredient {
  id: string;
  name: string;
  alt_labels?: string[];
  alt_labels_text?: string;
  description?: string;
  food_group?: string;
  tags?: string[];
  nutrition?: {
    calories?: number;
    protein?: number;
    carbs?: number;
    fat?: number;
    fiber?: number;
  };
  image_url?: string;
  score?: number;
}

export interface SearchResponse {
  results: Ingredient[];
  total: number;
  facets?: {
    food_groups?: Record<string, number>;
    tags?: Record<string, number>;
  };
}

export interface SearchFiltersType {
  foodGroups: string[];
  tags: string[];
}
