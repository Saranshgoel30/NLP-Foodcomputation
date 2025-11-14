'use client';

import { Ingredient } from '@/types';
import { IngredientCard } from './IngredientCard';

interface SearchResultsProps {
  results: Ingredient[];
  loading: boolean;
}

export function SearchResults({ results, loading }: SearchResultsProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {[...Array(6)].map((_, i) => (
          <div
            key={i}
            className="h-48 rounded-2xl bg-gray-200 dark:bg-gray-800 animate-pulse"
          />
        ))}
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="text-center py-20">
        <div className="text-6xl mb-4">🔍</div>
        <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2">
          No results found
        </h3>
        <p className="text-gray-600 dark:text-gray-400">
          Try a different search term or change your filters
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {results.map((ingredient, index) => (
          <IngredientCard
            key={ingredient.id || index}
            ingredient={ingredient}
            rank={index + 1}
          />
        ))}
      </div>
    </div>
  );
}
