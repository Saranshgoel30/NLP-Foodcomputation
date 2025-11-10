'use client'

import React, { useState, useEffect } from 'react'
import { Search, SlidersHorizontal, X, ArrowLeft, TrendingUp, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { RecipeGrid } from '@/components/ModernRecipeCard'
import RecipeDetailModal from '@/components/RecipeDetailModal'
import LoadingState, { RecipeGridSkeleton } from '@/components/LoadingState'
import LanguageSelector from '@/components/LanguageSelector'

// Mock data for demonstration
const mockRecipes = [
  {
    id: '1',
    title: 'Paneer Tikka Masala',
    image: 'https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=500',
    cookTime: 45,
    servings: 4,
    difficulty: 'medium' as const,
    rating: 4.8,
    cuisine: 'North Indian',
    diet: ['Vegetarian'],
    calories: 420,
    isPopular: true,
    description: 'Creamy and flavorful paneer curry with aromatic spices',
    ingredients: [
      '250g paneer cubes',
      '2 onions, finely chopped',
      '3 tomatoes, pureed',
      '1 cup heavy cream',
      '2 tbsp butter',
      '2 tsp garam masala',
      'Salt to taste'
    ],
    instructions: [
      'Marinate paneer cubes with yogurt and spices for 30 minutes',
      'Grill paneer until lightly charred',
      'Prepare the masala gravy with onions, tomatoes, and spices',
      'Add cream and grilled paneer to the gravy',
      'Simmer for 10 minutes and serve hot'
    ]
  },
  {
    id: '2',
    title: 'Vegetable Biryani',
    image: 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500',
    cookTime: 60,
    servings: 6,
    difficulty: 'medium' as const,
    rating: 4.6,
    cuisine: 'Hyderabadi',
    diet: ['Vegetarian', 'Vegan'],
    calories: 380,
    isTrending: true,
  },
  {
    id: '3',
    title: 'Dal Tadka',
    image: 'https://images.unsplash.com/photo-1546833998-877b37c2e5c6?w=500',
    cookTime: 30,
    servings: 4,
    difficulty: 'easy' as const,
    rating: 4.7,
    cuisine: 'Indian',
    diet: ['Vegetarian', 'Vegan'],
    calories: 220,
  },
  {
    id: '4',
    title: 'Chicken Butter Masala',
    image: 'https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?w=500',
    cookTime: 50,
    servings: 4,
    difficulty: 'medium' as const,
    rating: 4.9,
    cuisine: 'Punjabi',
    diet: [],
    calories: 520,
    isPopular: true,
  },
  {
    id: '5',
    title: 'Masala Dosa',
    image: 'https://images.unsplash.com/photo-1630383249896-424e482df921?w=500',
    cookTime: 40,
    servings: 4,
    difficulty: 'hard' as const,
    rating: 4.8,
    cuisine: 'South Indian',
    diet: ['Vegetarian'],
    calories: 280,
    isTrending: true,
  },
  {
    id: '6',
    title: 'Palak Paneer',
    image: 'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=500',
    cookTime: 35,
    servings: 4,
    difficulty: 'easy' as const,
    rating: 4.5,
    cuisine: 'North Indian',
    diet: ['Vegetarian'],
    calories: 320,
  },
]

export default function SearchResultsPage() {
  const [query, setQuery] = useState('paneer recipes')
  const [isLoading, setIsLoading] = useState(false)
  const [recipes, setRecipes] = useState(mockRecipes)
  const [selectedRecipe, setSelectedRecipe] = useState<any>(null)
  const [showFilters, setShowFilters] = useState(false)
  const [language, setLanguage] = useState('en')
  const [filters, setFilters] = useState({
    cuisine: [] as string[],
    diet: [] as string[],
    difficulty: [] as string[],
    maxTime: null as number | null,
  })

  const handleSearch = (searchQuery: string) => {
    setIsLoading(true)
    setQuery(searchQuery)
    
    // Simulate API call
    setTimeout(() => {
      setRecipes(mockRecipes)
      setIsLoading(false)
    }, 1500)
  }

  const cuisineOptions = ['Indian', 'North Indian', 'South Indian', 'Punjabi', 'Hyderabadi']
  const dietOptions = ['Vegetarian', 'Vegan', 'Jain', 'Gluten-Free']
  const difficultyOptions = ['easy', 'medium', 'hard']

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-red-50 to-pink-50">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-sm border-b border-gray-200 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            {/* Back Button (mobile) */}
            <button className="lg:hidden p-2 rounded-lg hover:bg-gray-100">
              <ArrowLeft className="w-5 h-5 text-gray-700" />
            </button>

            {/* Search Bar */}
            <div className="flex-1 relative">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch(query)}
                  placeholder="Search recipes..."
                  className="w-full pl-12 pr-4 py-3 rounded-xl border-2 border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-200 outline-none transition-all"
                />
              </div>
            </div>

            {/* Filters Button */}
            <Button
              onClick={() => setShowFilters(!showFilters)}
              variant="outline"
              className="hidden md:flex"
            >
              <SlidersHorizontal className="w-5 h-5 mr-2" />
              Filters
            </Button>

            {/* Language Selector */}
            <LanguageSelector value={language} onChange={setLanguage} />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="flex gap-8">
          {/* Filters Sidebar */}
          <aside className={`
            ${showFilters ? 'block' : 'hidden'}
            md:block w-full md:w-80 flex-shrink-0
          `}>
            <div className="sticky top-24 bg-white rounded-2xl shadow-lg p-6 space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold text-gray-900">Filters</h3>
                <button
                  onClick={() => setFilters({ cuisine: [], diet: [], difficulty: [], maxTime: null })}
                  className="text-sm text-orange-600 hover:text-orange-700 font-medium"
                >
                  Clear All
                </button>
              </div>

              {/* Cuisine Filter */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Cuisine</h4>
                <div className="space-y-2">
                  {cuisineOptions.map((cuisine) => (
                    <label key={cuisine} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={filters.cuisine.includes(cuisine)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setFilters({ ...filters, cuisine: [...filters.cuisine, cuisine] })
                          } else {
                            setFilters({ ...filters, cuisine: filters.cuisine.filter(c => c !== cuisine) })
                          }
                        }}
                        className="w-4 h-4 rounded border-gray-300 text-orange-500 focus:ring-orange-500"
                      />
                      <span className="text-gray-700">{cuisine}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Diet Filter */}
              <div className="pt-6 border-t border-gray-200">
                <h4 className="font-semibold text-gray-900 mb-3">Dietary Preferences</h4>
                <div className="space-y-2">
                  {dietOptions.map((diet) => (
                    <label key={diet} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={filters.diet.includes(diet)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setFilters({ ...filters, diet: [...filters.diet, diet] })
                          } else {
                            setFilters({ ...filters, diet: filters.diet.filter(d => d !== diet) })
                          }
                        }}
                        className="w-4 h-4 rounded border-gray-300 text-orange-500 focus:ring-orange-500"
                      />
                      <span className="text-gray-700">{diet}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Difficulty Filter */}
              <div className="pt-6 border-t border-gray-200">
                <h4 className="font-semibold text-gray-900 mb-3">Difficulty</h4>
                <div className="flex gap-2">
                  {difficultyOptions.map((diff) => (
                    <button
                      key={diff}
                      onClick={() => {
                        if (filters.difficulty.includes(diff)) {
                          setFilters({ ...filters, difficulty: filters.difficulty.filter(d => d !== diff) })
                        } else {
                          setFilters({ ...filters, difficulty: [...filters.difficulty, diff] })
                        }
                      }}
                      className={`
                        flex-1 px-4 py-2 rounded-lg font-medium text-sm transition-all capitalize
                        ${filters.difficulty.includes(diff)
                          ? 'bg-gradient-to-r from-orange-500 to-red-500 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }
                      `}
                    >
                      {diff}
                    </button>
                  ))}
                </div>
              </div>

              {/* Time Filter */}
              <div className="pt-6 border-t border-gray-200">
                <h4 className="font-semibold text-gray-900 mb-3">Max Cooking Time</h4>
                <input
                  type="range"
                  min="15"
                  max="120"
                  step="15"
                  value={filters.maxTime || 60}
                  onChange={(e) => setFilters({ ...filters, maxTime: parseInt(e.target.value) })}
                  className="w-full accent-orange-500"
                />
                <div className="flex justify-between text-sm text-gray-600 mt-2">
                  <span>15 min</span>
                  <span className="font-semibold text-orange-600">{filters.maxTime || 60} min</span>
                  <span>120 min</span>
                </div>
              </div>
            </div>
          </aside>

          {/* Results */}
          <main className="flex-1">
            {/* Results Header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-1">
                  {isLoading ? 'Searching...' : `${recipes.length} Recipes Found`}
                </h2>
                <p className="text-gray-600">for "{query}"</p>
              </div>

              {/* Sort Options */}
              <select className="px-4 py-2 rounded-lg border-2 border-gray-200 focus:border-orange-500 outline-none">
                <option>Most Relevant</option>
                <option>Highest Rated</option>
                <option>Quickest</option>
                <option>Newest</option>
              </select>
            </div>

            {/* Loading State */}
            {isLoading && <RecipeGridSkeleton count={8} />}

            {/* Results Grid */}
            {!isLoading && (
              <RecipeGrid
                recipes={recipes}
                onRecipeClick={(recipe) => setSelectedRecipe(recipe)}
              />
            )}
          </main>
        </div>
      </div>

      {/* Recipe Detail Modal */}
      {selectedRecipe && (
        <RecipeDetailModal
          isOpen={!!selectedRecipe}
          onClose={() => setSelectedRecipe(null)}
          recipe={selectedRecipe}
        />
      )}
    </div>
  )
}
