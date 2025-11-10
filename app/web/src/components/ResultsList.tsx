'use client';

import React from 'react';
import { RecipeCard } from './RecipeCard';
import { Loader2, AlertCircle } from 'lucide-react';
import type { Recipe } from '@/lib/api-client';

interface ResultsListProps {
  recipes: Recipe[];
  isLoading: boolean;
  error?: string | null;
  onRecipeClick: (recipe: Recipe) => void;
}

export function ResultsList({ recipes, isLoading, error, onRecipeClick }: ResultsListProps) {
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <Loader2 className="w-12 h-12 text-primary-500 animate-spin mb-4" />
        <p className="text-gray-600">Searching delicious recipes...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
        <p className="text-red-600 font-medium">{error}</p>
      </div>
    );
  }

  if (recipes.length === 0) {
    return (
      <div className="text-center py-16">
        <div className="text-6xl mb-4">🍽️</div>
        <h3 className="text-xl font-bold text-gray-900 mb-2">No recipes found</h3>
        <p className="text-gray-600">Try adjusting your search or filters</p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <p className="text-sm text-gray-600">
          Found <span className="font-bold text-gray-900">{recipes.length}</span> recipe{recipes.length !== 1 ? 's' : ''}
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {recipes.map((recipe) => (
          <RecipeCard
            key={recipe.iri}
            recipe={recipe}
            onClick={() => onRecipeClick(recipe)}
          />
        ))}
      </div>
    </div>
  );
}
