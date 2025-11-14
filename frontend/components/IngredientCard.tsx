'use client';

import { useState } from 'react';
import { Globe, Tag, Award, ChevronDown, ChevronUp } from 'lucide-react';
import type { Ingredient } from '@/types';

interface IngredientCardProps {
  ingredient: Ingredient;
  rank: number;
}

export function IngredientCard({ ingredient, rank }: IngredientCardProps) {
  const [expanded, setExpanded] = useState(false);

  // Parse multilingual names from alt_labels
  const multilingualNames = ingredient.alt_labels || [];
  const displayNames = multilingualNames.slice(0, 3);
  const remainingCount = multilingualNames.length - 3;

  return (
    <div className="group relative bg-white dark:bg-gray-800 rounded-2xl shadow-md hover:shadow-2xl transition-all duration-300 overflow-hidden border border-gray-100 dark:border-gray-700">
      {/* Rank Badge */}
      <div className="absolute top-4 left-4 z-10">
        <div className="bg-gradient-to-r from-orange-500 to-red-500 text-white w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm shadow-lg">
          {rank}
        </div>
      </div>

      {/* Score Badge */}
      {ingredient.score !== undefined && (
        <div className="absolute top-4 right-4 z-10">
          <div className="bg-green-500 text-white px-3 py-1 rounded-full flex items-center gap-1 font-semibold text-sm shadow-lg">
            <Award className="w-4 h-4" />
            {(ingredient.score * 100).toFixed(0)}%
          </div>
        </div>
      )}

      {/* Card Content */}
      <div className="p-6">
        {/* Main Name */}
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3 mt-6">
          {ingredient.name}
        </h3>

        {/* Multilingual Names */}
        {displayNames.length > 0 && (
          <div className="mb-4">
            <div className="flex items-center gap-2 mb-2">
              <Globe className="w-4 h-4 text-orange-500" />
              <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                Multilingual Names
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              {displayNames.map((name, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-orange-50 dark:bg-orange-900/20 text-orange-700 dark:text-orange-400 rounded-lg text-sm font-medium"
                >
                  {name}
                </span>
              ))}
              {remainingCount > 0 && !expanded && (
                <button
                  onClick={() => setExpanded(true)}
                  className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-lg text-sm font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors flex items-center gap-1"
                >
                  +{remainingCount} more
                  <ChevronDown className="w-3 h-3" />
                </button>
              )}
            </div>

            {/* Expanded Names */}
            {expanded && multilingualNames.length > 3 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {multilingualNames.slice(3).map((name, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-orange-50 dark:bg-orange-900/20 text-orange-700 dark:text-orange-400 rounded-lg text-sm font-medium"
                  >
                    {name}
                  </span>
                ))}
                <button
                  onClick={() => setExpanded(false)}
                  className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-lg text-sm font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors flex items-center gap-1"
                >
                  Show less
                  <ChevronUp className="w-3 h-3" />
                </button>
              </div>
            )}
          </div>
        )}

        {/* Description */}
        {ingredient.description && (
          <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-2">
            {ingredient.description}
          </p>
        )}

        {/* Food Group */}
        {ingredient.food_group && (
          <div className="mb-4">
            <span className="inline-flex items-center gap-1 px-3 py-1 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 rounded-lg text-sm font-medium">
              <Tag className="w-3 h-3" />
              {ingredient.food_group}
            </span>
          </div>
        )}

        {/* Tags */}
        {ingredient.tags && ingredient.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {ingredient.tags.slice(0, 5).map((tag, idx) => (
              <span
                key={idx}
                className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded text-xs"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Nutrition Info */}
        {ingredient.nutrition && (
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="grid grid-cols-3 gap-3 text-center">
              {ingredient.nutrition.calories && (
                <div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Calories</div>
                  <div className="text-sm font-semibold text-gray-900 dark:text-white">
                    {ingredient.nutrition.calories}
                  </div>
                </div>
              )}
              {ingredient.nutrition.protein && (
                <div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Protein</div>
                  <div className="text-sm font-semibold text-gray-900 dark:text-white">
                    {ingredient.nutrition.protein}g
                  </div>
                </div>
              )}
              {ingredient.nutrition.carbs && (
                <div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Carbs</div>
                  <div className="text-sm font-semibold text-gray-900 dark:text-white">
                    {ingredient.nutrition.carbs}g
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ID (for debugging) */}
        <div className="mt-4 text-xs text-gray-400 dark:text-gray-600 font-mono">
          ID: {ingredient.id}
        </div>
      </div>

      {/* Hover Effect Border */}
      <div className="absolute inset-0 rounded-2xl border-2 border-orange-500 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
    </div>
  );
}
