'use client'

import { Filter, X } from 'lucide-react'

interface FiltersType {
  cuisine: string
  diet: string
  course: string
}

interface FilterSidebarProps {
  filters: FiltersType
  onChange: (filters: FiltersType) => void
}

export default function FilterSidebar({ filters, onChange }: FilterSidebarProps) {
  const cuisines = ['All', 'Indian', 'Continental', 'Mexican', 'Italian', 'Chinese', 'Thai']
  const diets = ['All', 'Vegetarian', 'Non Vegeterian', 'High Protein Vegetarian', 'Diabetic Friendly', 'Vegan', 'Gluten Free']
  const courses = ['All', 'Lunch', 'Dinner', 'Snack', 'Breakfast', 'Dessert']

  const hasActiveFilters = filters.cuisine || filters.diet || filters.course

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700 shadow-xl p-6 sticky top-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-blue-400" />
          <h2 className="text-lg font-bold text-white">Filters</h2>
        </div>
        {hasActiveFilters && (
          <button
            onClick={() => onChange({ cuisine: '', diet: '', course: '' })}
            className="text-gray-400 hover:text-white transition-colors"
            title="Clear all filters"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Cuisine Filter */}
      <div className="mb-5">
        <label className="block text-sm font-semibold text-gray-300 mb-2 uppercase tracking-wide">
          Cuisine
        </label>
        <select
          value={filters.cuisine}
          onChange={(e) => onChange({ ...filters, cuisine: e.target.value })}
          className="w-full px-3 py-2.5 border border-slate-600 rounded-md focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 bg-slate-900 text-white font-medium text-sm transition-colors"
        >
          {cuisines.map(c => (
            <option key={c} value={c === 'All' ? '' : c}>{c}</option>
          ))}
        </select>
      </div>

      {/* Diet Filter */}
      <div className="mb-5">
        <label className="block text-sm font-semibold text-gray-300 mb-2 uppercase tracking-wide">
          Diet Type
        </label>
        <select
          value={filters.diet}
          onChange={(e) => onChange({ ...filters, diet: e.target.value })}
          className="w-full px-3 py-2.5 border border-slate-600 rounded-md focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 bg-slate-900 text-white font-medium text-sm transition-colors"
        >
          {diets.map(d => (
            <option key={d} value={d === 'All' ? '' : d}>{d}</option>
          ))}
        </select>
      </div>

      {/* Course Filter */}
      <div className="mb-6">
        <label className="block text-sm font-semibold text-gray-300 mb-2 uppercase tracking-wide">
          Course
        </label>
        <select
          value={filters.course}
          onChange={(e) => onChange({ ...filters, course: e.target.value })}
          className="w-full px-3 py-2.5 border border-slate-600 rounded-md focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 bg-slate-900 text-white font-medium text-sm transition-colors"
        >
          {courses.map(c => (
            <option key={c} value={c === 'All' ? '' : c}>{c}</option>
          ))}
        </select>
      </div>

      {/* Active Filters Count */}
      {hasActiveFilters && (
        <div className="p-3 bg-blue-600/20 border border-blue-600/30 rounded-md mb-4">
          <p className="text-sm text-blue-300 font-medium">
            {Object.values(filters).filter(Boolean).length} filter(s) active
          </p>
        </div>
      )}

      {/* Stats */}
      <div className="mt-6 pt-6 border-t border-slate-700">
        <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">
          Platform Stats
        </p>
        <div className="space-y-2 text-sm text-gray-300">
          <div className="flex justify-between">
            <span>Version</span>
            <span className="font-semibold text-white">1.0.0</span>
          </div>
          <div className="flex justify-between">
            <span>Recipes</span>
            <span className="font-semibold text-white">9,600+</span>
          </div>
          <div className="flex justify-between">
            <span>Search Type</span>
            <span className="font-semibold text-white">AI-Powered</span>
          </div>
        </div>
      </div>
    </div>
  )
}
