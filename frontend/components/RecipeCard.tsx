'use client'

import { ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'

interface Recipe {
  name: string
  description?: string
  ingredients: string[]
  cuisine?: string
  course?: string
  diet?: string
  total_time?: number
  prep_time?: number
  cook_time?: number
  servings?: number
  url?: string
  instructions?: any
}

export default function RecipeCard({ recipe, index }: { recipe: Recipe; index: number }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="bg-white rounded-2xl border-2 border-gray-200 shadow-lg hover:shadow-2xl hover:border-purple-300 transition-all duration-300 overflow-hidden">
      {/* Card Header */}
      <div className="p-6">
        <h3 className="text-2xl font-bold text-gray-900 mb-3">
          {index}. {recipe.name}
        </h3>

        {/* Badges */}
        <div className="flex flex-wrap gap-2 mb-4">
          {recipe.cuisine && (
            <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-semibold rounded-lg">
              🌍 {recipe.cuisine}
            </span>
          )}
          {recipe.diet && (
            <span className="px-3 py-1 bg-green-100 text-green-800 text-sm font-semibold rounded-lg">
              🥗 {recipe.diet}
            </span>
          )}
          {recipe.total_time && (
            <span className="px-3 py-1 bg-orange-100 text-orange-800 text-sm font-semibold rounded-lg">
              ⏱️ {recipe.total_time}m
            </span>
          )}
          {recipe.course && (
            <span className="px-3 py-1 bg-purple-100 text-purple-800 text-sm font-semibold rounded-lg">
              🍽️ {recipe.course}
            </span>
          )}
        </div>

        {/* Description */}
        {recipe.description && (
          <p className="text-gray-700 text-base leading-relaxed mb-4">
            {recipe.description}
          </p>
        )}

        {/* Expand Button */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="flex items-center gap-2 text-purple-600 hover:text-purple-700 font-semibold transition-colors"
        >
          {expanded ? (
            <>
              <ChevronUp className="w-5 h-5" />
              Hide Details
            </>
          ) : (
            <>
              <ChevronDown className="w-5 h-5" />
              View Full Recipe
            </>
          )}
        </button>
      </div>

      {/* Expanded Details */}
      {expanded && (
        <div className="border-t-2 border-gray-100 bg-gray-50 p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Ingredients */}
            <div>
              <h4 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                🛒 Ingredients
              </h4>
              <ul className="space-y-2">
                {recipe.ingredients.map((ing, i) => (
                  <li key={i} className="text-gray-700 flex items-start gap-2">
                    <span className="text-purple-600 font-bold">•</span>
                    <span>{ing}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Instructions */}
            <div>
              <h4 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                📝 Instructions
              </h4>
              {recipe.instructions ? (
                <div className="space-y-3 text-gray-700">
                  {typeof recipe.instructions === 'string' 
                    ? <p>{recipe.instructions}</p>
                    : Array.isArray(recipe.instructions)
                    ? recipe.instructions.map((step: any, i: number) => (
                        <div key={i} className="flex items-start gap-2">
                          <span className="font-bold text-purple-600">{i + 1}.</span>
                          <span>{typeof step === 'object' ? step.instructions : step}</span>
                        </div>
                      ))
                    : <p className="text-gray-500 italic">Instructions not available</p>
                  }
                </div>
              ) : (
                <p className="text-gray-500 italic">Instructions not available</p>
              )}
            </div>
          </div>

          {/* View Original Button */}
          {recipe.url && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <a
                href={recipe.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold rounded-xl hover:from-purple-700 hover:to-blue-700 transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                🔗 View Original Recipe
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
