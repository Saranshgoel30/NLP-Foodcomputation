'use client';

import React from 'react';
import { Clock, Users, ChefHat } from 'lucide-react';
import type { Recipe } from '@/lib/api-client';
import { formatTime, formatServings, truncateText } from '@/lib/utils';

interface RecipeCardProps {
  recipe: Recipe;
  onClick?: () => void;
}

export function RecipeCard({ recipe, onClick }: RecipeCardProps) {
  return (
    <div
      onClick={onClick}
      className="
        bg-white rounded-lg shadow-md overflow-hidden
        hover:shadow-xl transition-shadow duration-200
        cursor-pointer border border-gray-200
      "
    >
      {/* Content */}
      <div className="p-6">
        {/* Title & Score */}
        <div className="flex items-start justify-between mb-3">
          <h3 className="text-lg font-bold text-gray-900 flex-1">
            {recipe.title || 'Untitled Recipe'}
          </h3>
          {recipe.score !== undefined && (
            <span className="ml-2 px-2 py-1 bg-primary-100 text-primary-700 text-xs font-semibold rounded-full">
              {(recipe.score * 100).toFixed(0)}%
            </span>
          )}
        </div>

        {/* Metadata */}
        <div className="flex flex-wrap gap-4 mb-4 text-sm text-gray-600">
          {recipe.cookTime && (
            <div className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              <span>{formatTime(recipe.cookTime)}</span>
            </div>
          )}
          {recipe.servings && (
            <div className="flex items-center gap-1">
              <Users className="w-4 h-4" />
              <span>{formatServings(recipe.servings)}</span>
            </div>
          )}
          {recipe.difficulty && (
            <div className="flex items-center gap-1">
              <ChefHat className="w-4 h-4" />
              <span>{recipe.difficulty}</span>
            </div>
          )}
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-2 mb-4">
          {recipe.cuisine && (
            <span className="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">
              {recipe.cuisine}
            </span>
          )}
          {recipe.diet && (
            <span className="px-3 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">
              {recipe.diet}
            </span>
          )}
          {recipe.course && (
            <span className="px-3 py-1 bg-purple-100 text-purple-700 text-xs font-medium rounded-full">
              {recipe.course}
            </span>
          )}
        </div>

        {/* Ingredients Preview */}
        {recipe.ingredients && recipe.ingredients.length > 0 && (
          <div className="mb-4">
            <p className="text-sm font-semibold text-gray-700 mb-1">Ingredients:</p>
            <p className="text-sm text-gray-600">
              {truncateText(recipe.ingredients.slice(0, 5).join(', '), 150)}
              {recipe.ingredients.length > 5 && ' ...'}
            </p>
          </div>
        )}

        {/* Instructions Preview */}
        {recipe.instructions && (
          <div>
            <p className="text-sm text-gray-600 line-clamp-3">
              {truncateText(recipe.instructions, 200)}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
