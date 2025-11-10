'use client';

import React from 'react';
import { X, Clock, Users, ChefHat, ExternalLink } from 'lucide-react';
import type { Recipe } from '@/lib/api-client';
import { formatTime, formatServings } from '@/lib/utils';

interface RecipeModalProps {
  recipe: Recipe;
  onClose: () => void;
}

export function RecipeModal({ recipe, onClose }: RecipeModalProps) {
  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="absolute inset-0 overflow-y-auto">
        <div className="flex items-center justify-center min-h-full p-4">
          <div className="relative bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="sticky top-0 bg-white border-b border-gray-200 px-8 py-6 flex items-start justify-between z-10">
              <div className="flex-1 pr-4">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  {recipe.title || 'Untitled Recipe'}
                </h2>
                <div className="flex flex-wrap gap-2">
                  {recipe.cuisine && (
                    <span className="px-3 py-1 bg-blue-100 text-blue-700 text-sm font-medium rounded-full">
                      {recipe.cuisine}
                    </span>
                  )}
                  {recipe.diet && (
                    <span className="px-3 py-1 bg-green-100 text-green-700 text-sm font-medium rounded-full">
                      {recipe.diet}
                    </span>
                  )}
                  {recipe.course && (
                    <span className="px-3 py-1 bg-purple-100 text-purple-700 text-sm font-medium rounded-full">
                      {recipe.course}
                    </span>
                  )}
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 rounded-lg hover:bg-gray-100 transition-colors flex-shrink-0"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Content */}
            <div className="px-8 py-6 space-y-6">
              {/* Metadata */}
              <div className="flex flex-wrap gap-6 pb-6 border-b border-gray-200">
                {recipe.cookTime && (
                  <div className="flex items-center gap-2">
                    <Clock className="w-5 h-5 text-gray-500" />
                    <div>
                      <p className="text-xs text-gray-500">Cook Time</p>
                      <p className="font-semibold">{formatTime(recipe.cookTime)}</p>
                    </div>
                  </div>
                )}
                {recipe.totalTime && (
                  <div className="flex items-center gap-2">
                    <Clock className="w-5 h-5 text-gray-500" />
                    <div>
                      <p className="text-xs text-gray-500">Total Time</p>
                      <p className="font-semibold">{formatTime(recipe.totalTime)}</p>
                    </div>
                  </div>
                )}
                {recipe.servings && (
                  <div className="flex items-center gap-2">
                    <Users className="w-5 h-5 text-gray-500" />
                    <div>
                      <p className="text-xs text-gray-500">Servings</p>
                      <p className="font-semibold">{formatServings(recipe.servings)}</p>
                    </div>
                  </div>
                )}
                {recipe.difficulty && (
                  <div className="flex items-center gap-2">
                    <ChefHat className="w-5 h-5 text-gray-500" />
                    <div>
                      <p className="text-xs text-gray-500">Difficulty</p>
                      <p className="font-semibold">{recipe.difficulty}</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Ingredients */}
              {recipe.ingredients && recipe.ingredients.length > 0 && (
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-4">Ingredients</h3>
                  <ul className="space-y-2">
                    {recipe.ingredients.map((ingredient, index) => (
                      <li key={index} className="flex items-start gap-3">
                        <span className="text-primary-500 mt-1">•</span>
                        <span className="text-gray-700">{ingredient}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Instructions */}
              {recipe.instructions && (
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-4">Instructions</h3>
                  <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap">
                    {recipe.instructions}
                  </div>
                </div>
              )}

              {/* External Link */}
              {recipe.url && (
                <div className="pt-6 border-t border-gray-200">
                  <a
                    href={recipe.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="
                      inline-flex items-center gap-2 px-4 py-2 
                      bg-primary-500 text-white rounded-lg
                      hover:bg-primary-600 transition-colors
                    "
                  >
                    <ExternalLink className="w-4 h-4" />
                    View Original Recipe
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
