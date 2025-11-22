'use client'

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

  return (
    <div className="bg-white rounded-2xl border-2 border-gray-200 shadow-lg p-6 sticky top-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
        🎯 Filters
      </h2>

      {/* Cuisine Filter */}
      <div className="mb-6">
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Cuisine
        </label>
        <select
          value={filters.cuisine}
          onChange={(e) => onChange({ ...filters, cuisine: e.target.value })}
          className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-100 bg-white text-gray-900 font-medium"
        >
          {cuisines.map(c => (
            <option key={c} value={c === 'All' ? '' : c}>{c}</option>
          ))}
        </select>
      </div>

      {/* Diet Filter */}
      <div className="mb-6">
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Diet Type
        </label>
        <select
          value={filters.diet}
          onChange={(e) => onChange({ ...filters, diet: e.target.value })}
          className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-100 bg-white text-gray-900 font-medium"
        >
          {diets.map(d => (
            <option key={d} value={d === 'All' ? '' : d}>{d}</option>
          ))}
        </select>
      </div>

      {/* Course Filter */}
      <div className="mb-6">
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Course
        </label>
        <select
          value={filters.course}
          onChange={(e) => onChange({ ...filters, course: e.target.value })}
          className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-100 bg-white text-gray-900 font-medium"
        >
          {courses.map(c => (
            <option key={c} value={c === 'All' ? '' : c}>{c}</option>
          ))}
        </select>
      </div>

      {/* Clear Filters Button */}
      <button
        onClick={() => onChange({ cuisine: '', diet: '', course: '' })}
        className="w-full px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold rounded-lg transition-colors duration-200"
      >
        Clear All Filters
      </button>

      {/* Stats */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-3">
          Platform Stats
        </p>
        <div className="space-y-2 text-sm text-gray-600">
          <p>✓ Version 1.0.0</p>
          <p>✓ 9,600+ Recipes</p>
          <p>✓ Semantic Search</p>
        </div>
      </div>
    </div>
  )
}
