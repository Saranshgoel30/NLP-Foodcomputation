'use client'

import { useState } from 'react'
import { RefreshCw, Edit3, Tag } from 'lucide-react'
import ChipInput from './ChipInput'

interface StructuredQuery {
  base_query: string
  include_ingredients: string[]
  exclude_ingredients: string[]
  tags: string[]
  original_query: string
}

interface QueryEditorProps {
  structured: StructuredQuery
  onUpdate: (updated: StructuredQuery) => void
  onReset: () => void
  loading?: boolean
}

export default function QueryEditor({
  structured,
  onUpdate,
  onReset,
  loading = false
}: QueryEditorProps) {
  const [isExpanded, setIsExpanded] = useState(true)

  const handleBaseQueryChange = (value: string) => {
    onUpdate({ ...structured, base_query: value })
  }

  const handleIncludeIngredientsChange = (values: string[]) => {
    onUpdate({ ...structured, include_ingredients: values })
  }

  const handleExcludeIngredientsChange = (values: string[]) => {
    onUpdate({ ...structured, exclude_ingredients: values })
  }

  const handleTagsChange = (values: string[]) => {
    onUpdate({ ...structured, tags: values })
  }

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700 shadow-xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-5 border-b border-slate-700">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-600 rounded-md">
            <Edit3 className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Query Components</h3>
            <p className="text-sm text-gray-400">
              Edit any component to refine your search
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          {/* Toggle collapse/expand */}
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="px-3 py-2 bg-slate-700 hover:bg-slate-600 text-gray-300 rounded-md text-sm font-medium transition-colors duration-200"
          >
            {isExpanded ? 'Collapse' : 'Expand'}
          </button>

          {/* Reset button */}
          <button
            onClick={onReset}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-orange-600 hover:bg-orange-700 disabled:bg-orange-800 disabled:cursor-not-allowed text-white rounded-md text-sm font-bold transition-colors duration-200"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Reset to Original</span>
          </button>
        </div>
      </div>

      {/* Content */}
      {isExpanded && (
        <div className="p-6 space-y-6">
          {/* Original Query (read-only) */}
          <div className="p-4 bg-slate-900 rounded-lg border border-slate-700">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-bold text-gray-400 uppercase tracking-wide">
                Original Query
              </span>
            </div>
            <p className="text-white text-sm font-medium">
              "{structured.original_query}"
            </p>
          </div>

          {/* Base Query */}
          <div>
            <label className="block text-sm font-semibold text-gray-300 mb-2">
              Dish Name
              <span className="ml-2 text-xs font-normal text-gray-500">
                (Core dish without modifiers)
              </span>
            </label>
            <input
              type="text"
              value={structured.base_query}
              onChange={(e) => handleBaseQueryChange(e.target.value)}
              placeholder="e.g., dal, paneer tikka, pasta"
              disabled={loading}
              className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            />
            {structured.base_query === '' && (
              <p className="mt-2 text-xs text-yellow-400">
                ⚠️ Empty dish name will search all recipes with filters applied
              </p>
            )}
          </div>

          {/* Include Ingredients */}
          <div>
            <label className="block text-sm font-semibold text-gray-300 mb-2">
              Include Ingredients
              <span className="ml-2 text-xs font-normal text-gray-500">
                (Must have these - press Enter to add)
              </span>
            </label>
            <ChipInput
              values={structured.include_ingredients}
              onChange={handleIncludeIngredientsChange}
              placeholder="Type ingredient and press Enter..."
              disabled={loading}
              variant="success"
            />
            {structured.include_ingredients.length === 0 && (
              <p className="mt-2 text-xs text-gray-400">
                No specific ingredients required
              </p>
            )}
          </div>

          {/* Exclude Ingredients */}
          <div>
            <label className="block text-sm font-semibold text-gray-300 mb-2">
              Exclude Ingredients
              <span className="ml-2 text-xs font-normal text-gray-500">
                (Must NOT have these - {structured.exclude_ingredients.length} variants)
              </span>
            </label>
            <ChipInput
              values={structured.exclude_ingredients}
              onChange={handleExcludeIngredientsChange}
              placeholder="Type ingredient to exclude and press Enter..."
              disabled={loading}
              variant="danger"
            />
            {structured.exclude_ingredients.length > 10 && (
              <p className="mt-2 text-xs text-blue-400">
                ℹ️ Showing {structured.exclude_ingredients.length} ingredient variants (including regional names)
              </p>
            )}
          </div>

          {/* Tags */}
          <div>
            <label className="block text-sm font-semibold text-gray-300 mb-2 flex items-center gap-2">
              <Tag className="w-4 h-4" />
              <span>Tags</span>
              <span className="text-xs font-normal text-gray-500">
                (Descriptive modifiers - editable)
              </span>
            </label>
            <ChipInput
              values={structured.tags}
              onChange={handleTagsChange}
              placeholder="Type tag and press Enter..."
              disabled={loading}
              variant="default"
            />
            {structured.tags.length === 0 && (
              <p className="mt-2 text-xs text-gray-400">
                No tags specified
              </p>
            )}
          </div>

          {/* Tip */}
          <div className="p-4 bg-blue-600/10 border border-blue-600/30 rounded-lg">
            <p className="text-sm text-blue-300 flex items-start gap-2">
              <span className="text-lg">💡</span>
              <span>
                <strong>Tip:</strong> Edit any component and the search will automatically update. 
                Use "Reset to Original" to revert to the AI's initial understanding.
              </span>
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
