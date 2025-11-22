'use client'

import { Clock, ExternalLink, X } from 'lucide-react'
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
  instructions?: string[] | any[]
}

// Helper function to parse instructions properly
function parseInstructions(instructions: any): string[] {
  if (!instructions) return []
  
  // If it's already an array of strings
  if (Array.isArray(instructions) && typeof instructions[0] === 'string') {
    return instructions
  }
  
  // If it's an array of objects with 'instructions' field
  if (Array.isArray(instructions) && typeof instructions[0] === 'object') {
    const parsed: string[] = []
    instructions.forEach(item => {
      if (item.instructions) {
        // Split by sentences properly
        const steps = item.instructions
          .split(/\.\s+(?=[A-Z])/)
          .map((s: string) => s.trim())
          .filter((s: string) => s.length > 15)
        parsed.push(...steps)
      }
    })
    return parsed
  }
  
  // If it's a single string
  if (typeof instructions === 'string') {
    return instructions
      .split(/\.\s+(?=[A-Z])/)
      .map(s => s.trim())
      .filter(s => s.length > 15)
  }
  
  return []
}

export default function RecipeCard({ recipe }: { recipe: Recipe }) {
  const [isOpen, setIsOpen] = useState(false)
  
  const parsedInstructions = parseInstructions(recipe.instructions)

  return (
    <>
      {/* Grid Card - Click to Open */}
      <button
        onClick={() => setIsOpen(true)}
        className="group bg-slate-800 rounded-xl border border-slate-700 p-6 hover:border-blue-500 hover:shadow-2xl hover:shadow-blue-500/10 transition-all duration-300 text-left w-full flex flex-col min-h-[180px]"
      >
        <div className="flex-1 flex flex-col">
          <h3 className="text-lg font-bold text-white leading-tight mb-4 group-hover:text-blue-400 transition-colors line-clamp-3">
            {recipe.name}
          </h3>
          
          <div className="mt-auto space-y-3">
            <div className="flex flex-wrap gap-2">
              {recipe.cuisine && (
                <span className="px-2.5 py-1 bg-blue-600 text-white text-xs font-semibold rounded-md">
                  {recipe.cuisine}
                </span>
              )}
              {recipe.diet && (
                <span className="px-2.5 py-1 bg-green-600 text-white text-xs font-semibold rounded-md">
                  {recipe.diet}
                </span>
              )}
              {recipe.course && (
                <span className="px-2.5 py-1 bg-purple-600 text-white text-xs font-semibold rounded-md">
                  {recipe.course}
                </span>
              )}
            </div>
            
            {recipe.total_time && (
              <div className="flex items-center gap-2 text-gray-400 text-sm">
                <Clock className="w-4 h-4" />
                <span>{recipe.total_time} mins</span>
              </div>
            )}
          </div>
        </div>
      </button>

      {/* Modal */}
      {isOpen && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-slate-900 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-slate-700 shadow-2xl">
            {/* Modal Header */}
            <div className="sticky top-0 bg-slate-900 border-b border-slate-700 p-6 flex items-start justify-between gap-4 z-10">
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-white mb-3 leading-tight">
                  {recipe.name}
                </h2>
                <div className="flex flex-wrap gap-2">
                  {recipe.cuisine && (
                    <span className="px-3 py-1 bg-blue-600 text-white text-sm font-semibold rounded-md">
                      {recipe.cuisine}
                    </span>
                  )}
                  {recipe.diet && (
                    <span className="px-3 py-1 bg-green-600 text-white text-sm font-semibold rounded-md">
                      {recipe.diet}
                    </span>
                  )}
                  {recipe.course && (
                    <span className="px-3 py-1 bg-purple-600 text-white text-sm font-semibold rounded-md">
                      {recipe.course}
                    </span>
                  )}
                  {recipe.total_time && (
                    <span className="px-3 py-1 bg-slate-700 text-white text-sm font-semibold rounded-md flex items-center gap-1.5">
                      <Clock className="w-4 h-4" />
                      {recipe.total_time} mins
                    </span>
                  )}
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="flex-shrink-0 p-2 hover:bg-slate-800 rounded-lg transition-colors"
              >
                <X className="w-6 h-6 text-gray-400 hover:text-white" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6 space-y-8">
              {/* Description */}
              {recipe.description && (
                <div>
                  <p className="text-gray-300 leading-relaxed">
                    {recipe.description}
                  </p>
                </div>
              )}

              {/* Ingredients */}
              <div>
                <h3 className="text-xl font-bold text-white mb-4 uppercase tracking-wide">
                  Ingredients
                </h3>
                <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
                  <ul className="space-y-3">
                    {recipe.ingredients.map((ing, i) => (
                      <li key={i} className="text-gray-300 flex items-start gap-3 leading-relaxed">
                        <span className="text-blue-400 font-bold mt-1 flex-shrink-0">•</span>
                        <span>{ing}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Instructions */}
              {parsedInstructions.length > 0 && (
                <div>
                  <h3 className="text-xl font-bold text-white mb-4 uppercase tracking-wide">
                    Instructions
                  </h3>
                  <div className="space-y-4">
                    {parsedInstructions.map((step, i) => (
                      <div key={i} className="flex items-start gap-4 bg-slate-800 rounded-xl p-5 border border-slate-700">
                        <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-blue-600 text-white font-bold rounded-lg">
                          {i + 1}
                        </div>
                        <p className="flex-1 text-gray-300 leading-relaxed pt-1">
                          {step.endsWith('.') ? step : `${step}.`}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* View Original */}
              {recipe.url && (
                <div className="pt-4 border-t border-slate-700">
                  <a
                    href={recipe.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <ExternalLink className="w-4 h-4" />
                    View Original Recipe
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  )
}
